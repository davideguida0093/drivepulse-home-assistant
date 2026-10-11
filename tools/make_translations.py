"""Generate custom_components/drivepulse/translations/*.json.

The three app labels quoted in the texts (Send to Home Assistant / Webhook
address / Test send) are read from the app's own ARB files, so the words in
Home Assistant are the ones the user sees in the app. Pass the app's l10n
folder as the first argument.
"""

from __future__ import annotations

import json
import pathlib
import sys

ARB = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).resolve().parent.parent / "custom_components/drivepulse/translations"

LANGS = ["en", "it", "de", "fr", "es", "pt", "cs", "hu", "pl", "ro"]

# Sentences. {menu}, {field}, {test} are the app labels; {webhook_url} is kept
# for Home Assistant to fill in.
T = {
    "en": {
        "user_title": "Add DrivePulse",
        "user_desc": "This creates a private address (a webhook) that the DrivePulse app sends your car's data to. No account, no cloud: the data stays in your Home Assistant. Select Submit, then paste the address into the app.",
        "created": "DrivePulse is ready. In the app open \u201c{menu}\u201d, paste this address in \u201c{field}\u201d and tap \u201c{test}\u201d:\n\n{webhook_url}\n\nAway from home, use the HTTPS address of your Home Assistant (for example Nabu Casa) or a VPN, and turn off \u201cLocal network only\u201d in the integration options.",
        "opt_desc": "Address to paste in the DrivePulse app (\u201c{menu}\u201d):\n\n{webhook_url}",
        "local_only": "Local network only",
        "local_only_desc": "Accept the app only from your home network (or a VPN). Turn off to receive from the internet through your HTTPS address.",
        "fuel_level": "Fuel level", "battery_level": "Battery level", "range": "Range",
        "odometer": "Odometer", "battery_voltage": "12 V battery", "coolant_temperature": "Coolant temperature",
        "trouble_codes": "Trouble codes", "fuel_volume": "Fuel", "speed": "Speed", "engine_speed": "Engine speed",
        "last_trip_distance": "Last trip", "trip_in_progress": "Trip in progress", "adapter_connected": "Adapter connected",
    },
    "it": {
        "user_title": "Aggiungi DrivePulse",
        "user_desc": "Crea un indirizzo privato (un webhook) a cui l'app DrivePulse manda i dati della tua auto. Nessun account, nessun cloud: i dati restano nel tuo Home Assistant. Premi Invia, poi incolla l'indirizzo nell'app.",
        "created": "DrivePulse \u00e8 pronto. Nell'app apri \u201c{menu}\u201d, incolla questo indirizzo in \u201c{field}\u201d e tocca \u201c{test}\u201d:\n\n{webhook_url}\n\nFuori casa usa l'indirizzo HTTPS del tuo Home Assistant (per esempio Nabu Casa) o una VPN, e disattiva \u201cSolo rete locale\u201d nelle opzioni dell'integrazione.",
        "opt_desc": "Indirizzo da incollare nell'app DrivePulse (\u201c{menu}\u201d):\n\n{webhook_url}",
        "local_only": "Solo rete locale",
        "local_only_desc": "Accetta l'app solo dalla rete di casa (o da una VPN). Disattiva per ricevere da internet tramite il tuo indirizzo HTTPS.",
        "fuel_level": "Livello carburante", "battery_level": "Livello batteria", "range": "Autonomia",
        "odometer": "Contachilometri", "battery_voltage": "Batteria 12 V", "coolant_temperature": "Temperatura refrigerante",
        "trouble_codes": "Codici errore", "fuel_volume": "Carburante", "speed": "Velocit\u00e0", "engine_speed": "Giri motore",
        "last_trip_distance": "Ultimo viaggio", "trip_in_progress": "Viaggio in corso", "adapter_connected": "Adattatore collegato",
    },
    "de": {
        "user_title": "DrivePulse hinzuf\u00fcgen",
        "user_desc": "Das erzeugt eine private Adresse (einen Webhook), an die die DrivePulse-App die Fahrzeugdaten sendet. Kein Konto, keine Cloud: Die Daten bleiben in Ihrem Home Assistant. W\u00e4hlen Sie \u201eAbsenden\u201c und f\u00fcgen Sie die Adresse dann in der App ein.",
        "created": "DrivePulse ist bereit. \u00d6ffnen Sie in der App \u201e{menu}\u201c, f\u00fcgen Sie diese Adresse bei \u201e{field}\u201c ein und tippen Sie auf \u201e{test}\u201c:\n\n{webhook_url}\n\nUnterwegs nutzen Sie die HTTPS-Adresse Ihres Home Assistant (z. B. Nabu Casa) oder ein VPN und schalten Sie in den Integrationsoptionen \u201eNur lokales Netzwerk\u201c aus.",
        "opt_desc": "Adresse f\u00fcr die DrivePulse-App (\u201e{menu}\u201c):\n\n{webhook_url}",
        "local_only": "Nur lokales Netzwerk",
        "local_only_desc": "Die App nur aus dem Heimnetz (oder per VPN) akzeptieren. Ausschalten, um \u00fcber Ihre HTTPS-Adresse aus dem Internet zu empfangen.",
        "fuel_level": "Tankf\u00fcllstand", "battery_level": "Batterieladung", "range": "Reichweite",
        "odometer": "Kilometerstand", "battery_voltage": "12-V-Batterie", "coolant_temperature": "K\u00fchlmitteltemperatur",
        "trouble_codes": "Fehlercodes", "fuel_volume": "Kraftstoff", "speed": "Geschwindigkeit", "engine_speed": "Motordrehzahl",
        "last_trip_distance": "Letzte Fahrt", "trip_in_progress": "Fahrt l\u00e4uft", "adapter_connected": "Adapter verbunden",
    },
    "fr": {
        "user_title": "Ajouter DrivePulse",
        "user_desc": "Cela cr\u00e9e une adresse priv\u00e9e (un webhook) \u00e0 laquelle l'application DrivePulse envoie les donn\u00e9es de votre voiture. Pas de compte, pas de cloud : les donn\u00e9es restent dans votre Home Assistant. S\u00e9lectionnez Valider, puis collez l'adresse dans l'application.",
        "created": "DrivePulse est pr\u00eat. Dans l'application, ouvrez \u00ab\u00a0{menu}\u00a0\u00bb, collez cette adresse dans \u00ab\u00a0{field}\u00a0\u00bb et touchez \u00ab\u00a0{test}\u00a0\u00bb :\n\n{webhook_url}\n\nHors de chez vous, utilisez l'adresse HTTPS de votre Home Assistant (par exemple Nabu Casa) ou un VPN, et d\u00e9sactivez \u00ab\u00a0R\u00e9seau local uniquement\u00a0\u00bb dans les options de l'int\u00e9gration.",
        "opt_desc": "Adresse \u00e0 coller dans l'application DrivePulse (\u00ab\u00a0{menu}\u00a0\u00bb) :\n\n{webhook_url}",
        "local_only": "R\u00e9seau local uniquement",
        "local_only_desc": "N'accepter l'application que depuis votre r\u00e9seau domestique (ou un VPN). D\u00e9sactivez pour recevoir depuis internet via votre adresse HTTPS.",
        "fuel_level": "Niveau de carburant", "battery_level": "Niveau de batterie", "range": "Autonomie",
        "odometer": "Compteur kilom\u00e9trique", "battery_voltage": "Batterie 12 V", "coolant_temperature": "Temp\u00e9rature du liquide de refroidissement",
        "trouble_codes": "Codes d'erreur", "fuel_volume": "Carburant", "speed": "Vitesse", "engine_speed": "R\u00e9gime moteur",
        "last_trip_distance": "Dernier trajet", "trip_in_progress": "Trajet en cours", "adapter_connected": "Adaptateur connect\u00e9",
    },
    "es": {
        "user_title": "A\u00f1adir DrivePulse",
        "user_desc": "Esto crea una direcci\u00f3n privada (un webhook) a la que la app DrivePulse env\u00eda los datos de tu coche. Sin cuenta, sin nube: los datos se quedan en tu Home Assistant. Pulsa Enviar y pega la direcci\u00f3n en la app.",
        "created": "DrivePulse est\u00e1 listo. En la app abre \u00ab{menu}\u00bb, pega esta direcci\u00f3n en \u00ab{field}\u00bb y toca \u00ab{test}\u00bb:\n\n{webhook_url}\n\nFuera de casa usa la direcci\u00f3n HTTPS de tu Home Assistant (por ejemplo Nabu Casa) o una VPN, y desactiva \u00abSolo red local\u00bb en las opciones de la integraci\u00f3n.",
        "opt_desc": "Direcci\u00f3n para pegar en la app DrivePulse (\u00ab{menu}\u00bb):\n\n{webhook_url}",
        "local_only": "Solo red local",
        "local_only_desc": "Aceptar la app solo desde tu red dom\u00e9stica (o una VPN). Desact\u00edvalo para recibir desde internet con tu direcci\u00f3n HTTPS.",
        "fuel_level": "Nivel de combustible", "battery_level": "Nivel de bater\u00eda", "range": "Autonom\u00eda",
        "odometer": "Od\u00f3metro", "battery_voltage": "Bater\u00eda de 12 V", "coolant_temperature": "Temperatura del refrigerante",
        "trouble_codes": "C\u00f3digos de error", "fuel_volume": "Combustible", "speed": "Velocidad", "engine_speed": "R\u00e9gimen del motor",
        "last_trip_distance": "\u00daltimo viaje", "trip_in_progress": "Viaje en curso", "adapter_connected": "Adaptador conectado",
    },
    "pt": {
        "user_title": "Adicionar DrivePulse",
        "user_desc": "Isto cria um endere\u00e7o privado (um webhook) para onde a app DrivePulse envia os dados do seu carro. Sem conta, sem nuvem: os dados ficam no seu Home Assistant. Selecione Submeter e cole o endere\u00e7o na app.",
        "created": "O DrivePulse est\u00e1 pronto. Na app abra \u201c{menu}\u201d, cole este endere\u00e7o em \u201c{field}\u201d e toque em \u201c{test}\u201d:\n\n{webhook_url}\n\nFora de casa, use o endere\u00e7o HTTPS do seu Home Assistant (por exemplo Nabu Casa) ou uma VPN e desative \u201cApenas rede local\u201d nas op\u00e7\u00f5es da integra\u00e7\u00e3o.",
        "opt_desc": "Endere\u00e7o a colar na app DrivePulse (\u201c{menu}\u201d):\n\n{webhook_url}",
        "local_only": "Apenas rede local",
        "local_only_desc": "Aceitar a app apenas a partir da sua rede dom\u00e9stica (ou de uma VPN). Desative para receber da internet atrav\u00e9s do seu endere\u00e7o HTTPS.",
        "fuel_level": "N\u00edvel de combust\u00edvel", "battery_level": "N\u00edvel da bateria", "range": "Autonomia",
        "odometer": "Od\u00f3metro", "battery_voltage": "Bateria de 12 V", "coolant_temperature": "Temperatura do l\u00edquido de arrefecimento",
        "trouble_codes": "C\u00f3digos de erro", "fuel_volume": "Combust\u00edvel", "speed": "Velocidade", "engine_speed": "Rota\u00e7\u00e3o do motor",
        "last_trip_distance": "\u00daltima viagem", "trip_in_progress": "Viagem em curso", "adapter_connected": "Adaptador ligado",
    },
    "cs": {
        "user_title": "P\u0159idat DrivePulse",
        "user_desc": "Vytvo\u0159\u00ed soukromou adresu (webhook), na kterou aplikace DrivePulse pos\u00edl\u00e1 data va\u0161eho auta. \u017d\u00e1dn\u00fd \u00fa\u010det, \u017e\u00e1dn\u00fd cloud: data z\u016fst\u00e1vaj\u00ed ve va\u0161em Home Assistantu. Vyberte Odeslat a vlo\u017ete adresu do aplikace.",
        "created": "DrivePulse je p\u0159ipraven. V aplikaci otev\u0159ete \u201e{menu}\u201c, vlo\u017ete tuto adresu do \u201e{field}\u201c a klepn\u011bte na \u201e{test}\u201c:\n\n{webhook_url}\n\nMimo domov pou\u017eijte HTTPS adresu sv\u00e9ho Home Assistantu (nap\u0159. Nabu Casa) nebo VPN a v mo\u017enostech integrace vypn\u011bte \u201eJen m\u00edstn\u00ed s\u00ed\u0165\u201c.",
        "opt_desc": "Adresa k vlo\u017een\u00ed do aplikace DrivePulse (\u201e{menu}\u201c):\n\n{webhook_url}",
        "local_only": "Jen m\u00edstn\u00ed s\u00ed\u0165",
        "local_only_desc": "P\u0159ij\u00edmat aplikaci jen z domovsk\u00e9 s\u00edt\u011b (nebo p\u0159es VPN). Vypn\u011bte pro p\u0159\u00edjem z internetu p\u0159es va\u0161i HTTPS adresu.",
        "fuel_level": "Hladina paliva", "battery_level": "Stav baterie", "range": "Dojezd",
        "odometer": "Po\u010d\u00edtadlo kilometr\u016f", "battery_voltage": "Baterie 12 V", "coolant_temperature": "Teplota chladic\u00ed kapaliny",
        "trouble_codes": "Chybov\u00e9 k\u00f3dy", "fuel_volume": "Palivo", "speed": "Rychlost", "engine_speed": "Ot\u00e1\u010dky motoru",
        "last_trip_distance": "Posledn\u00ed j\u00edzda", "trip_in_progress": "J\u00edzda prob\u00edh\u00e1", "adapter_connected": "Adapt\u00e9r p\u0159ipojen",
    },
    "hu": {
        "user_title": "DrivePulse hozz\u00e1ad\u00e1sa",
        "user_desc": "Ez l\u00e9trehoz egy priv\u00e1t c\u00edmet (webhookot), amelyre a DrivePulse alkalmaz\u00e1s k\u00fcldi az aut\u00f3 adatait. Nincs fi\u00f3k, nincs felh\u0151: az adatok a Home Assistantban maradnak. V\u00e1lassza a K\u00fcld\u00e9s gombot, majd illessze be a c\u00edmet az alkalmaz\u00e1sba.",
        "created": "A DrivePulse k\u00e9sz. Az alkalmaz\u00e1sban nyissa meg a \u201e{menu}\u201d men\u00fct, illessze be ezt a c\u00edmet a \u201e{field}\u201d mez\u0151be, \u00e9s koppintson a \u201e{test}\u201d gombra:\n\n{webhook_url}\n\nOtthonon k\u00edv\u00fcl haszn\u00e1lja a Home Assistant HTTPS c\u00edm\u00e9t (p\u00e9ld\u00e1ul Nabu Casa) vagy VPN-t, \u00e9s kapcsolja ki az \u201eCsak helyi h\u00e1l\u00f3zat\u201d be\u00e1ll\u00edt\u00e1st az integr\u00e1ci\u00f3 be\u00e1ll\u00edt\u00e1saiban.",
        "opt_desc": "A DrivePulse alkalmaz\u00e1sba beillesztend\u0151 c\u00edm (\u201e{menu}\u201d):\n\n{webhook_url}",
        "local_only": "Csak helyi h\u00e1l\u00f3zat",
        "local_only_desc": "Az alkalmaz\u00e1st csak az otthoni h\u00e1l\u00f3zatr\u00f3l (vagy VPN-r\u0151l) fogadja el. Kapcsolja ki, ha az internetr\u0151l, a HTTPS c\u00edmen kereszt\u00fcl akar adatot kapni.",
        "fuel_level": "\u00dczemanyagszint", "battery_level": "Akkumul\u00e1torszint", "range": "Hat\u00f3t\u00e1vols\u00e1g",
        "odometer": "Kilom\u00e9ter\u00f3ra", "battery_voltage": "12 V-os akkumul\u00e1tor", "coolant_temperature": "H\u0171t\u0151folyad\u00e9k h\u0151m\u00e9rs\u00e9klete",
        "trouble_codes": "Hibak\u00f3dok", "fuel_volume": "\u00dczemanyag", "speed": "Sebess\u00e9g", "engine_speed": "Motorford\u00falatsz\u00e1m",
        "last_trip_distance": "Utols\u00f3 \u00fat", "trip_in_progress": "\u00dat folyamatban", "adapter_connected": "Adapter csatlakoztatva",
    },
    "pl": {
        "user_title": "Dodaj DrivePulse",
        "user_desc": "Tworzy prywatny adres (webhook), na kt\u00f3ry aplikacja DrivePulse wysy\u0142a dane Twojego auta. Bez konta, bez chmury: dane zostaj\u0105 w Twoim Home Assistant. Wybierz Prze\u015blij, a potem wklej adres w aplikacji.",
        "created": "DrivePulse jest gotowy. W aplikacji otw\u00f3rz \u201e{menu}\u201d, wklej ten adres w polu \u201e{field}\u201d i dotknij \u201e{test}\u201d:\n\n{webhook_url}\n\nPoza domem u\u017cyj adresu HTTPS swojego Home Assistant (na przyk\u0142ad Nabu Casa) lub VPN i wy\u0142\u0105cz \u201eTylko sie\u0107 lokalna\u201d w opcjach integracji.",
        "opt_desc": "Adres do wklejenia w aplikacji DrivePulse (\u201e{menu}\u201d):\n\n{webhook_url}",
        "local_only": "Tylko sie\u0107 lokalna",
        "local_only_desc": "Przyjmuj dane z aplikacji tylko z sieci domowej (lub przez VPN). Wy\u0142\u0105cz, aby odbiera\u0107 z internetu przez adres HTTPS.",
        "fuel_level": "Poziom paliwa", "battery_level": "Poziom baterii", "range": "Zasi\u0119g",
        "odometer": "Przebieg", "battery_voltage": "Akumulator 12 V", "coolant_temperature": "Temperatura p\u0142ynu ch\u0142odz\u0105cego",
        "trouble_codes": "Kody b\u0142\u0119d\u00f3w", "fuel_volume": "Paliwo", "speed": "Pr\u0119dko\u015b\u0107", "engine_speed": "Obroty silnika",
        "last_trip_distance": "Ostatnia podr\u00f3\u017c", "trip_in_progress": "Podr\u00f3\u017c w toku", "adapter_connected": "Adapter po\u0142\u0105czony",
    },
    "ro": {
        "user_title": "Adaug\u0103 DrivePulse",
        "user_desc": "Aceasta creeaz\u0103 o adres\u0103 privat\u0103 (un webhook) c\u0103tre care aplica\u021bia DrivePulse trimite datele ma\u0219inii tale. F\u0103r\u0103 cont, f\u0103r\u0103 cloud: datele r\u0103m\u00e2n \u00een Home Assistant. Selecteaz\u0103 Trimite, apoi lipe\u0219te adresa \u00een aplica\u021bie.",
        "created": "DrivePulse este gata. \u00cen aplica\u021bie deschide \u201e{menu}\u201d, lipe\u0219te aceast\u0103 adres\u0103 la \u201e{field}\u201d \u0219i atinge \u201e{test}\u201d:\n\n{webhook_url}\n\nC\u00e2nd e\u0219ti plecat, folose\u0219te adresa HTTPS a Home Assistant (de exemplu Nabu Casa) sau un VPN \u0219i dezactiveaz\u0103 \u201eDoar re\u021bea local\u0103\u201d \u00een op\u021biunile integr\u0103rii.",
        "opt_desc": "Adresa de lipit \u00een aplica\u021bia DrivePulse (\u201e{menu}\u201d):\n\n{webhook_url}",
        "local_only": "Doar re\u021bea local\u0103",
        "local_only_desc": "Accept\u0103 aplica\u021bia doar din re\u021beaua de acas\u0103 (sau printr-un VPN). Dezactiveaz\u0103 pentru a primi de pe internet prin adresa ta HTTPS.",
        "fuel_level": "Nivel combustibil", "battery_level": "Nivel baterie", "range": "Autonomie",
        "odometer": "Kilometraj", "battery_voltage": "Baterie 12 V", "coolant_temperature": "Temperatura lichidului de r\u0103cire",
        "trouble_codes": "Coduri de eroare", "fuel_volume": "Combustibil", "speed": "Vitez\u0103", "engine_speed": "Tura\u021bie motor",
        "last_trip_distance": "Ultima c\u0103l\u0103torie", "trip_in_progress": "C\u0103l\u0103torie \u00een curs", "adapter_connected": "Adaptor conectat",
    },
}


