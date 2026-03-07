# Nicht unterstütz GOTO, bit zugrief
from operator import itemgetter

import Baustein_erkennen
import dataclasses
import copy

@dataclasses.dataclass
class Baustein:
    def __init__(self,name:str,cod:list[str],Veriablen:dict[str, dict[str, str]],Veriablen_reinfolge_in:list[str],Veriablen_reinfolge_out:list[str],typ,Baustein_list,zeilen_Veriabelen,SCL_text,Baustein_fertig,Baustein_aufrufe,Veriabeln_zuordung):
        self.typ = typ
        self.name:str=name
        self.cod:list[str]=cod
        self.Veriablen=Veriablen
        self.Veriablen_reinfolge_in=Veriablen_reinfolge_in
        self.Veriablen_reinfolge_out=Veriablen_reinfolge_out
        self.Baustein_list:list[str] = Baustein_list # zusätzliche benötigte Bausteine
        self.zeilen_Veriabelen= zeilen_Veriabelen
        self.SCL_text:str = SCL_text
        self.Baustein_fertig = Baustein_fertig
        self.Baustein_aufrufe:dict[int,str] = Baustein_aufrufe # Zeile und Name
        self.Veriabeln_zuordung = Veriabeln_zuordung





def extract_scl_runtime_code(text: list[str]) -> (list[str],int):
    """SCL-Code ab BEGIN bis vor END_FUNCTION_BLOCK"""
    code = []
    in_begin = False
    Zeile = 1
    for line in text:
        if line.strip() == "BEGIN":
            in_begin = True
            continue

        if line.strip() in ["END_FUNCTION_BLOCK" ,"END_FUNCTION"]:
            break

        if in_begin:
            code.append(f"{Zeile}{line}")
            Zeile += 1

    return code


def Variablen_in_dic(speicher: dict[str, list[str]]) -> [dict[str, dict[str, str]], int]:
    """
    return = {teyp:{Varible: Wert in str,...},...}

    """
    typ_defaults = {
        "INT": "0",
        "DINT": "0",
        "REAL": "0.0",
        "LREAL": "0.0",
        "BOOL": "False",
        "STRING": '""',
        "WORD": "0",
        "DWORD": "0",
        "BYTE": "0",
    }

    ausgabe = {}
    zeilen = 0
    for key in speicher.keys():
        ausgabe[key] ={}
        block = speicher[key]
        for zeile in block:
            zeile = zeile.strip().rstrip(";")

            if ":" not in zeile:
                continue
            zeilen += 1
            # name : typ := wert
            if ":=" in zeile:
                links, wert = zeile.split(":=", 1)
            else:
                links = zeile
                wert = None

            name, typ = links.split(":", 1)
            name = name.strip().lstrip("#")
            typ = typ.strip().upper()

            if wert is None:
                wert = typ_defaults.get(typ, "0")
                if wert == "0":



                    if typ.startswith("ARRAY"):
                        innen = typ.split("[", 1)[1].split("]", 1)[0]
                        start, ende = innen.split("..")

                        start = int(start)
                        ende = int(ende)

                        basis_typ = typ.split("OF", 1)[1].strip().upper()
                        default = typ_defaults.get(basis_typ, "0")
                        wert = "["
                        for _ in range(0, ende +2):
                            wert += f"{default}, "
                        wert += "]"
                        print(start, ende, typ)


            ausgabe[key][name] = wert

    return ausgabe,zeilen


    return ausgabe
