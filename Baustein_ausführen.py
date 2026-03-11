import copy
import sys
from baustein_erstellen import Baustein

def execute_with_trace(code: str):
    trace_data = []

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != "<string>":
            return tracer

        if event in ( "line", ):
            trace_data.append({
                #"event": event,
                #"function": frame.f_code.co_name,
                "line": frame.f_lineno,
                "locals": copy.copy({
                    k: v
                    for k, v in frame.f_locals.items()
                    if not k.startswith("__")
                })
            })

        return tracer

    sys.settrace(tracer)
    try:
        exec(code, {})
    except Exception as e:
        # Drucke den Fehler
        #print("Ein Fehler ist aufgetreten:")
        #print(e)
        temp = {}
        temp["locals"] ={"Fehler" : "SyntaxError"}
        temp["line"] = 1
        trace_data.append(temp)
        trace_data.append(temp)
    finally:
        sys.settrace(None)

    return trace_data


def Variablen_bereitstellen(speicher:dict[str, dict[str, str]],input_V  = True)-> str:
    ausgabe = ""
    if input_V:
        for (key,katrorie) in speicher.items():
            for (name,wert) in katrorie.items():

                ausgabe += f"{name} = {wert}\n"

    else:
        for (key,katrorie) in speicher.items():
            if not key == input_V:
                for (name,wert) in katrorie.items():

                    ausgabe += f"{name} = {wert}\n"


    return ausgabe
def python_code_erstellen(bausteine: dict[str, Baustein], Baustein_name: str,Veriabelen:None| list[str] = None):
    zeilen = 0
    code = ""
    # 1. Abhängige Bausteine als Funktionen
    reihenfolge = bausteine_ermitteln(bausteine, Baustein_name)



    abhängige = reihenfolge[:-1]  # ohne Hauptbaustein

    for dep in abhängige:
        fun_code, fun_zeilen = Baustein_zu_fun(dep, bausteine)
        code += fun_code + "\n"
        zeilen += fun_zeilen +1

    #  Initialvariablen (VAR, TEMP, STATIC des Hauptbausteins)
    if Veriabelen ==  None:
        code += Variablen_bereitstellen(bausteine[Baustein_name].Veriablen,False)
        zeilen += bausteine[Baustein_name].zeilen_Veriabelen
    else:

        #code += Variablen_bereitstellen(bausteine[Baustein_name].Veriablen, True)
        for index,Veriabele in enumerate( bausteine[Baustein_name].Veriablen_reinfolge_in):
            code += f"{Veriabele} = {Veriabelen[index]}\n"
        zeilen += len(bausteine[Baustein_name].Veriablen_reinfolge_in)

    if bausteine[Baustein_name].typ == "FB":
        code_Fb,zeilen = init_fb_memory(bausteine, reihenfolge,zeilen)
        code += code_Fb
        Veriablen = bausteine[Baustein_name].Veriablen["var"]
        zeilen += len(Veriablen)
        for (name, wert) in Veriablen.items():
            code += f"{name} = __FB_MEMORY['{Baustein_name}']['__{name}']\n"
    #  Haupt-SCL-Code INLINE (wichtig!)
    for line in bausteine[Baustein_name].cod:
        code += line + "\n"
    code += "ende = True # auto eingefügt"
    #print("start code")
    #print(code)
    #print("end code")
    return code,zeilen

def ausführen(python_code:str):


    # Trace ausführen
    trace = execute_with_trace(python_code)
    return trace


def bausteine_ermitteln(
        bausteine: dict[str, Baustein],
        name: str,
        result: list[str] | None = None,
    visited: set[str] | None = None
) -> list[str]:
    if bausteine[name].Baustein_fertig == False:
        raise ValueError(f"baustein nicht volständig: {name}")
    if result is None:
        result = []
    if visited is None:
        visited = set()

    if name in visited:
        return result

    visited.add(name)
    if  bausteine[name].Baustein_list: #Abfrage ob ein elment vorhaden ist
        for dep in bausteine[name].Baustein_list:
            bausteine_ermitteln(bausteine, dep, result, visited)

    result.append(name)  # WICHTIG: erst Dependencies, dann selbst
    return result



def Baustein_zu_fun(Baustein_name: str, bausteine: dict[str, Baustein]) -> tuple[str, int]:
    baustein = bausteine[Baustein_name]

    header = f"def {Baustein_name}({', '.join(baustein.Veriablen_reinfolge_in)}):\n"

    body = ""
    zeilen = len(baustein.cod)

    if baustein.typ == "FB":
        Veriablen = baustein.Veriablen["var"]
        zeilen += len(Veriablen)
        for (name, wert) in Veriablen.items():
            body += f"    {name} = __FB_MEMORY['{Baustein_name}']['__{name}']\n"

    for n in ["static","temp"]:
        Veriablen = baustein.Veriablen[n]
        zeilen += len(Veriablen)
        for (name, wert) in Veriablen.items():
            body += f"    {name} = {wert}\n"

    for line in baustein.cod:
        body += f"    {line}\n"

    if baustein.typ == "FB":
        Veriablen = baustein.Veriablen["var"]
        zeilen += len(Veriablen)
        for (name, wert) in Veriablen.items():
            body += f"    __FB_MEMORY['{Baustein_name}']['__{name}'] = {Baustein_name} \n"
    footer = f"    return {', '.join(baustein.Veriablen_reinfolge_out)}\n"

    code = header + body + footer

    return code, zeilen




from typing import Any

def init_fb_memory(Bausteine: dict[str, Baustein],Reihenfolge: list[str],zeilen:int)->[str,int]:
    code = "__FB_MEMORY:dict[str,dict[str,any]] = {"
    zeilen += 1

    for bname in Reihenfolge:
        if Bausteine[bname].typ == "FC":
            continue
        vars_ = Bausteine[bname].Veriablen.get("var")
        code += f'"{bname}":{{\n'
        zeilen +=1
        for vname, wert in vars_.items():

            code += f'"__{vname}":{wert},'
        code += "},"
    code += "}\n"
    return code, zeilen



def veriabeln_aufruf_filtern(name,bausteine: dict[str, Baustein],Veriabelen:dict[str,str]) -> dict[str:str]:
    Veriablen_input = bausteine[name].Veriablen_reinfolge_in
    Veriablen_ausgabe = {}
    for var_name, valu in Veriabelen.items():
        if var_name in Veriablen_input:
            Veriablen_ausgabe[var_name] = valu
    return Veriablen_ausgabe

