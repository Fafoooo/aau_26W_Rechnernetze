# KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Recherchierte WLAN-Hardwarepreise und das PoE-Budget für Ü 2.7 mit Python berechnen.
from decimal import Decimal

# Bruttopreise aus den verlinkten Geizhals-AT-Angeboten; keine Live-Abfrage.
positionen = [
    ('UCG-Ultra', 1, Decimal('114.00'), 'https://geizhals.at/ubiquiti-cloud-gateway-ultra-ucg-ultra-a3145685.html'),
    ('USW-Lite-8-PoE', 1, Decimal('124.00'), 'https://geizhals.at/ubiquiti-unifiswitch-lite-8-desktop-gigabit-managed-switch-usw-lite-8-poe-a2378317.html'),
    ('U6+', 2, Decimal('111.90'), 'https://geizhals.at/ubiquiti-unifi-6-u6-a2849254.html'),
]

warenwert = Decimal('0.00')
for modell, anzahl, einzelpreis, quelle in positionen:
    zeilensumme = anzahl * einzelpreis
    warenwert += zeilensumme
    print(f'{anzahl} x {modell}: {einzelpreis:.2f} EUR = {zeilensumme:.2f} EUR')

# Die ausgewählten Angebote nennen Gratisversand innerhalb Österreichs.
versand = Decimal('0.00')
gesamt = warenwert + versand
print(f'Warenwert inkl. MwSt.: {warenwert:.2f} EUR')
print(f'Versand laut ausgewählten Angeboten: {versand:.2f} EUR')
print(f'Geplante Anschaffung gesamt: {gesamt:.2f} EUR')
assert gesamt == Decimal('461.80')

ap_anzahl = 2
ap_max_watt = Decimal('9')
poe_budget_watt = Decimal('52')
ap_max_gesamt = ap_anzahl * ap_max_watt
poe_reserve = poe_budget_watt - ap_max_gesamt
assert ap_max_gesamt <= poe_budget_watt
print(f'AP-Leistungsbedarf maximal: {ap_max_gesamt} W')
print(f'Rechnerische PoE-Budgetreserve: {poe_reserve} W')
print('Planungsrechnung, keine Bestellung und keine Verbrauchsmessung.')
