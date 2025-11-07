#!/usr/bin/env python3
"""
MamboLite GUI - Tiny Tkinter wrapper for the CLI processor
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from mambo_lite import process, resource_path


class TextLogger:
    def __init__(self, widget: ScrolledText):
        self.widget = widget

    def write(self, msg: str):
        self.widget.configure(state=tk.NORMAL)
        self.widget.insert(tk.END, msg + "\n")
        self.widget.see(tk.END)
        self.widget.configure(state=tk.DISABLED)

    def flush(self):
        pass


class MamboLiteGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MamboLite - Single CSV Contact Formatter")
        self.geometry("760x520")

        # Variables
        self.var_input = tk.StringVar()
        self.var_output = tk.StringVar(value="formatted_contacts.csv")
        default_lookups = resource_path("lookups")
        self.var_lookups = tk.StringVar(value=default_lookups)
        self.var_source = tk.StringVar(value="")
        self.var_dedupe = tk.BooleanVar(value=True)
        self.var_send_email = tk.BooleanVar(value=False)
        self.var_email_method = tk.StringVar(value="smtp")
        self.var_recipient = tk.StringVar(value="")
        self.var_smtp = tk.StringVar(value=resource_path("smtp.json.example"))

        self._build_form()

    def _build_form(self):
        pad = {"padx": 8, "pady": 6}

        # Row 0: Input
        tk.Label(self, text="Input CSV").grid(row=0, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.var_input, width=70).grid(row=0, column=1, sticky="we", **pad)
        tk.Button(self, text="Browse", command=self.browse_input).grid(row=0, column=2, **pad)

        # Row 1: Output
        tk.Label(self, text="Output CSV").grid(row=1, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.var_output, width=70).grid(row=1, column=1, sticky="we", **pad)
        tk.Button(self, text="Browse", command=self.browse_output).grid(row=1, column=2, **pad)

        # Row 2: Lookups
        tk.Label(self, text="Lookups folder").grid(row=2, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.var_lookups, width=70).grid(row=2, column=1, sticky="we", **pad)
        tk.Button(self, text="Browse", command=self.browse_lookups).grid(row=2, column=2, **pad)

        # Row 3: Source label
        tk.Label(self, text="Source label").grid(row=3, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.var_source, width=30).grid(row=3, column=1, sticky="w", **pad)
        tk.Checkbutton(self, text="Deduplicate by email", variable=self.var_dedupe).grid(row=3, column=2, sticky="w", **pad)

        # Row 4: Email options
        self.chk_send_email = tk.Checkbutton(self, text="Send result via email", variable=self.var_send_email, command=self._toggle_email)
        self.chk_send_email.grid(row=4, column=0, sticky="e", **pad)
        self.method_frame = tk.Frame(self)
        self.method_frame.grid(row=4, column=1, sticky="w", **pad)
        self.rb_smtp = tk.Radiobutton(self.method_frame, text="SMTP", variable=self.var_email_method, value="smtp", command=self._toggle_email)
        self.rb_smtp.pack(side=tk.LEFT)
        self.rb_outlook = tk.Radiobutton(self.method_frame, text="Outlook", variable=self.var_email_method, value="outlook", command=self._toggle_email)
        self.rb_outlook.pack(side=tk.LEFT)
        self.entry_recipient = tk.Entry(self, textvariable=self.var_recipient, width=30)
        self.entry_recipient.grid(row=4, column=2, sticky="w", **pad)

        # Row 5: SMTP JSON (only for SMTP)
        self.lbl_smtp = tk.Label(self, text="SMTP JSON")
        self.lbl_smtp.grid(row=5, column=0, sticky="e", **pad)
        self.entry_smtp = tk.Entry(self, textvariable=self.var_smtp, width=70)
        self.entry_smtp.grid(row=5, column=1, sticky="we", **pad)
        self.btn_smtp = tk.Button(self, text="Browse", command=self.browse_smtp)
        self.btn_smtp.grid(row=5, column=2, **pad)

        # Row 6: Log area
        tk.Label(self, text="Log").grid(row=6, column=0, sticky="ne", **pad)
        self.log_widget = ScrolledText(self, height=16, width=100, state=tk.DISABLED)
        self.log_widget.grid(row=6, column=1, columnspan=2, sticky="nsew", **pad)

        # Row 7: Run button
        tk.Button(self, text="Run", command=self.on_run, width=16).grid(row=7, column=2, sticky="e", **pad)

        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._toggle_email()

    def _toggle_email(self):
        sending = self.var_send_email.get()
        state = tk.NORMAL if sending else tk.DISABLED
        # Enable/disable only widgets that support 'state'
        self.rb_smtp.configure(state=state)
        self.rb_outlook.configure(state=state)
        self.entry_recipient.configure(state=state)

        # SMTP controls only when SMTP selected
        smtp_enabled = sending and self.var_email_method.get() == "smtp"
        smtp_state = tk.NORMAL if smtp_enabled else tk.DISABLED
        self.entry_smtp.configure(state=smtp_state)
        self.btn_smtp.configure(state=smtp_state)

    def browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self.var_input.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            self.var_output.set(path)

    def browse_lookups(self):
        path = filedialog.askdirectory()
        if path:
            self.var_lookups.set(path)

    def browse_smtp(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if path:
            self.var_smtp.set(path)

    def on_run(self):
        input_path = self.var_input.get().strip()
        output_path = self.var_output.get().strip()
        lookups_dir = self.var_lookups.get().strip()
        source = self.var_source.get().strip()
        dedupe = self.var_dedupe.get()
        send_email = self.var_send_email.get()
        email_method = self.var_email_method.get()
        recipient = self.var_recipient.get().strip() if send_email else None
        smtp_path = self.var_smtp.get().strip() if (send_email and email_method == "smtp") else None

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please choose a valid input CSV file.")
            return
        if not lookups_dir or not os.path.isdir(lookups_dir):
            messagebox.showerror("Error", "Please choose a valid lookups folder.")
            return
        if send_email:
            if not recipient:
                messagebox.showerror("Error", "Please provide a recipient email address.")
                return
            if email_method == "smtp":
                if not smtp_path or not os.path.exists(smtp_path):
                    messagebox.showerror("Error", "Please choose a valid SMTP JSON file.")
                    return

        logger = TextLogger(self.log_widget)
        self.log_widget.configure(state=tk.NORMAL)
        self.log_widget.delete("1.0", tk.END)
        self.log_widget.configure(state=tk.DISABLED)

        def worker():
            try:
                out = process(
                    input_path=input_path,
                    lookups_dir=lookups_dir,
                    output_path=output_path,
                    source_label=source,
                    dedupe_email=dedupe,
                    email_to=recipient,
                    smtp_config_path=smtp_path,
                    email_method=email_method,
                    logger=logger,
                )
                messagebox.showinfo("Success", f"Finished. Output saved to:\n{out}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = MamboLiteGUI()
    app.mainloop()
