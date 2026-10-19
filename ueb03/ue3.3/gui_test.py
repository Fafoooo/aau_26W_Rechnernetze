# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Auftrag: echten Thunderbird-GUI-Test des POP3-Servers mit Screenshots und Verifikationslog ausführen; bestehenden Server unverändert lassen.
"""Optionaler Linux-GUI-Integrationstest; nur frisches Profil und lokale Testdaten.

Abhängigkeiten: Thunderbird, Xvfb, ffmpeg und optional marionette_driver.
Beispiel: python3 gui_test.py --thunderbird /pfad/zu/thunderbird
Das optionale Python-Paket bei Bedarf in einer separaten Umgebung installieren.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time

from pop3_server import POP3Handler, create_server


class RecordingHandler(POP3Handler):
    """Beobachtung im Test, ohne Änderungen an pop3_server.py; PASS bleibt geheim."""

    def dispatch(self, name, argument, args):
        event = {"command": name, "argument": "<redacted>" if name == "PASS" else argument}
        result = super().dispatch(name, argument, args)
        self.server.gui_events.append(event)
        return result


def wait_for(check, description, timeout=40):
    """Bedingung statt blinder Startverzögerung prüfen, mit begrenzter Wartezeit."""
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            last = check()
            if last:
                return last
        except Exception as error:
            last = str(error)
        time.sleep(0.2)
    raise TimeoutError(f"{description}: {last}")


def port_ready(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


def stop_process(process):
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thunderbird", default=shutil.which("thunderbird"))
    parser.add_argument("--display", default=":183")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "screenshots")
    args = parser.parse_args()
    try:
        from marionette_driver.marionette import Marionette
    except ImportError:
        parser.error("Optionales Paket fehlt: marionette_driver (z.B. in separater venv installieren).")
    if not args.thunderbird or not Path(args.thunderbird).is_file():
        parser.error("Thunderbird fehlt; --thunderbird /pfad/zu/thunderbird angeben.")
    for command in ("Xvfb", "ffmpeg"):
        if not shutil.which(command):
            parser.error(f"Benötigtes Programm fehlt: {command}")
    if not args.display.startswith(":") or not args.display[1:].isdigit():
        parser.error("--display muss ein lokales Display wie :183 sein.")
    display_number = args.display[1:]
    if Path(f"/tmp/.X11-unix/X{display_number}").exists() or Path(f"/tmp/.X{display_number}-lock").exists():
        parser.error("Display belegt; kein fremdes X-Display verwenden oder beenden.")
    args.output.mkdir(parents=True, exist_ok=True)
    protected = [Path(__file__).with_name("pop3_server.py"), Path(__file__).parents[1] / "Angabe" / "SampleDataBase.py"]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "RUNNING", "source_sha256_before": hashes}
    server = create_server(host="127.0.0.1", port=0)
    server.gui_events = []
    server.RequestHandlerClass = RecordingHandler
    worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1})
    worker.start()
    xvfb = thunderbird = marionette = None
    try:
        originals = [BytesParser(policy=policy.default).parsebytes(record["raw"].encode()) for record in server.database.get_messages("alice")]
        subjects = [str(message["Subject"]) for message in originals]
        expected_body = originals[0].get_content().strip().replace("\r\n", "\n")
        report.update(expected_subjects=subjects, pop3_address=list(server.server_address))
        report["thunderbird_version"] = subprocess.check_output([args.thunderbird, "--version"], text=True).strip()
        with tempfile.TemporaryDirectory(prefix="rn03-thunderbird-") as temporary, ExitStack() as processes:
            profile = Path(temporary) / "profile"
            profile.mkdir()
            with socket.socket() as reservation:
                reservation.bind(("127.0.0.1", 0))
                marionette_port = reservation.getsockname()[1]
            preferences = {
                "marionette.port": marionette_port,
                "mail.accountmanager.accounts": "account1,account2",
                "mail.accountmanager.defaultaccount": "account1",
                "mail.accountmanager.localfoldersserver": "server2",
                "mail.account.account1.server": "server1",
                "mail.account.account1.identities": "id1",
                "mail.account.account2.server": "server2",
                "mail.identity.id1.fullName": "Alice (local POP3 lab)",
                "mail.identity.id1.useremail": "alice@example.com",
                "mail.server.server1.type": "pop3",
                "mail.server.server1.name": "POP3 Lab - alice@127.0.0.1",
                "mail.server.server1.hostname": "127.0.0.1",
                "mail.server.server1.userName": "alice",
                "mail.server.server1.port": server.server_address[1],
                "mail.server.server1.socketType": 0,
                "mail.server.server1.authMethod": 3,
                "mail.server.server1.leave_on_server": True,
                "mail.server.server1.check_new_mail": False,
                "mail.server.server1.login_at_startup": False,
                "mail.server.server1.download_on_biff": True,
                "mail.server.server2.type": "none",
                "mail.server.server2.hostname": "Local Folders",
                "mail.server.server2.userName": "nobody",
                "mail.server.server2.name": "Local Folders",
                "mail.biff.show_alert": False,
                "mail.biff.play_sound": False,
                "mail.shell.checkDefaultClient": False,
                "mailnews.start_page.enabled": False,
                "mailnews.message_display.disable_remote_image": True,
                "mailnews.database.global.indexer.enabled": False,
                "mailnews.default_view_flags": 0,
                "mailnews.start_page_override.mstone": "ignore",
                "mail.provider.enabled": False,
                "app.update.auto": False,
                "app.update.enabled": False,
                "datareporting.policy.dataSubmissionEnabled": False,
                "toolkit.telemetry.reportingpolicy.firstRun": False,
                "toolkit.telemetry.enabled": False,
                "network.captive-portal-service.enabled": False,
                "network.connectivity-service.enabled": False,
                "browser.newtabpage.enabled": False,
            }
            (profile / "user.js").write_text("\n".join(f"user_pref({json.dumps(key)}, {json.dumps(value)});" for key, value in preferences.items()), encoding="utf-8")
            environment = dict(os.environ, DISPLAY=args.display, MOZ_NO_REMOTE="1")
            with (args.output / "thunderbird.log").open("w", encoding="utf-8") as application_log:
                xvfb = subprocess.Popen(["Xvfb", args.display, "-screen", "0", "1440x1000x24", "-nolisten", "tcp"], stdout=application_log, stderr=subprocess.STDOUT)
                processes.callback(stop_process, xvfb)
                report["xvfb_pid"] = xvfb.pid
                wait_for(lambda: Path(f"/tmp/.X11-unix/X{display_number}").exists() and xvfb.poll() is None, "Xvfb bereit")
                thunderbird = subprocess.Popen([args.thunderbird, "--no-remote", "--new-instance", "--marionette", "--remote-allow-system-access", "--profile", str(profile)], env=environment, stdout=application_log, stderr=subprocess.STDOUT)
                processes.callback(stop_process, thunderbird)
                report["thunderbird_pid"] = thunderbird.pid
                wait_for(lambda: port_ready(marionette_port), "Marionette bereit", 60)
                marionette = Marionette(host="127.0.0.1", port=marionette_port, socket_timeout=30)
                marionette.start_session()
                marionette.set_context("chrome")

                def chrome(script, *values):
                    prefix = 'const win = Services.wm.getMostRecentWindow("mail:3pane"); const tabmail = win?.document.getElementById("tabmail"); const pane = tabmail?.currentAbout3Pane; '
                    return marionette.execute_script(prefix + script, script_args=list(values))

                wait_for(lambda: chrome("return !!pane?.folderPane && !!pane?.threadTree;"), "Thunderbird-Hauptfenster bereit")
                chrome("win.resizeTo(1440, 1000); win.moveTo(0, 0);")
                chrome('''
                    const { MailServices } = ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs");
                    const login = Cc["@mozilla.org/login-manager/loginInfo;1"].createInstance(Ci.nsILoginInfo);
                    login.init("mailbox://127.0.0.1", null, "mailbox://127.0.0.1", "alice", "secret", "", "");
                    win.guiLoginReady = false;
                    Services.logins.addLoginAsync(login).then(() => { win.guiLoginReady = true; });
                    return MailServices.accounts.getIncomingServer("server1").rootFolder.URI;
                ''')
                wait_for(lambda: chrome('return win.guiLoginReady;'), "synthetisches Passwort gespeichert")
                chrome('''
                    const { MailServices } = ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs");
                    const incoming = MailServices.accounts.getIncomingServer("server1");
                    incoming.performBiff(win.msgWindow);
                ''')
                folder_info = '''
                    const { MailServices } = ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs");
                    const inbox = MailServices.accounts.getIncomingServer("server1").rootFolder.getFolderWithFlags(Ci.nsMsgFolderFlags.Inbox);
                '''
                observed = wait_for(lambda: chrome(folder_info + 'return inbox && inbox.getTotalMessages(false) == 4 ? Array.from(inbox.messages, h => h.mime2DecodedSubject) : null;'), "vier Originalmails empfangen", 60)
                if sorted(observed) != sorted(subjects):
                    raise AssertionError(f"Falsche Betreffzeilen: {observed}")
                report["received_subjects"] = observed
                chrome(folder_info + 'pane.restoreState({folderURI: inbox.URI, folderPaneVisible: true, messagePaneVisible: true});')
                wait_for(lambda: chrome('return pane.gDBView?.rowCount == 4;'), "vier sichtbare Inbox-Zeilen")
                report["visible_subjects"] = chrome('return Array.from({length: pane.gDBView.rowCount}, (_, i) => pane.gDBView.getMsgHdrAt(i).mime2DecodedSubject);')
                if sorted(report["visible_subjects"]) != sorted(subjects):
                    raise AssertionError("Sichtbare Inbox stimmt nicht mit Originaldaten überein.")

                def screenshot(filename):
                    target = args.output / filename
                    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "x11grab", "-video_size", "1440x1000", "-i", args.display, "-frames:v", "1", "-update", "1", str(target)], env=environment, check=True, timeout=20)
                    report.setdefault("screenshots", {})[filename] = hashlib.sha256(target.read_bytes()).hexdigest()

                wait_for(lambda: any(e["command"] == "QUIT" for e in server.gui_events), "POP3-Sitzung mit QUIT abgeschlossen")
                screenshot("inbox.png")
                chrome(folder_info + 'pane.selectMessage(Array.from(inbox.messages).find(h => h.mime2DecodedSubject == arguments[0]));', subjects[0])
                body = wait_for(lambda: chrome('const text = pane.messageBrowser?.contentWindow?.getMessagePaneBrowser()?.contentDocument?.body?.innerText; return text?.includes("Welcome to the POP3 laboratory.") ? text : null;'), "Original-Mailtext sichtbar")
                normalized_body = body.strip().replace("\r\n", "\n")
                if normalized_body != expected_body:
                    raise AssertionError(f"Mailtext weicht ab: {body!r}")
                report["opened_message"] = {"subject": subjects[0], "body": normalized_body, "body_matches_original": True}
                screenshot("mail_offen.png")
                chrome('win.setTimeout(() => Services.startup.quit(Ci.nsIAppStartup.eAttemptQuit), 500);')
                marionette.delete_session()
                marionette = None
                report["thunderbird_exit_code"] = thunderbird.wait(timeout=20)
                if report["thunderbird_exit_code"] != 0:
                    raise AssertionError("Thunderbird wurde nicht regulär beendet.")
        report["profile_removed_after_run"] = not profile.exists()
        report["retr_commands"] = [e["argument"] for e in server.gui_events if e["command"] == "RETR"]
        if sorted(report["retr_commands"]) != ["1", "2", "3", "4"]:
            raise AssertionError("Nicht genau vier Originalnachrichten über RETR abgerufen.")
        if len(server.database.get_messages("alice")) != 4:
            raise AssertionError("leave_on_server hat die Originaldatenbank nicht erhalten.")
        report["status"] = "PASS"
    except BaseException as error:
        report.update(status="FAIL", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        if marionette is not None:
            try:
                marionette.delete_session()
            except Exception:
                pass
        stop_process(thunderbird)
        stop_process(xvfb)
        server.shutdown()
        server.server_close()
        worker.join(timeout=10)
        report["protocol_events"] = server.gui_events
        report["source_sha256_after"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        report["protected_sources_unchanged"] = report["source_sha256_after"] == hashes
        report["cleanup"] = {"thunderbird_stopped": thunderbird is None or thunderbird.poll() is not None, "xvfb_stopped": xvfb is None or xvfb.poll() is not None, "server_thread_stopped": not worker.is_alive(), "server_socket_closed": server.socket.fileno() == -1}
        if not report["protected_sources_unchanged"] or not all(report["cleanup"].values()):
            report["status"] = "FAIL"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        (args.output / "verifikation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