def app_labels(lang: str) -> dict[str, str]:
    arb = json.loads((ARB / f"app_{lang}.arb").read_text(encoding="utf-8"))
    return {
        "menu": arb["ha_settings_title"],
        "field": arb["ha_url_label"],
        "test": arb["ha_test"],
    }


SENSORS = [
    "fuel_level", "battery_level", "range", "odometer", "battery_voltage",
    "coolant_temperature", "trouble_codes", "fuel_volume", "speed",
    "engine_speed", "last_trip_distance",
]


def build(lang: str) -> dict:
    t = T[lang]
    labels = app_labels(lang)

    def fill(text: str) -> str:
        # Fill the app labels, keep {webhook_url} for Home Assistant.
        return text.replace("{menu}", labels["menu"]).replace(
            "{field}", labels["field"]).replace("{test}", labels["test"])

    return {
        "config": {
            "step": {"user": {"title": t["user_title"], "description": t["user_desc"]}},
            "create_entry": {"default": fill(t["created"])},
        },
        "options": {
            "step": {
                "init": {
                    "description": fill(t["opt_desc"]),
                    "data": {"local_only": t["local_only"]},
                    "data_description": {"local_only": t["local_only_desc"]},
                }
            }
        },
        "entity": {
            "sensor": {k: {"name": t[k]} for k in SENSORS},
            "binary_sensor": {
                "trip_in_progress": {"name": t["trip_in_progress"]},
                "adapter_connected": {"name": t["adapter_connected"]},
            },
        },
    }


OUT.mkdir(parents=True, exist_ok=True)
for lang in LANGS:
    (OUT / f"{lang}.json").write_text(
        json.dumps(build(lang), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
print("written", len(LANGS))
