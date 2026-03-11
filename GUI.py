import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import Baustein_manager

class LineNumbers(tk.Canvas):

    def __init__(self, parent, textwidget):
        super().__init__(parent, width=50)
        self.textwidget = textwidget
        self.breakpoints = set()

    def redraw(self):

        self.delete("all")

        i = self.textwidget.index("@0,0")

        while True:

            dline = self.textwidget.dlineinfo(i)

            if dline is None:
                i = self.textwidget.index(f"{i}+1line")
                if i == self.textwidget.index("end"):
                    break
                continue

            y = dline[1]
            linenum = int(str(i).split(".")[0])

            # Breakpoint-Kreis
            if linenum in self.breakpoints:
                self.create_oval(
                    5,
                    y + 2,
                    15,
                    y + 12,
                    fill="red",
                    outline=""
                )

            # Zeilennummer
            self.create_text(
                40,
                y,
                anchor="ne",
                text=str(linenum),
                fill="black"
            )

            i = self.textwidget.index(f"{i}+1line")

class SCLDebuggerGUI:
    def sync_scroll(self, *args):
        self.text.yview(*args)
        self.text_python.yview(*args)

    def on_mousewheel(self, event):

        self.text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.text_python.yview_scroll(int(-1 * (event.delta / 120)), "units")

        return "break"

    def __init__(self, root):
        self.root = root
        self.root.title("SCL Step Debugger")

        # -------------------------------------------------
        # SCL laden
        # -------------------------------------------------
        with open("text", "r", encoding="utf-8") as f:
            full_scl = f.read().splitlines()

        self.manager = Baustein_manager.mager()
        self.manager.Baustein_hinzufügen(full_scl)
        self.breakpoints = set()  # z.B. {3, 7, 12}

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
        self.scl_frame = ttk.Frame(code_frame)
        self.scl_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(
            self.scl_frame,
            text="SCL Code",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        scl_inner = ttk.Frame(self.scl_frame)
        scl_inner.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = LineNumbers(scl_inner, None)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)


        self.line_numbers.bind("<Button-1>", self.toggle_breakpoint)

        self.text = tk.Text(
            scl_inner,
            font=("Consolas", 11)
        )

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.line_numbers.textwidget = self.text
        self.scrollbar = ttk.Scrollbar(
            scl_inner,
            command=self.text.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(yscrollcommand=self.scrollbar.set)
        self.text.bind("<KeyRelease>", lambda e: self.line_numbers.redraw())
        self.text.bind("<MouseWheel>", lambda e: self.line_numbers.redraw())
        self.text.bind("<Button-1>", lambda e: self.line_numbers.redraw())

        self.text.tag_config("current", background="#ffe066")  # ← hinzufügen

        self.text.tag_config("breakpoint", background="red")
        # -------------------------------------------------
        # Codefenster (python)
        # -------------------------------------------------
        self.python_frame = ttk.Frame(code_frame)
        self.python_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(
            self.python_frame,
            text="Python Code",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        py_inner = ttk.Frame(self.python_frame)
        py_inner.pack(fill=tk.BOTH, expand=True)

        self.text_python = tk.Text(
            py_inner,
            font=("Consolas", 11)
        )
        self.text_python.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        self.text_python.tag_config("current", background="#c6f5ff")

        #scrollbar

        self.scrollbar_py = ttk.Scrollbar(
            py_inner,
            command=self.text_python.yview
        )
        self.scrollbar_py.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_python.config(yscrollcommand=self.scrollbar_py.set)

        self.scrollbar.config(command=self.sync_scroll)
        self.scrollbar_py.config(command=self.sync_scroll)

        self.text.bind("<MouseWheel>", self.on_mousewheel)
        self.text_python.bind("<MouseWheel>", self.on_mousewheel)

        self.text.bind("<KeyRelease>", lambda e: self.line_numbers.redraw())
        self.text.bind("<MouseWheel>", lambda e: self.line_numbers.redraw())
        self.text.bind("<Button-1>", lambda e: self.line_numbers.redraw())

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
            font=("Consolas", 11)
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

        ttk.Button(btn_frame, text="zum-Punkt |->", command=self.to_next_point)\
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

        self.show_python = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            btn_frame,
            text="Python anzeigen",
            variable=self.show_python,
            command=self.toggle_python
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
        self.root.after_idle(self.line_numbers.redraw)

    # -------------------------------------------------
    # Anzeige
    # -------------------------------------------------
    def highlight_line(self):

        # -------- SCL --------
        self.text.config(state=tk.NORMAL)
        self.text.tag_remove("current", "1.0", tk.END)

        scl_line = self.manager.get_scl_line() + 1
        start = f"{scl_line}.0"
        end = f"{scl_line}.end"

        self.text.tag_add("current", start, end)
        self.text.see(start)
        self.text.config(state=tk.DISABLED)

        # -------- Python --------
        self.text_python.config(state=tk.NORMAL)
        self.text_python.tag_remove("current", "1.0", tk.END)

        py_line = self.manager.get_python_line() + 1
        start = f"{py_line}.0"
        end = f"{py_line}.end"

        self.text_python.tag_add("current", start, end)
        self.text_python.see(start)
        self.text_python.config(state=tk.DISABLED)

        self.status_label.config(
            text=f"SCL: {scl_line}  Python: {py_line}  (Trace-Step: {self.manager.current_step})"
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

    def to_next_point(self):
        self.manager.to_next_point(self.line_numbers.breakpoints)

        self.update_variables()
        self.update_code_view()
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
        self.root.after_idle(self.line_numbers.redraw)




    def update_code_view(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "\n".join(self.manager.get_SCL_text()))
        self.text.config(state=tk.DISABLED)
        #python
        self.text_python.config(state=tk.NORMAL)
        self.text_python.delete("1.0", tk.END)
        self.text_python.insert(tk.END, "".join(self.manager.get_Python_text()))
        self.text_python.config(state=tk.DISABLED)


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

    def toggle_python(self):

        if self.show_python.get():
            self.python_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        else:
            self.python_frame.pack_forget()

    def toggle_breakpoint(self, event):

        index = self.text.index(f"@0,{event.y}")
        line = int(index.split(".")[0])

        if line in self.line_numbers.breakpoints:
            self.line_numbers.breakpoints.remove(line)
        else:
            self.line_numbers.breakpoints.add(line)

        self.line_numbers.redraw()

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
