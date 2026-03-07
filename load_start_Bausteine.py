from baustein_erstellen import Baustein
def load_start_Bausteine(FBs:{}) -> None:
    FBs["R_TRIG"] = Baustein("R_TRIG", [
        "Q = CLK and not S", "S = CLK"],
                                  {"input": {"CLK": "False"}, "output": {"Q": "False"}, "var": {"S": "False"}},
                                  ["CLK"],
                                  ["Q"],
                                  "FB",
                                  [],
                                  3,
                                  "Kein SCL cod",
                                  True,
                                  {},
                                  {})

    FBs["F_TRIG"] = Baustein(
        "F_TRIG",
        ["Q = (not CLK) and S", "S = CLK"],
        {"input": {"CLK": "False"},
         "output": {"Q": "False"},
         "var": {"S": "False"}
         },
        ["CLK"],
        ["Q"],
        "FB",
        [],
        0,
        "Kein SCL code",
        True,
        {},
        {}
    )

    FBs["TP"] = Baustein(
        "TP",
        [
            "start = IN and not S",
            "S = IN",
            "",
            "if start:",
            "    RUN = True",
            "    ET = 0",
            "",
            "if RUN:",
            "    ET = ET + 1",
            "    if ET >= PT:",
            "        RUN = False",
            "",
            "Q = RUN"
        ],
        {
            "input": {
                "IN": "False",
                "PT": "0"
            },
            "output": {
                "Q": "False"
            },
            "var": {
                "S": "False",
                "RUN": "False",
                "ET": "0"
            }
        },
        ["IN", "PT"],
        ["Q"],
        "FB",
        [],
        5,
        "Kein SCL cod",
        True,
        {},
        {}
    )
    FBs["CTU"] = Baustein(
        "CTU",
        [
            "if R:",
            "    CV = 0",
            "",
            "edge = CU and not S",
            "S = CU",
            "",
            "if edge:",
            "    CV = CV + 1",
            "",
            "Q = CV >= PV"
        ],
        {
            "input": {
                "CU": "False",
                "R": "False",
                "PV": "0"
            },
            "output": {
                "Q": "False",
                "CV": "0"
            },
            "var": {
                "S": "False"
            }
        },
        ["CU", "R", "PV"],
        ["Q", "CV"],
        "FB",
        [],
        3,
        "Kein SCL cod",
        True,
        {},
        {}
    )
    FBs["CTD"] = Baustein(
        "CTD",
        [
            "if LD:",
            "    CV = PV",
            "",
            "edge = CD and not S",
            "S = CD",
            "",
            "if edge:",
            "    CV = CV - 1",
            "",
            "Q = CV <= 0"
        ],
        {
            "input": {
                "CD": "False",
                "LD": "False",
                "PV": "0"
            },
            "output": {
                "Q": "False",
                "CV": "0"
            },
            "var": {
                "S": "False"
            }
        },
        ["CD", "LD", "PV"],
        ["Q", "CV"],
        "FB",
        [],
        3,
        "Kein SCL cod",
        True,
        {},
        {}
    )
    FBs["CTUD"] = Baustein(
        "CTUD",
        [
            "if R:",
            "    CV = 0",
            "",
            "if LD:",
            "    CV = PV",
            "",
            "edgeU = CU and not SU",
            "SU = CU",
            "",
            "edgeD = CD and not SD",
            "SD = CD",
            "",
            "if edgeU:",
            "    CV = CV + 1",
            "",
            "if edgeD:",
            "    CV = CV - 1",
            "",
            "QU = CV >= PV",
            "QD = CV <= 0"
        ],
        {
            "input": {
                "CU": "False",
                "CD": "False",
                "R": "False",
                "LD": "False",
                "PV": "0"
            },
            "output": {
                "QU": "False",
                "QD": "False",
                "CV": "0"
            },
            "var": {
                "SU": "False",
                "SD": "False"
            }
        },
        ["CU", "CD", "R", "LD", "PV"],
        ["QU", "QD", "CV"],
        "FB",
        [],
        4,
        "Kein SCL cod",
        True,
        {},
        {}
    )


    return FBs