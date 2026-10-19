# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Original-Testdaten mit Chromium und Firefox gegen beide HTTP-Server prüfen; Socket-Client mit echtem GoPop3Server testen und Nachweise speichern.
"""Optionale Integration: Playwright-Browser und ein lokal kompiliertes Go-Testprogramm.

Aufruf: python3 integration_test.py --go-server /pfad/zum/lokal-gebundenen-server
Die Serverprogramme selbst benötigen weiterhin nur die Python-Standardbibliothek.
"""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import zipfile

ROOT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack():
    destination = ROOT / 'Angabe' / 'document_root'
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(ROOT / 'Angabe' / 'document_root.zip') as archive:
        for info in archive.infolist():
            target = (destination / info.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError('Unsicherer ZIP-Pfad')
            archive.extract(info, destination)
    indexes = list(destination.rglob('index.html'))
    if len(indexes) != 1:
        raise ValueError('Genau eine Original-Startseite erwartet')
    return indexes[0].parent


def go_test(binary, report):
    """Fremdimplementierung starten und ausschließlich das synthetische Konto nutzen."""
    client_module = load('integration_pop3_client', ROOT / 'ue3.2' / 'pop3_client.py')
    process = subprocess.Popen([str(binary)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        deadline = time.monotonic() + 10
        while True:
            if process.poll() is not None:
                raise RuntimeError(process.stdout.read())
            try:
                client = client_module.POP3Client('127.0.0.1', 11119, timeout=3)
                break
            except OSError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.05)
        with client:
            client.login('alice', 'secret')
            listing = client.list_messages()
            assert len(listing) == 2, listing
            mail = client.retrieve(1)
            assert b'Subject: Hello Alice\r\n' in mail, mail
            assert len(mail) == listing[0][1]
        report['go_pop3'] = {'greeting': client.greeting.decode(), 'listing': listing,
                             'retrieved_octets': len(mail), 'mail': mail.decode(),
                             'closed_after_quit': client.closed,
                             'source': 'https://github.com/kurthorvath/GoPop3Server',
                             'revision': 'eae717dd98cb0a59e7afd3e857bc1c86660c530d',
                             'modification': 'Nur Bind-Adresse von :110 auf 127.0.0.1:11119 geändert; Go 1.27.2.'}
    finally:
        process.terminate()
        output, _ = process.communicate(timeout=10)
        report['go_server_log'] = output
        report['go_server_stopped'] = process.poll() is not None


def browser_tests(document_root, report):
    """Zwei echte Browser-Engines, bytegenaue Dateien und echte Render-Screenshots."""
    from playwright.sync_api import sync_playwright
    http09 = load('integration_http09', ROOT / 'ue3.4' / 'server.py')
    http10 = load('integration_http10', ROOT / 'ue3.5' / 'server.py')
    stop = threading.Event()
    ready09, ready10 = threading.Event(), threading.Event()
    addresses = {}
    def ready(name, event):
        def callback(address):
            addresses[name] = address
            event.set()
        return callback
    logs = io.StringIO()
    server = http10.HTTPServer(document_root, port=0, log_stream=logs)
    threads = [threading.Thread(target=http09.serve,
                               args=(document_root,),
                               kwargs={'port': 0, 'stop': stop, 'ready': ready('09', ready09)}),
               threading.Thread(target=server.serve, args=(ready('10', ready10),))]
    for thread in threads:
        thread.start()
    try:
        assert ready09.wait(10) and ready10.wait(10), 'Server nicht bereit'
        report['browsers'] = []
        screenshots = ROOT / 'browser_nachweise'
        screenshots.mkdir(exist_ok=True)
        with sync_playwright() as playwright:
            for name in ('chromium', 'firefox'):
                if name == 'chromium':
                    browser = playwright.chromium.launch(headless=True, channel='chromium')
                else:
                    browser = playwright.firefox.launch(headless=True)
                try:
                    page = browser.new_page(viewport={'width': 1280, 'height': 900})
                    result = {'browser': name, 'version': browser.version, 'http10_files': []}
                    base = f'http://127.0.0.1:{addresses["10"][1]}'
                    response = page.goto(base + '/', wait_until='networkidle')
                    assert response.status == 200
                    assert response.body() == (document_root / 'index.html').read_bytes()
                    assert page.locator('body').inner_text().strip()
                    # Browser-Rendering und Nachladen der Bilder getrennt von Rohbytechecks prüfen.
                    images = page.locator('img').evaluate_all('(imgs) => imgs.map(i => ({src:i.getAttribute("src"),ok:i.complete && i.naturalWidth>0}))')
                    assert all(image['ok'] for image in images), images
                    result['images'] = images
                    result['title'] = page.title()
                    result['body_text'] = page.locator('body').inner_text()
                    page.screenshot(path=str(screenshots / f'{name}_http10.png'), full_page=True)
                    for path in sorted(document_root.rglob('*')):
                        if path.is_file():
                            relative = path.relative_to(document_root).as_posix()
                            reply = page.request.get(base + '/' + relative)
                            expected = path.read_bytes()
                            assert reply.status == 200 and reply.body() == expected, relative
                            result['http10_files'].append({'path': relative, 'bytes': len(expected),
                                                          'sha256': hashlib.sha256(expected).hexdigest()})
                    try:
                        page.goto(f'http://127.0.0.1:{addresses["09"][1]}/', timeout=15000)
                    except Exception as error:
                        result['http09'] = {'displayed': False, 'error': str(error)}
                    else:
                        raise AssertionError('Moderner Browser zeigte strikt HTTP/0.9 unerwartet an')
                    page.screenshot(path=str(screenshots / f'{name}_http09_fehler.png'), full_page=True)
                    report['browsers'].append(result)
                finally:
                    browser.close()
    finally:
        stop.set()
        server.stop.set()
        for thread in threads:
            thread.join(10)
            assert not thread.is_alive(), 'Serverthread blieb aktiv'
        report['http_access_log'] = [json.loads(line) for line in logs.getvalue().splitlines()]
        report['http_servers_stopped'] = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--go-server', type=Path)
    args = parser.parse_args()
    report = {'python': sys.version, 'testdate': '2026-10-19', 'mode': 'Echte lokale Prozesse, keine externen Mailkonten'}
    if args.go_server:
        go_test(args.go_server.resolve(), report)
    browser_tests(unpack(), report)
    destination = ROOT / 'integration_ergebnis.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
