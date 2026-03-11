import copy


def normalize_line(line: str) -> str:
    line = line.split("//", 1)[0]   # SCL-Kommentar
    return line.strip()
import re
from copy import deepcopy
BLOCK_CALL_RE = re.compile(
    r"""
    ^
    (?:\s*(?P<ret>\w+)\s*:=\s*)?
    (?P<name>\#?[A-Za-z_][A-Za-z0-9_]*)
    \s*
    \(
    """,
    re.VERBOSE
)


def block_type(name: str) -> str:
    name = name.upper()

    if name.startswith("FC"):
        return "FC"
    if name.startswith("FB"):
        return "FB"

    return "FB_INSTANCE"


def collect_block_call(lines: list[str], start_index: int):
    buffer = []
    paren_level = 0

    for i in range(start_index, len(lines)):
        line = lines[i]
        buffer.append(line)

        paren_level += line.count("(")
        paren_level -= line.count(")")

        if paren_level == 0 and ");" in line:
            return {
                "start": start_index,
                "end": i,
                "code": buffer
            }

    return None

def detect_block_call(lines: list[str], i: int):
    KEYWORDS = {
        "IF", "WHILE", "CASE", "FOR", "ELSIF", "RETURN"
    }
    line = normalize_line(lines[i])

    m = BLOCK_CALL_RE.match(line)
    if not m:
        return None

    name = m.group("name").lstrip("#")
    ret = m.group("ret")
    if name.upper() in KEYWORDS:
        return None

    call = collect_block_call(lines, i)
    if not call:
        return None

    return {
        "instance": name,
        "type": block_type(name),
        "call": call,
        "return": ret}


PARAM_RE = re.compile(
    r"""
    (?P<name>"[^"]+"|\w+)
    \s*
    (?P<op>:=|=>)
    \s*
    (?P<value>[^,)\n]+)?
    """,
    re.VERBOSE
)



def extract_names_and_values(code_lines: list[str]) -> dict[str, str | None]:
    params = {}

    for line in code_lines:
        for m in PARAM_RE.finditer(line):
            name = m.group("name").strip('"')
            value = m.group("value")

            params[name] = value.strip() if value else None

    return params



def Baustein_erkennen(cod: list[str],startwert:int,Bausteine) -> (list[object],list[str]):
    i:int = startwert
    Baustein_list:list[str] = []
    Baustein_list_fehlend:list[str] = []
    Baustein_aufrufe:dict[int:str] = {}
    Veriabeln_zuordung = {}
    while i < len(cod):
        Baustein_SCL =detect_block_call(cod,i)
        if Baustein_SCL is None:
            i += 1
            continue

        Baustein_aufrufe[i-startwert]= Baustein_SCL["instance"]


        if not Baustein_SCL["instance"] in  Bausteine.keys():
            Baustein_list_fehlend.append(Baustein_SCL["instance"])
            i += Baustein_SCL["call"]["end"]
            continue

        params  = extract_names_and_values(Baustein_SCL["call"]["code"])
        Veriabeln_zuordung[i-startwert] = copy.deepcopy(params)

        input_V = []
        for element in Bausteine[Baustein_SCL["instance"]].Veriablen_reinfolge_in:
            input_V.append(params[element])
        output = []
        for element in Bausteine[Baustein_SCL["instance"]].Veriablen_reinfolge_out:
            output.append(params[element])

        if Baustein_SCL["return"]:
            Veriabeln_zuordung[i - startwert][Baustein_SCL["return"]] = Baustein_SCL["return"]
            output.append(Baustein_SCL["return"])
        funcion_start = Baustein_SCL["call"]["start"]
        funcion_end = Baustein_SCL["call"]["end"]
        cod[funcion_start] = f"{",".join(output)} := {Baustein_SCL["instance"]}({",".join(input_V)})"
        for element in range(funcion_start+1, funcion_end+1):
            cod[element] = "" #lösche SCl Zeilen von aufruf

        Baustein_list.append( Baustein_SCL["instance"])
        i = funcion_end +1

    return Baustein_list, cod,Baustein_list_fehlend,Baustein_aufrufe,Veriabeln_zuordung