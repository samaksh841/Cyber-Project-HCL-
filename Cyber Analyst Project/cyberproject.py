"""
64 bit encoder/decoder  -  GUI version (Base64)
Author : Samaksh Sharma

A simple desktop window to encode and decode Base64.
Uses only Python's built-in tkinter, so nothing extra to install.

Run:   python base64_gui.py
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------------------------------------------------------------------------
# 1. CORE LOGIC (same algorithm as the console version)
# ---------------------------------------------------------------------------
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
REVERSE = {ch: i for i, ch in enumerate(ALPHABET)}


def encode(data: bytes) -> str:
    out = []
    for i in range(0, len(data), 3):              # 3 bytes at a time
        chunk = data[i:i + 3]
        pad = 3 - len(chunk)                      # missing bytes (0, 1 or 2)
        chunk += b"\x00" * pad
        n = (chunk[0] << 16) | (chunk[1] << 8) | chunk[2]       # 24 bits
        idx = [(n >> 18) & 63, (n >> 12) & 63, (n >> 6) & 63, n & 63]
        chars = [ALPHABET[k] for k in idx]
        if pad:
            chars[4 - pad:] = "=" * pad
        out.append("".join(chars))
    return "".join(out)


def decode(text: str) -> bytes:
    text = "".join(text.split())                  # remove spaces / new lines
    if len(text) % 4 != 0:
        raise ValueError("Invalid length: not a multiple of 4")
    out = bytearray()
    for i in range(0, len(text), 4):              # 4 characters at a time
        block = text[i:i + 4]
        pad = block.count("=")
        if pad > 2 or ("=" in block[:4 - pad]):
            raise ValueError("Invalid padding")
        if pad and i + 4 != len(text):
            raise ValueError("Invalid padding: '=' found before the end")
        n = 0
        for ch in block:
            if ch == "=":
                n <<= 6
            elif ch in REVERSE:
                n = (n << 6) | REVERSE[ch]
            else:
                raise ValueError(f"Invalid character: {ch!r}")
        triple = bytes([(n >> 16) & 255, (n >> 8) & 255, n & 255])
        out += triple[:3 - pad]
    return bytes(out)


# ---------------------------------------------------------------------------
# 2. THE WINDOW
# ---------------------------------------------------------------------------
NAVY = "#1F3A5F"
GOLD = "#C8A24A"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("64 bit encoder/decoder")
        self.geometry("760x640")
        self.minsize(620, 560)
        self.configure(bg="white")

        self._style()
        self._build()

    # ---------- look and feel ----------
    def _style(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure("TFrame", background="white")
        st.configure("TLabel", background="white", font=("Helvetica", 11))
        st.configure("Head.TLabel", font=("Helvetica", 11, "bold"), foreground=NAVY)
        st.configure("TButton", font=("Helvetica", 11), padding=6)
        st.configure("Main.TButton", font=("Helvetica", 12, "bold"),
                     background=NAVY, foreground="white", padding=8)
        st.map("Main.TButton", background=[("active", "#2D5385")])

    # ---------- layout ----------
    def _build(self):
        # Title bar
        top = tk.Frame(self, bg=NAVY)
        top.pack(fill="x")
        tk.Label(top, text="64 bit encoder/decoder", bg=NAVY, fg="white",
                 font=("Helvetica", 20, "bold")).pack(pady=(14, 2))
        tk.Label(top, text="Base64 Encoder and Decoder  |  by Samaksh Sharma",
                 bg=NAVY, fg="#D9E2EF", font=("Helvetica", 10)).pack(pady=(0, 12))
        tk.Frame(self, bg=GOLD, height=3).pack(fill="x")

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)
        body.rowconfigure(4, weight=1)

        # Input box
        ttk.Label(body, text="Input", style="Head.TLabel").grid(row=0, column=0, sticky="w")
        self.inp = self._textbox(body, row=1)

        # Main buttons
        bar = ttk.Frame(body)
        bar.grid(row=2, column=0, pady=10)
        ttk.Button(bar, text="Encode  \u2193", style="Main.TButton",
                   command=self.do_encode).grid(row=0, column=0, padx=6)
        ttk.Button(bar, text="Decode  \u2193", style="Main.TButton",
                   command=self.do_decode).grid(row=0, column=1, padx=6)
        ttk.Button(bar, text="Swap \u21C5", command=self.do_swap).grid(row=0, column=2, padx=6)

        # Output box
        ttk.Label(body, text="Output", style="Head.TLabel").grid(row=3, column=0, sticky="w")
        self.out = self._textbox(body, row=4)

        # Small buttons
        bar2 = ttk.Frame(body)
        bar2.grid(row=5, column=0, pady=(10, 0))
        ttk.Button(bar2, text="Copy output", command=self.do_copy).grid(row=0, column=0, padx=4)
        ttk.Button(bar2, text="Clear", command=self.do_clear).grid(row=0, column=1, padx=4)
        ttk.Button(bar2, text="Encode file...", command=self.do_encode_file).grid(row=0, column=2, padx=4)
        ttk.Button(bar2, text="Decode file...", command=self.do_decode_file).grid(row=0, column=3, padx=4)
        ttk.Button(bar2, text="Self-test", command=self.do_test).grid(row=0, column=4, padx=4)

        # Status bar
        self.status = tk.StringVar(value="Ready. Type text above and click Encode or Decode.")
        tk.Label(self, textvariable=self.status, anchor="w", bg="#F3F5F8", fg="#333333",
                 font=("Helvetica", 10), padx=10, pady=6).pack(fill="x", side="bottom")

    def _textbox(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        box = tk.Text(frame, height=6, wrap="word", font=("Courier", 12), relief="solid",
                      borderwidth=1, padx=8, pady=8, undo=True)
        box.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=box.yview)
        sb.grid(row=0, column=1, sticky="ns")
        box.configure(yscrollcommand=sb.set)
        return box

    # ---------- helpers ----------
    def _get(self, box):
        return box.get("1.0", "end-1c")

    def _set(self, box, text):
        box.delete("1.0", "end")
        box.insert("1.0", text)

    def _say(self, msg):
        self.status.set(msg)

    # ---------- button actions ----------
    def do_encode(self):
        text = self._get(self.inp)
        if not text:
            self._say("Please type some text in the Input box first.")
            return
        self._set(self.out, encode(text.encode("utf-8")))
        self._say("Encoded successfully.")

    def do_decode(self):
        text = self._get(self.inp)
        if not text.strip():
            self._say("Please paste Base64 text in the Input box first.")
            return
        try:
            result = decode(text).decode("utf-8")
        except ValueError as err:
            self._say("Error: " + str(err))
            messagebox.showerror("Cannot decode", str(err))
            return
        except UnicodeDecodeError:
            msg = "The decoded data is not plain text (it may be a file). Use 'Decode file...'."
            self._say("Error: " + msg)
            messagebox.showerror("Cannot decode", msg)
            return
        self._set(self.out, result)
        self._say("Decoded successfully.")

    def do_swap(self):
        a, b = self._get(self.inp), self._get(self.out)
        self._set(self.inp, b)
        self._set(self.out, a)
        self._say("Input and output swapped.")

    def do_copy(self):
        text = self._get(self.out)
        if not text:
            self._say("Nothing to copy yet.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self._say("Output copied to clipboard.")

    def do_clear(self):
        self._set(self.inp, "")
        self._set(self.out, "")
        self._say("Cleared.")

    def do_encode_file(self):
        src = filedialog.askopenfilename(title="Choose a file to encode")
        if not src:
            return
        dst = filedialog.asksaveasfilename(title="Save Base64 text as", defaultextension=".txt",
                                           initialfile=os.path.basename(src) + ".b64.txt")
        if not dst:
            return
        try:
            with open(src, "rb") as f:
                data = f.read()
            with open(dst, "w") as f:
                f.write(encode(data))
        except OSError as err:
            messagebox.showerror("File error", str(err))
            return
        self._say(f"Encoded {len(data)} bytes. Saved to {dst}")

    def do_decode_file(self):
        src = filedialog.askopenfilename(title="Choose a Base64 text file",
                                         filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not src:
            return
        dst = filedialog.asksaveasfilename(title="Save the original file as")
        if not dst:
            return
        try:
            with open(src, "r") as f:
                data = decode(f.read())
            with open(dst, "wb") as f:
                f.write(data)
        except (OSError, ValueError, UnicodeDecodeError) as err:
            messagebox.showerror("Cannot decode file", str(err))
            return
        self._say(f"Decoded {len(data)} bytes. Saved to {dst}")

    def do_test(self):
        import base64
        lines, ok_all = [], True
        samples = [b"", b"f", b"fo", b"foo", b"foobar", b"Man",
                   b"Hello, World!", b"Samaksh Sharma"]
        for s in samples:
            e = encode(s)
            ok = decode(e) == s and e == base64.b64encode(s).decode()
            ok_all &= ok
            lines.append(f"{'PASS' if ok else 'FAIL'}   {s.decode()!r:20} -> {e}")
        passed = 0
        for n in range(1000):
            d = os.urandom(n % 257)
            if decode(encode(d)) == d and encode(d) == base64.b64encode(d).decode():
                passed += 1
        ok_all &= passed == 1000
        lines.append("")
        lines.append(f"Random data test: {passed}/1000 passed")
        lines.append("")
        lines.append("ALL TESTS PASSED" if ok_all else "SOME TESTS FAILED")
        messagebox.showinfo("Self-test", "\n".join(lines))
        self._say("Self-test finished: " + ("all passed." if ok_all else "some failed."))


if __name__ == "__main__":
    App().mainloop()