import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import copy
import Baustein_manager

class SCLDebuggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SCL Step Debugger")

        # -------------------------------------------------
        # SCL laden
        # -------------------------------------------------
        with open("text", "r", encoding="utf-8") as f:
            full_scl = f.read().splitlines()

        # nur Runtime-SCL anzeigen
        self.manager = Baustein_manager.mager()
        self.manager.Baustein_hinzufügen(full_scl)
        # -------------------------------------------------
        # Layout
        # -------------------------------------------------
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        code_frame = ttk.Frame(main_frame)
        code_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        var_frame = ttk.Frame(main_frame, width=260)
        var_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # -------------------------------------------------
        # Codefenster (SCL)
        # -------------------------------------------------
        self.text = tk.Text(
            code_frame,
            width=90,
            height=30,
            font=("Consolas", 11),
            state=tk.NORMAL
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(code_frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        self.text.tag_config("current", background="#ffe066")


        self.text.config(state=tk.DISABLED)

        # -------------------------------------------------
        # Variablenanzeige
        # -------------------------------------------------
        ttk.Label(
            var_frame,
            text="Variablen",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.var_list = tk.Listbox(
            var_frame,
            width=35,
            height=25,
            font=("Consolas", 10)
        )
        self.var_list.pack(fill=tk.BOTH, padx=5, expand=True)



        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------
        btn_frame = ttk.Frame(root)
        btn_frame.pack(side=tk.BOTTOM, pady=6)

        ttk.Button(btn_frame, text="<< Rückwärts", command=self.step_back)\
            .pack(side=tk.LEFT, padx=6)

        ttk.Button(btn_frame, text="Vorwärts >>", command=self.step_forward)\
            .pack(side=tk.LEFT, padx=6)

        ttk.Button(
            btn_frame,
            text="Variablen ändern",
            command=self.open_variable_editor
        ).pack(side=tk.LEFT, padx=6)


        ttk.Button(
            btn_frame,
            text="Bausteine verwalten",
            command=self.open_baustein_manager
        ).pack(side=tk.LEFT, padx=6)

        # Statuszeile
        # -------------------------------------------------
        # Initialanzeige
        self.status_label = ttk.Label(
            root,
            text="Zeile: -",
            anchor="w",
            font=("Consolas", 10)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=6)

        self.reload_debugger()
        self.aufruf_liste = []
    # -------------------------------------------------
    # Anzeige
    # -------------------------------------------------
    def highlight_line(self):

        self.text.config(state=tk.NORMAL)
        self.text.tag_remove("current", "1.0", tk.END)

        # Python-Zeile → Runtime-SCL-Zeile

        scl_line = self.manager.get_scl_line() + 1
        start = f"{scl_line }.0"
        end = f"{scl_line }.end"
        self.text.tag_add("current", start, end)
        self.text.see(start)

        self.text.config(state=tk.DISABLED)
        self.status_label.config(
            text=f"Zeile: {scl_line}   (Trace-Step: {self.manager.current_step})"
        )

    def update_variables(self):
        self.var_list.delete(0, tk.END)

        locals_ = self.manager.get_trace_step()
        for name, value in sorted(locals_.items()):
            self.var_list.insert(tk.END, f"{name} = {value}")

    # -------------------------------------------------
    # Steuerung
    # -------------------------------------------------
    def step_forward(self):
        self.manager.step_forward()

        self.update_variables()
        self.update_code_view() #später verlicht verbsseren
        self.highlight_line()

    def step_back(self):
        self.manager.step_back()

        self.update_variables()
        self.update_code_view()#später verlicht verbsseren
        self.highlight_line()

    def reload_debugger(self,Veriablen=None):
        """

        :param cod:
        Ist cod True cod wird neue von SCL in python übersetzt
        :return:
        """
        self.manager.reload_mager(Veriablen)
        # nur Runtime-SCL anzeigen

        self.update_code_view()
        self.highlight_line()
        self.update_variables()




    def update_code_view(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "\n".join(self.manager.get_SCL_text()))
        self.text.config(state=tk.DISABLED)

    def open_variable_editor(self):
        win = tk.Toplevel(self.root)
        win.title("Initialwerte ändern")

        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.var_entries = {}  # (scope, name) -> Entry

        baustein = self.manager.Baustein_ausgabe()

        for scope, vars_ in baustein.Veriablen.items():
            if not vars_:
                continue

            # Scope-Überschrift
            ttk.Label(
                frame,
                text=f"[{scope}]",
                font=("Arial", 9, "bold")
            ).pack(anchor="w", pady=(6, 2))

            for name, value in vars_.items():
                row = ttk.Frame(frame)
                row.pack(fill=tk.X, pady=1)

                ttk.Label(row, text=name, width=18).pack(side=tk.LEFT)
                entry = ttk.Entry(row)
                entry.insert(0, value)
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

                self.var_entries[(scope, name)] = entry

        ttk.Button(
            win,
            text="Neu starten",
            command=lambda: self.apply_initial_values(win)
        ).pack(pady=8)

    def apply_initial_values(self, win):
        bs = self.manager.Baustein_ausgabe()

        for (scope, name), entry in self.var_entries.items():
            bs.Veriablen[scope][name] = entry.get()

        win.destroy()
        self.reload_debugger()

    def open_baustein_manager(self):
        win = tk.Toplevel(self.root)
        win.title("Bausteine verwalten")
        win.geometry("420x300")

        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # -------------------------------------------------
        # Bausteinliste
        # -------------------------------------------------
        ttk.Label(frame, text="Vorhandene Bausteine").pack(anchor="w")

        self.baustein_listbox = tk.Listbox(
            frame,
            height=10,
            font=("Consolas", 10)
        )
        self.baustein_listbox.pack(fill=tk.BOTH, expand=True, pady=4)

        self.update_baustein_list()

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=6)

        ttk.Button(
            btn_frame,
            text="Baustein hinzufügen",
            command=self.add_baustein_dialog
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            btn_frame,
            text="Öffnen",
            command=self.open_selected_baustein
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            btn_frame,
            text="Entfernen",
            command=self.remove_selected_baustein
        ).pack(side=tk.RIGHT, padx=4)

    def update_baustein_list(self):
        self.baustein_listbox.delete(0, tk.END)
        for name, bs in self.manager.bausteine.items():
            self.baustein_listbox.insert(
                tk.END,
                f"{bs.typ} {name}"
            )

    def add_baustein_dialog(self,):
        path = filedialog.askopenfilename(
            filetypes=[("SCL Dateien", "*.scl *.txt")]
        )
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            text:list[str] =  f.read().splitlines()
        self.manager.Baustein_hinzufügen(text)

        self.update_baustein_list()

    def open_selected_baustein(self):
            sel = self.baustein_listbox.curselection()
            if not sel:
                return

            text = self.baustein_listbox.get(sel[0])
            name = text.split()[-1]
            self.manager.open_selected_baustein(name)
            self.reload_debugger()

    def remove_selected_baustein(self):
        sel = self.baustein_listbox.curselection()
        if not sel:
            return

        text = self.baustein_listbox.get(sel[0])
        name = text.split()[-1]

        self.manager.remove_selected_baustein(name)
        self.update_baustein_list()


# -------------------------------------------------
# Start
# -------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SCLDebuggerGUI(root)
    root.mainloop()