def überstzer_cod(text:list[str],start,länge,bausteine)-> list[str]:
    ausgabe = []

    einrücken = 0
    ausfürhen_einrücken = 0
    SCL_TO_PY_TOKEN = {
        ":=": "=",
        "=": "==",
        "<>": "!=",
        "MOD": "%",
        "AND": "and",
        "OR": "or",
        "NOT": "not",
        "XOR": "^",
        "CONTINUE" : "continue",
        "THEN":"):",
    }
    for lane in range(start,länge):

        if text[lane] == "END_FUNCTION_BLOCK" or text[lane] == "END_FUNCTION":
            for line in ausgabe:
                print(line)
            return ausgabe
        zeichen= text[lane].rstrip(";")
        zeichen = zeichen.rstrip("#")
        zeichen = zeichen.split()
        for i in range( len(zeichen)):

            if  zeichen[i] == "//":
                zeichen[i] = "#"
                break
            elif zeichen[i] == "IF":
                zeichen[i] = "if ("
                einrücken += 2
            elif zeichen[i] == "END_IF;" or  zeichen[i] == "END_IF":
                zeichen[i] = ""
                einrücken -= 2
            elif zeichen[i] == "ELSIF":
                zeichen[i] = "elif ("
                ausfürhen_einrücken -= 2
            elif zeichen[i] == "ELSE":
                zeichen[i] = "else:"
                ausfürhen_einrücken -= 2
            elif zeichen[i] == "WHILE":
                zeichen[i] = "while ("
                einrücken += 2
            elif zeichen[i] == "DO":
                zeichen[i] = "):"
            elif zeichen[i] == "END_WHILE":
                zeichen[i] = ""
                einrücken -= 2
            elif zeichen[i] == "REPEAT":
                zeichen[i] = "while True:"
                einrücken += 2
            elif zeichen[i] == "UNTIL":
                zeichen[i] = "if"
                zeichen.append(": break")
            elif zeichen[i] == "END_REPEAT":
                zeichen[i] = ""
                einrücken -= 2
            if zeichen[i] == "FOR":
                einrücken += 2
                zeichen[i] = "for"
                for j in range( len(zeichen)+1):
                    if zeichen[j] == ":=":
                        zeichen[j] = " in range("
                    if zeichen[j] == "TO":
                        zeichen[j] = ","
                        zeichen[j+1] = f"{zeichen[j+1]} + 1"
                        #zeichen[j+1] = f"{ int(zeichen[j+1]) +1}"
                        #muss noch um eins erhöt werden
                    if zeichen[j] == "BY" :
                        zeichen[j] = ","
                    if zeichen[j] == "DO":
                        zeichen[j] = "):"
                        break
            elif zeichen[i] == "EXIT":
                zeichen[i] = "break"
            elif zeichen[i] == "END_FOR":
                zeichen[i] = ""
                einrücken -= 2
            elif zeichen[i] == "CASE":
                zeichen[i] = "match"
                einrücken += 2
            elif zeichen[i] == "OF":
                zeichen[i] = ":"

            elif zeichen[i] == "END_CASE":
                # Blockende → Einrückung zurücksetzen
                einrücken -= 2
            zeichen[i] = SCL_TO_PY_TOKEN.get(zeichen[i], zeichen[i])
        ausgabe.append(f"{" "*ausfürhen_einrücken}{" ".join(zeichen)}")
        ausfürhen_einrücken = einrücken

""" 

test:=... ;
test := 
"""
def sammeln_Veriabeln(text:str,start:int,länge:int):
    liste = []

    for line in range(start, länge):
        if text[line] == "END_VAR":
            return liste
        liste.append(text[line])



def Baustein_erstellen(text:list[str],bausteine):
    """

      :param text:
      :return:
      "cod" : code_block, "list[list]
    "zeilen" : zeilen,
    "trace" : trace,
    "Veriablen" : Veriablen,}"cod" : code_block,
    """
    speicher = {
        "input" : [],
        "output": [],
        "static" : [],
          "temp" : [],
        "var" : []

    }
    #text =text.split("\n")
    länge = len(text)
    code_block: list[str] = []
    for line in range(länge):#
         zeile = text[line].split()
         if zeile[0] == "FUNCTION_BLOCK" or zeile[0] ==  "FUNCTION":
             name = zeile[1]
             if zeile[0] == "FUNCTION_BLOCK":
                 typ = "FB"
             else:
                 typ = "FC"
             break
    for line in range(länge):
        if text[line] == "VAR_INPUT":
            speicher["input"] = sammeln_Veriabeln(text,line+1,länge)
        elif text[line] == "VAR_OUTPUT":
            speicher["output"] = sammeln_Veriabeln(text, line + 1, länge)
        elif text[line] == "VAR_STATIC":
            speicher["static"] = sammeln_Veriabeln(text, line + 1, länge)
        elif text[line] == "VAR_TEMP":
            speicher["temp"] = sammeln_Veriabeln(text, line + 1, länge)
        elif text[line] == "VAR":
            speicher["var"] = sammeln_Veriabeln(text, line + 1, länge)
        elif text[line] == "BEGIN":
            Baustein_list, code,Baustein_list_fehlend,Baustein_aufrufe,Veriabeln_zuordung= Baustein_erkennen.Baustein_erkennen(copy.deepcopy( text),line + 1,bausteine)
            code_block = überstzer_cod(code,line+1,länge,bausteine)
            break
    if code_block == []:
        raise ValueError(
            f"Kein ausführbarer Code im Baustein '{name}' gefunden")
    if typ not in ("FC", "FB"):
      raise ValueError(f"Unbekannter Bausteintyp: {typ}")

    Veriablen,zeilen = Variablen_in_dic(speicher)
    if Baustein_list_fehlend:
        Baustein_fertig = False
    else:
        Baustein_fertig = True
    #print(speicher)
    #print(Veriablen,)
    #print(zeilen)
    SCL_text = extract_scl_runtime_code(text)
    return   Baustein(
              name=name,
              cod=code_block,
              Veriablen=Veriablen,
              Veriablen_reinfolge_in=Veriablen["input"].keys(),
              Veriablen_reinfolge_out=Veriablen["output"].keys(),
              typ= typ,  # "FC" oder "FB"
              Baustein_list=Baustein_list,
              zeilen_Veriabelen=zeilen,
              SCL_text=  SCL_text,
              Baustein_fertig= Baustein_fertig,
              Baustein_aufrufe= Baustein_aufrufe,
              Veriabeln_zuordung= Veriabeln_zuordung
          ),Baustein_list_fehlend







if __name__ == "__main__":
    # Nicht mher funktionn tüchtig
    with open("text", 'r', encoding='utf-8') as file:
        content =  file.read().splitlines()

