import copy
import Baustein_ausführen
import baustein_erstellen
from baustein_erstellen import Baustein
import dataclasses
import load_start_Bausteine

@dataclasses.dataclass
class Baustein_aufrufe:

    def __init__(self,treas,current_step,baustein_name,zeilen_offset):
        self.treas = treas
        self.current_step:int = current_step
        self.baustein_name:str = baustein_name
        self.zeilen_offset = zeilen_offset


class mager:
    def __init__(self, ):
        self.bausteine : dict[str,Baustein] = {}
        self.FBs: dict[str,Baustein] = {}
        self.bausteine_fehlen: dict[str:list[str]] = {}
        self.FBs_instanzen:dict[str,dict[str,bool]] = {}

        self.baustein_name = "FB_Test"
        self.current_step = 0
        self.aufruf_liste= []


        self.FBs = load_start_Bausteine.load_start_Bausteine(self.FBs)

    def Baustein_speicherung_mit_zordung(self, aktuler_Baustein: Baustein, FBs: dict[str, Baustein], Bausteine:dict[str, str] ):
        zwischen_speicher = []
        veriabeln = aktuler_Baustein.Veriablen.get("var",None)
        Bausteine[aktuler_Baustein.name] = aktuler_Baustein
        if veriabeln == None:

            return aktuler_Baustein, Bausteine,FBs
        for (key, wert) in veriabeln.items():
            if wert in FBs:
                if wert == aktuler_Baustein.name:
                    zwischen_speicher.append((key, wert))
                    Bausteine[key] = copy.deepcopy(FBs[wert])
                veriabeln[key] = "false // FB"
        FBs[aktuler_Baustein.name] = aktuler_Baustein
        for (key, wert) in zwischen_speicher:
            self.Baustein_speicherung_mit_zordung[wert][key] = True
            Bausteine[key] = copy.deepcopy(FBs[wert])
        return aktuler_Baustein, Bausteine,FBs


    def Baustein_hinzufügen(self,text:list[str]):
        baustein, Baustein_list_fehlend = baustein_erstellen.Baustein_erstellen(text, self.bausteine)
        self.bausteine[baustein.name] = baustein

        if Baustein_list_fehlend:
            self.bausteine_fehlen[baustein.name] = (Baustein_list_fehlend, text)

        self.bausteine, self.bausteine_fehlen = self.vollstaendigt_Bausteine(self.bausteine,
                                                                                           self.bausteine_fehlen)

    def vollstaendigt_Bausteine(self,Bausteine: dict[str, Baustein], Baustein_fehlend: dict[str, tuple[str, list[str]]]):
        # über Kopie iterieren!
        for baustein_name in list(Baustein_fehlend.keys()):

            fehlende = Baustein_fehlend[baustein_name][0]
            SCL_cod = Baustein_fehlend[baustein_name][1]
            # Prüfen: sind alle benötigten Bausteine vorhanden?
            alle_vorhanden = True
            for instance in fehlende:
                if not instance in Bausteine:
                    alle_vorhanden = False
                    break

            if not alle_vorhanden:
                continue

            # Baustein vervollständigen
            Bausteine[baustein_name], Baustein_list_fehlend = baustein_erstellen.Baustein_erstellen(SCL_cod, Bausteine)
            Bausteine[baustein_name].Baustein_fertig = True
            # Lehere Liste wen Baustein ist FC
            for elment in self.FBs_instanzen.get(baustein_name,[]):
                Bausteine[elment] =Bausteine[baustein_name]
            # aus "fehlend" entfernen
            Baustein_fehlend.pop(baustein_name)

        return Bausteine, Baustein_fehlend


    def Baustein_ausgabe(self,Baustein_name=None):
        if Baustein_name == None:
            Baustein_name = self.baustein_name
        return self.bausteine[Baustein_name]

    def open_selected_baustein(self,name):
            self.baustein_name = name
            self.Baustein = self.bausteine[self.baustein_name]
            self.aufruf_liste = []
            self.reload_mager()

    def remove_selected_baustein(self,baustein_name):

        del self.bausteine[baustein_name]

    def filter_trace(self,trace: list[dict]) -> list[dict]:
        for entry in trace:
            if "locals" in entry and isinstance(entry["locals"], dict):
                entry["locals"] = self.filter_scl_variables(entry["locals"])
        return trace

    def filter_scl_variables(self,locals_dict: dict) -> dict:
        result = {}

        for name, value in locals_dict.items():
            if name.startswith("__"):
                continue
            if callable(value):
                continue

            result[name] = value

        return result

    def reload_mager(self,Veriablen=None):
        """

        :param cod:
        Ist cod True cod wird neue von SCL in python übersetzt
        :return:
        """
        if Veriablen == None:
             self.python_code ,self.zeilen_offset =Baustein_ausführen.python_code_erstellen(self.bausteine,self.baustein_name)
        else:
            self.python_code, self.zeilen_offset = Baustein_ausführen.python_code_erstellen(self.bausteine,
                                                                                      self.baustein_name,copy.deepcopy( Veriablen))
        trace_ungefiltert = Baustein_ausführen.ausführen(self.python_code)
        self.Baustein = self.bausteine[self.baustein_name]
        self.trace = self.filter_trace(trace_ungefiltert)

        for index,line in enumerate(self.trace):
            if line["line"]== self.zeilen_offset:
                self.current_step = index
                break

    def inBaustein_sprinegn(self, treas:list[dict[str,dict[str,str]]], step:int, target_baustein:str):
        """

        :param treas:
        :param step:
        :param name: Des Aufgerufne Baustein
        :return:
        """

        Veriablen = []
        Veriabeln_zuordung:dict[str,str] =self.Baustein.Veriabeln_zuordung[self.get_scl_line()]
        trace_sep:dict[str,str] = self.trace[step]["locals"] # Verieabeln mit werte aus den treases Schriet
        for key in self.bausteine[target_baustein].Veriablen_reinfolge_in:
            print(Veriabeln_zuordung[key])
            Veriablen.append(trace_sep[Veriabeln_zuordung[key]])
        self.aufruf_liste.append( Baustein_aufrufe( copy.deepcopy(treas), step,self.baustein_name,self.zeilen_offset)
                     )
        print(Veriablen)
        self.baustein_name = target_baustein

        self.reload_mager(Veriablen)

    def ausBausteinspringen(self):
        if self.aufruf_liste:
            temp =self.aufruf_liste.pop(len(self.aufruf_liste)-1)
            self.trace = temp.treas
            self.current_step = temp.current_step
            if self.current_step < len(self.trace) -1:
                self.current_step += 1
            self.baustein_name = temp.baustein_name
            self.zeilen_offset = temp.zeilen_offset

    def step_forward(self):

        if self.current_step < len(self.trace) -1:
            aufruf = self.bausteine[self.baustein_name].Baustein_aufrufe.get(self.get_scl_line())
            if aufruf != None:
                self.inBaustein_sprinegn(self.trace, self.current_step,aufruf)

            self.current_step += 1
        else:
            self.ausBausteinspringen()

    def step_back(self):
        if self.current_step >  self.zeilen_offset:
            self.current_step -= 1

        else:
            self.ausBausteinspringen()

    def get_SCL_text(self)->str:
        return self.bausteine[self.baustein_name].SCL_text


    def get_scl_line(self)->int:
        step = self.trace[self.current_step]["line"] -1
        scl_line = step - self.zeilen_offset
        return scl_line

    def get_trace_step(self)->dict[str,int]:
        """

        :return: gibt die Veriablen aus den akulen schriet
        """
        return copy.deepcopy(self.trace[self.current_step]["locals"])

    def get_python_line(self) -> int:
        """Aktuelle Python-Zeile zum Highlight."""
        step = self.trace[self.current_step]["line"] - 1
        scl_line = step
        return scl_line

    def get_Python_text(self) -> list[str]:
        """Gibt die gesamte generierte Python-Version der Runtime-SCL zurück."""
        return self.python_code

    def to_next_point(self,breakpoints):

        while self.current_step < len(self.trace) -1:

            self.current_step += 1
            line = self.get_scl_line() + 1

            if line in breakpoints:
                break



