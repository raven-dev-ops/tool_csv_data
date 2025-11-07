#!/usr/bin/env python3
"""
MamboLite GUI - Tiny Tkinter wrapper for the CLI processor
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

from mambo_lite import process, resource_path


def default_output_path() -> str:
    """Return a safe default output path in the user's profile.

    Prefer Documents, then Downloads, finally the home directory.
    """
    home = os.path.expanduser("~")
    for folder in ("Documents", "Downloads"):
        candidate_dir = os.path.join(home, folder)
        if os.path.isdir(candidate_dir):
            return os.path.join(candidate_dir, "formatted_contacts.csv")
    return os.path.join(home, "formatted_contacts.csv")


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
        self.geometry("820x560")

        # Prefer a modern ttk theme if available
        try:
            style = ttk.Style(self)
            if "vista" in style.theme_names():
                style.theme_use("vista")
            elif "clam" in style.theme_names():
                style.theme_use("clam")
        except Exception:
            pass

        # Variables
        self.var_input = tk.StringVar()
        self.var_output = tk.StringVar(value=default_output_path())
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
        pad_out = {"padx": 10, "pady": 8}
        pad_in = {"padx": 6, "pady": 4}

        # Files section
        files = ttk.LabelFrame(self, text="Files")
        files.grid(row=0, column=0, sticky="nsew", **pad_out)
        files.columnconfigure(1, weight=1)

        ttk.Label(files, text="Input CSV").grid(row=0, column=0, sticky="e", **pad_in)
        self.entry_input = ttk.Entry(files, textvariable=self.var_input)
        self.entry_input.grid(row=0, column=1, sticky="ew", **pad_in)
        self.btn_input = ttk.Button(files, text="Browse", command=self.browse_input, width=10)
        self.btn_input.grid(row=0, column=2, **pad_in)

        ttk.Label(files, text="Output CSV").grid(row=1, column=0, sticky="e", **pad_in)
        self.entry_output = ttk.Entry(files, textvariable=self.var_output)
        self.entry_output.grid(row=1, column=1, sticky="ew", **pad_in)
        self.btn_output = ttk.Button(files, text="Browse", command=self.browse_output, width=10)
        self.btn_output.grid(row=1, column=2, **pad_in)

        ttk.Label(files, text="Lookups folder").grid(row=2, column=0, sticky="e", **pad_in)
        self.entry_lookups = ttk.Entry(files, textvariable=self.var_lookups)
        self.entry_lookups.grid(row=2, column=1, sticky="ew", **pad_in)
        self.btn_lookups = ttk.Button(files, text="Browse", command=self.browse_lookups, width=10)
        self.btn_lookups.grid(row=2, column=2, **pad_in)

        # Options section
        opts = ttk.LabelFrame(self, text="Options")
        opts.grid(row=1, column=0, sticky="nsew", **pad_out)
        opts.columnconfigure(1, weight=1)

        ttk.Label(opts, text="Source label").grid(row=0, column=0, sticky="e", **pad_in)
        self.entry_source = ttk.Entry(opts, textvariable=self.var_source, width=30)
        self.entry_source.grid(row=0, column=1, sticky="w", **pad_in)
        self.chk_dedupe = ttk.Checkbutton(opts, text="Deduplicate by email", variable=self.var_dedupe)
        self.chk_dedupe.grid(row=0, column=2, sticky="w", **pad_in)

        # Email section
        email = ttk.LabelFrame(self, text="Email (optional)")
        email.grid(row=2, column=0, sticky="nsew", **pad_out)
        email.columnconfigure(1, weight=1)

        self.chk_send_email = ttk.Checkbutton(email, text="Send result via email", variable=self.var_send_email, command=self._toggle_email)
        self.chk_send_email.grid(row=0, column=0, sticky="w", **pad_in)
        ttk.Label(email, text="Recipient").grid(row=0, column=1, sticky="e", **pad_in)
        self.entry_recipient = ttk.Entry(email, textvariable=self.var_recipient, width=32)
        self.entry_recipient.grid(row=0, column=2, sticky="w", **pad_in)

        ttk.Label(email, text="Method").grid(row=1, column=0, sticky="e", **pad_in)
        self.method_frame = ttk.Frame(email)
        self.method_frame.grid(row=1, column=1, columnspan=2, sticky="w", **pad_in)
        self.rb_smtp = ttk.Radiobutton(self.method_frame, text="SMTP", variable=self.var_email_method, value="smtp", command=self._toggle_email)
        self.rb_smtp.pack(side=tk.LEFT, padx=(0, 12))
        self.rb_outlook = ttk.Radiobutton(self.method_frame, text="Outlook", variable=self.var_email_method, value="outlook", command=self._toggle_email)
        self.rb_outlook.pack(side=tk.LEFT)

        ttk.Label(email, text="SMTP JSON").grid(row=2, column=0, sticky="e", **pad_in)
        self.entry_smtp = ttk.Entry(email, textvariable=self.var_smtp)
        self.entry_smtp.grid(row=2, column=1, sticky="ew", **pad_in)
        self.btn_smtp = ttk.Button(email, text="Browse", command=self.browse_smtp, width=10)
        self.btn_smtp.grid(row=2, column=2, **pad_in)

        # Log section
        logf = ttk.LabelFrame(self, text="Log")
        logf.grid(row=3, column=0, sticky="nsew", **pad_out)
        logf.columnconfigure(0, weight=1)
        logf.rowconfigure(0, weight=1)
        self.log_widget = ScrolledText(logf, height=14, state=tk.DISABLED)
        self.log_widget.grid(row=0, column=0, sticky="nsew", **pad_in)

        # Run button (bottom right)
        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, sticky="e", **pad_out)
        self.btn_run = ttk.Button(actions, text="Run", command=self.on_run, width=16)
        self.btn_run.grid(row=0, column=0, sticky="e")

        # Top-level resize rules
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._toggle_email()

    def _set_state(self, widget, enabled: bool) -> None:
        try:
            # ttk widgets
            if enabled:
                widget.state(["!disabled"])
            else:
                widget.state(["disabled"])
        except Exception:
            # classic tkinter widgets
            widget.configure(state=(tk.NORMAL if enabled else tk.DISABLED))

    def _toggle_email(self):
        sending = self.var_send_email.get()
        self._set_state(self.rb_smtp, sending)
        self._set_state(self.rb_outlook, sending)
        self._set_state(self.entry_recipient, sending)

        smtp_enabled = sending and self.var_email_method.get() == "smtp"
        self._set_state(self.entry_smtp, smtp_enabled)
        self._set_state(self.btn_smtp, smtp_enabled)

    def _validate_or_prompt_output(self, path):
        """Ensure output path is absolute and writable.

        If not, prompt the user with a Save As dialog. Returns the
        validated path or None if the user cancels.
        """
        # Expand env vars and ~
        p = os.path.expandvars(os.path.expanduser(path or ""))

        need_prompt = False
        if not p or not os.path.isabs(p):
            need_prompt = True
        else:
            out_dir = os.path.dirname(os.path.abspath(p)) or os.getcwd()
            if not os.path.isdir(out_dir) or not os.access(out_dir, os.W_OK):
                need_prompt = True

        if need_prompt:
            dflt = default_output_path()
            sel = filedialog.asksaveasfilename(
                initialdir=os.path.dirname(dflt),
                initialfile=os.path.basename(dflt),
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
            if not sel:
                return None
            self.var_output.set(sel)
            return sel
        return p

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

        # Ensure output path is absolute and writable; otherwise prompt the user
        validated_output = self._validate_or_prompt_output(output_path)
        if not validated_output:
            return
        output_path = validated_output

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
