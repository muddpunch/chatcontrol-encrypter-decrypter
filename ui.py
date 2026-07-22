from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = Path(__file__).with_name("key.txt")

def main () -> None:
    root = tk.Tk()
    root.title("Anti Chat-Control Encrypter/Decrypter")
    root.geometry("650x500")
    root.minsize(500, 400)

    frame = ttk.Frame(root, padding=16)
    frame.grid(sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(2, weight=1)
    frame.rowconfigure(5, weight=1)
    status = tk.StringVar(value="Ready")
    def load_cipher() -> Fernet | None:
        try:
            return Fernet(KEY_FILE.read_bytes().strip())
        except FileNotFoundError:
            messagebox.showerror("Key error", "Generate a key first.")
        except ValueError:
            messagebox.showerror("Key error", "key.txt contains an invalid key.")
        return None
    def generate_key() -> None:
        if KEY_FILE.exists() and KEY_FILE.stat().st_size:
            confirmed = messagebox.askyesno(
                "Replace key?",
                "Old messages cannot be decrypted after replacing the key.",
            )
            if not confirmed:
                return
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        key_text = key.decode("ascii")
        set_output(key_text)
        status.set(f"New key generated! {key_text}")
    def set_output(value: str) -> None:
        output_box.delete("1.0", tk.END)
        output_box.insert("1.0", value)
    def encrypt() -> None:
        message = input_box.get("1.0", "end-1c")
        if not message:
            messagebox.showwarning("Empty message", "Enter a message.")
            return
        cipher = load_cipher()
        if cipher is None:
            return
        encrypted = cipher.encrypt(message.encode("utf-8")).decode("ascii")
        set_output(encrypted)
        status.set("Message encrypted")
    def decrypt() -> None:
        encrypted = input_box.get("1.0", "end-1c").strip()
        if not encrypted:
            messagebox.showwarning("Empty message", "Enter an encrypted message.")
            return
        cipher = load_cipher()
        if cipher is None:
            return
        try:
            decrypted = cipher.decrypt(encrypted.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError):
            messagebox.showerror(
                "Decryption failed",
                "Invalid message or incorrect key.",
            )
            return
        set_output(decrypted)
        status.set("Message decrypted")
    def copy_output() -> None:
        value = output_box.get("1.0", "end-1c")
        if not value:
            return
        root.clipboard_clear()
        root.clipboard_append(value)
        status.set("Output copied")
    key_var = tk.StringVar()
    def import_key() -> None:
        raw = key_var.get().strip()
        if not raw:
            try:
                raw = root.clipboard_get().strip()
                key_var.set(raw)
            except tk.TclError:
                messagebox.showwarning("Empty key", "Paste or enter a key.")
                return
        try:
            key = raw.encode("ascii")
            Fernet(key) #Key vali
        except (UnicodeEncodeError, ValueError):
            messagebox.showerror("Key error", "Invalid Fernet key.")
            return
        old_key = KEY_FILE.read_bytes().strip() if KEY_FILE.exists() else b""
        if old_key and old_key != key and not messagebox.askyesno(
            "Replace key?",
            "Replace the current key with the custom key?",
        ):
            return
        KEY_FILE.write_bytes(key)
        status.set("Key saved to key.txt") 
    buttons = ttk.Frame(frame)
    buttons.grid(row=0, column=0, sticky="ew", pady=(0,12))
    buttons.columnconfigure(3, weight=1)
    ttk.Button(
        buttons,
        text="Generate key",
        command=generate_key
    ).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(
        buttons, 
        text="Encrypt", 
        command=encrypt,
    ).grid(row=0, column=1, padx=(0, 8))
    ttk.Button(
        buttons, 
        text="Decrypt", 
        command=decrypt
    ).grid(row=0, column=2, padx=(0, 8))
    ttk.Entry(
        buttons,
        textvariable=key_var,
        width=28,
    ).grid(row=0, column=4, padx=(12, 8), sticky="e")
    ttk.Button(
        buttons,
        text="Paste / save key",
        command=import_key,
    ).grid(row=0, column=5)
    ttk.Label(frame, text ="Input").grid (row=1, column=0, sticky="w")
    input_box = tk.Text(frame, height=8, wrap="word")
    input_box.grid(row=2, column=0, sticky="nsew", pady=(4, 12))
    output_header = ttk.Frame(frame)
    output_header.grid(row=3, column=0, sticky="ew")
    output_header.columnconfigure(0, weight=1)

    ttk.Label(output_header, text="Output").grid(
          row=0,
          column=0,
          sticky="w",
      )

    ttk.Button(
          output_header,
          text="Copy",
          command=copy_output,
      ).grid(row=0, column=1)

    output_box = tk.Text(frame, height=8, wrap="word")
    output_box.grid(
          row=5,
          column=0,
          sticky="nsew",
          pady=(4, 12),
      )

    ttk.Label(frame, textvariable=status).grid(
          row=6,
          column=0,
          sticky="w",
      )

    input_box.focus()
    root.mainloop()
if __name__ == "__main__":
    main()