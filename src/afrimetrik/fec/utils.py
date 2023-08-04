from typing import Optional
import re

FEC_CONSTANTS = [
    "RREEPPEERRTTOOIIRREE DDEESS EENNTTRREEPPRRIISSEESS CCOOMMMMEERRCCIIAALLEESS",
    "REPERTOIRE DES ENTREPRISES COMMERCIALES, INDUSTRIELLES ET DE SERVICES"
    "RREEPPEERRTTOOIIRREE DDEESS EENNTTRREEPPRRIISSEESS",
    "REPERTOIRE DES ENTREPRISES COMMERCIALES"
]

def parse_legal(raw: list[str]) -> Optional[str]:
    for elt in raw:
        if (
            "nom" in elt.lower()
            or "www" in elt
            or has_address(elt)
            or "Tél" in elt
            or '@' in elt
            or "secteur" in elt.lower()
            or has_fec(elt)
        ):
            continue
        has_virgule = elt.count(',')
        res = elt.replace("/", " ")
        if has_virgule == 1:
            res = "".join(res.split(',')[:-1])
        elif has_virgule == 2:
            res = "".join(res.split(',')[:-2])
        elif has_virgule == 3:
            res = "".join(res.split(',')[:-3])
        return re.sub(" \d+", " ", res)


ADRESS_INDICATORS = [
    "av.",
    "av,",
    "a/1",
    "av",
    "local",
    "immeuble",
    "imm.",
    "rue",
    "n°",
    "route",
    "appartement",
    "c/",
    "q/",
    "boulevard",
    "blvd",
    "niveau",
    "avenue",
    "commune",
    "ville",
    "domaine",
    "village",
]

def has_fec(text: str) -> bool:
    return any(cst in text for cst in FEC_CONSTANTS)

def has_address(text: str) -> bool:
    components = text.lower().split(" ")
    return any(component.strip() in ADRESS_INDICATORS for component in components)


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
            if e and ("Tél" in e or "Tel" in e)
        ),
        None,
    )


def parse_siteurl(raw: list[str]):
    for elt in raw:
        if "www" in elt:
            url = elt.split("www")[-1]
            return f"www{url}"


def parse_webinfo(raw: list[str]):
    for elt in raw:
        if "@" in elt:
            elt = elt.replace(".com :", ".com").strip()
            return elt.split("www")[0].split(" ")[-1]


def parse_state(list_comp: str) -> Optional[str]:
    for raw in list_comp:
        for state in RDC_STATE_LIST:
            if state.lower() in raw.lower() and "av" not in raw.lower():
                return state.capitalize()
    return ""

def append_to_company(company: list[str], elt: str) -> list[str]:
    for e in company:
        if elt in e or e in elt:
            return company
    return [*company, elt]



def parse_address(raw: list[str], cmp_name: str = "") -> Optional[str]:
    if type(raw) == str:
        return parse_address_string(raw)
    for elt in raw:
        return parse_address_string(elt)

def parse_address_string(elt: str):
    for indice in ADRESS_INDICATORS:
        if indice in elt.lower():
            adresse = elt.split(indice.capitalize())[-1]
            return f"{indice.capitalize()}{adresse}"
    if "," in elt:
        return elt.split(",")[-1]

def print_list(elts):
    for elt in elts:
        print(elt)

def parse_contact_name(raw: list[str]):
    for elt in raw:
        if "nom" in elt.lower():
            return elt.split(":")[-1].strip()


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

EXCLUDE_ADDRESS_KEYS = ["Manioc", "en", "du", "au", "TE", *FEC_CONSTANTS]
EXCLUDE_LEGALS = ["Manioc", *FEC_CONSTANTS] + [
    state.upper() for state in RDC_STATE_LIST
]
EXCLUDE_PROFILE_NAME = ["Manioc"]

if __name__ == '__main__':
    addresse = 'AGRIUMBE Immeuble INTERFINA, 9, Boulevard du 30 juin'
    legals = [
        ["EPICIER 12, Kivunda C/Mont-Ngafula(MBUDI)"],
        ["MANITECH 26, KUTU, C/Ngaliema"],
        ["ADONIS 5,Av. Tchad"],
        ["AFRICOS 34, LOKELE, C/Gombe"],
        ["ALPHA TOPO RDC 63, Col. Mondjiba, C/Ngaliema"],
        ["CMT/MUAMBA MPOYI 988, Kingabwa, C/Limete"],
        ["AGRIUMBE"],
        ["BRABANTA /16"]
    ]
    for legal in legals:
        print(f"\nDefault: {legal} Legal: {parse_legal(legal)}")