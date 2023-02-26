from typing import Optional


def parse_legal(raw: list[str]) -> Optional[str]:
    legals = [
        l for l in raw if l and "Nom" not in l and "Tel" not in l and "secteur" not in l
    ]
    for ex in EXCLUDE_LEGALS:
        if ex in legals:
            legals.remove(ex)
    return next(
        (legal.split("|")[0].strip().replace('Tel', '') for legal in legals if '@' not in legal),
        None,
    )


def parse_city(raw: list[str]) -> Optional[str]:
    return None


def parse_sectors(raw: list[str]) -> Optional[str]:
    return next(
        (
            [
                r.strip()
                for r in e.replace("|", "")
                .replace("et", "")
                .split(":")[-1]
                .split(" ")[:-1]
                if r
            ]
            for e in raw
            if e and "secteur" in e
        ),
        None,
    )


def parse_phones(raw: list[str]) -> Optional[list[str]]:
    return next(
        (
            [r.strip() for r in e.replace("|", "").split(":")[-1].split("-") if r]
            for e in raw
            if e and "Tel" in e
        ),
        None,
    )

def parse_webinfo(raw: list[str]):
    get_email = lambda s: s if "@" in s else None
    res = next(
        (
            e.replace("|", "").split(":")[-1].split(" ")[-1].strip()
            for e in raw
            if e and "secteur" in e
        ),
        None,
    )
    return (
        (get_email(res), None)
        if "www" not in res
        else (get_email(res[: res.index("www")]), res[res.index("www") :])
    )


def parse_state(raw: str) -> Optional[str]:
    raw = raw.lower()
    return next(
        (state.upper() for state in RDC_STATE_LIST if state.lower() in raw),
        None,
    )


def parse_address(raw: list[str]) -> Optional[str]:
    return next(
        (
            e.split("|")[-1].strip()
            for e in raw
            if e 
            and "secteur" in e
            or ("Nom" not in e and "Tel" not in e and "www" not in e)
        ),
        None,
    )


def parse_contact_name(raw: list[str]):
    new_raw = [el for el in raw if el not in EXCLUDE_PROFILE_NAME and ("Nom" in el or ('Tel' not in el and 'secteur' not in el))]
    return next(
        (
            r.replace('|', '').split(":")[1].strip()
            for r in new_raw
            if 'Nom' in r
        ),
        None,
    )


RDC_STATE_LIST = [
    "Bas-Uele",
    "Equateur",
    "Haut-Lomami",
    "Haut-Katanga",
    "Haut-Uele",
    "Ituri",
    "Kasai",
    "Kasai central",
    "Kasai oriental",
    "Kinshasa",
    "Kongo-Central",
    "Kwango",
    "Kwilu",
    "Lomami",
    "Lualaba",
    "Mai-Ndombe",
    "Maniema",
    "Mongala",
    "Nord-Kivu",
    "Nord-Ubangi",
    "Sankuru",
    "Sud-Kivu",
    "Sud-Ubangi",
    "Tanganyika",
    "Tshopo",
    "Tshuapa",
]

EXCLUDE_ADDRESS_KEYS = [
    "Manioc", 
    "en",
    "du"
]
EXCLUDE_LEGALS = ['Manioc'] + [state.upper() for state in RDC_STATE_LIST]
EXCLUDE_PROFILE_NAME = ['Manioc']