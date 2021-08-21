from tkinter import filedialog as fd
from pathlib import Path
from components import *
from enums import *
from utils import *

import tkinter as tk


labels = ["Vrsta simetričnog ključa:", "Način kriptiranja:", "Veličina simetričnog ključa:",
          "Veličina ključeva: ", "Generirani ključevi primatelja",
          "Generirani ključevi pošiljatelja", "Vrsta hasha:", "Veličina ključa:",
          "Stvoriti: ", "Provjeriti: ", "Datoteka:"]

PINK = "#DB619E"
PASTEL = "#ffd1dc"
f1 = ("Helvetica", 12, "bold")
f2 = ("Helvetica", 9)


class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self["background"] = PASTEL
        self.sym_key = tk.StringVar(self, "AES")
        self.sym_key_length = tk.IntVar(self, 128)
        self.sym_key_mode = tk.StringVar(self, "CBC")
        self.save_path = tk.StringVar(self, "C:/Users/Jelena/PycharmProjects/NOS_FER/lab2/saved")
        self.rsa_length = tk.IntVar(self, 1024)
        self.rsa_rec_file = tk.StringVar(self, "C:/Users/Jelena/PycharmProjects/NOS_FER/lab2/saved")
        self.rsa_sen_file = tk.StringVar(self, "C:/Users/Jelena/PycharmProjects/NOS_FER/lab2/saved")
        self.hash_mode = tk.StringVar(self, "SHA2")
        self.hash_length = tk.IntVar(self, 256)
        self.structure = tk.StringVar(self, "Digitalna omotnica")
        self.make_verify = tk.StringVar(self, "Stvori")
        self.file = tk.StringVar(self, "C:/Users/Jelena/PycharmProjects/NOS_FER/lab2/dat")
        tk.Label(self, text=self.file.get(), bg=PASTEL, font=f2).grid(row=14, column=1, sticky="news")
        tk.Label(self, text=self.save_path.get(), bg=PASTEL, font=f2).grid(row=15, column=1, sticky="news")
        tk.Label(self, text=self.rsa_rec_file.get(), bg=PASTEL, font=f2).grid(row=6, column=1, sticky="news")
        tk.Label(self, text=self.rsa_sen_file.get(), bg=PASTEL, font=f2).grid(row=7, column=1, sticky="news")
        self.file_seal = tk.StringVar()
        self.file_env = tk.StringVar()
        self.file_sign = tk.StringVar()

        self.make_sym_keys()
        self.make_rsa_keys()
        self.make_hash_mode()
        self.make_creation_buttons()

    def generate(self):
        save_path = Path(self.save_path.get())
        # poruka
        if self.file.get() != "":
            with Path(self.file.get()).open(mode="r") as f:
                message = f.read()
        else:
            print("Datoteka nije priložena! Greška!")
            return

        # simetrični ključ
        sym_key = KEY_TYPES[self.sym_key.get()]
        if self.sym_key.get() == "3DES":
            sym_key_mode = DES3_MODES[self.sym_key_mode.get()]
            iv_size = 8
            if self.sym_key_length.get() == 256:
                print("Za 3DES nije moguće odabrati veličinu ključa od 256!")
                return
        else:
            sym_key_mode = AES_MODES[self.sym_key_mode.get()]
            iv_size = 16
        padding = sym_key.block_size

        # rsa ključ
        if self.rsa_sen_file.get() != "" and self.rsa_rec_file.get() != "":
            rsa_sender_path = Path(self.rsa_sen_file.get())
            rsa_rec_path = Path(self.rsa_rec_file.get())
            private_sender_key, public_sender_key = load_rsa_keys(rsa_sender_path, sender=True)
            private_receiver_key, public_receiver_key = load_rsa_keys(rsa_rec_path, sender=False)
            private_sender_key = RSA.import_key(private_sender_key)
            public_sender_key = RSA.import_key(public_sender_key)
            private_receiver_key = RSA.import_key(private_receiver_key)
            public_receiver_key = RSA.import_key(public_receiver_key)
        else:
            public_sender_key, private_sender_key = get_public_private_keys(self.rsa_length.get(), RSA)
            save_rsa_keys(private_sender_key, public_sender_key, save_path, sender=True)
            public_receiver_key, private_receiver_key = get_public_private_keys(self.rsa_length.get(), RSA)
            save_rsa_keys(private_receiver_key, public_receiver_key, save_path, sender=False)
            private_sender_key, public_sender_key = load_rsa_keys(save_path, sender=True)
            private_receiver_key, public_receiver_key = load_rsa_keys(save_path, sender=False)
            private_sender_key = RSA.import_key(private_sender_key)
            public_sender_key = RSA.import_key(public_sender_key)
            private_receiver_key = RSA.import_key(private_receiver_key)
            public_receiver_key = RSA.import_key(public_receiver_key)

        # hash funkcija
        if self.hash_mode.get() == "SHA2":
            hash_mode = SHA2_TYPES[self.hash_length.get()]
        else:
            hash_mode = SHA3_TYPES[self.hash_length.get()]

        if self.make_verify.get() == "Stvori":
            if self.structure.get() == "Digitalni potpis":
                signature = get_signature(message, hash_mode, private_sender_key)
                save_component((save_path / "signature.txt"), signature)
            elif self.structure.get() == "Digitalna omotnica":
                cypher_text, cypher_key, iv = get_envelope(message, sym_key, sym_key_mode, self.sym_key_length.get(),
                                                           public_receiver_key, padding, iv_size)
                save_component((save_path / "envelope_cypher_text.txt"), cypher_text)
                save_component((save_path / "envelope_cypher_key.pem"), cypher_key)
                save_component((save_path / "iv.txt"), iv)

            else:
                cypher_text, cypher_key, iv, signature = get_stamp(message, sym_key, sym_key_mode,
                                                                   self.sym_key_length.get(), public_receiver_key,
                                                                   private_sender_key, hash_mode, padding, iv_size)
                save_component((save_path / "envelope_cypher_text.txt"), cypher_text)
                save_component((save_path / "envelope_cypher_key.pem"), cypher_key)
                save_component((save_path / "iv.txt"), iv)
                save_component((save_path / "signature.txt"), signature)
        else:
            if self.structure.get() == "Digitalni potpis":
                signature = load_component(save_path / "signature.txt")
                verify_signature(message, signature, hash_mode, public_sender_key)
            elif self.structure.get() == "Digitalna omotnica":
                cypher_text = load_component(save_path / "envelope_cypher_text.txt")
                cypher_key = load_component(save_path / "envelope_cypher_key.pem")
                iv = load_component(save_path / "iv.txt")
                message = decrypt_envelope(cypher_text, cypher_key, sym_key, sym_key_mode,
                                           private_receiver_key, padding, iv)
                print(message)
            else:
                cypher_text = load_component(save_path / "envelope_cypher_text.txt")
                cypher_key = load_component(save_path / "envelope_cypher_key.pem")
                signature = load_component(save_path / "signature.txt")
                verify_stamp(cypher_text, cypher_key, public_sender_key, hash_mode, signature)

        return

    def dat_load(self):
        file_name = fd.askopenfilename()
        if file_name:
            self.file.set(file_name)
            tk.Label(self, text=file_name, font=f2, bg=PASTEL).grid(row=14, column=1, sticky="news")
        return

    def path_load(self):
        file_name = fd.askdirectory()
        if file_name:
            self.save_path.set(file_name)
            tk.Label(self, text=file_name, font=f2, bg=PASTEL).grid(row=15, column=1, sticky="news")
        return

    def rsa_rec(self):
        file_name = fd.askdirectory()
        if file_name:
            self.rsa_rec_file.set(file_name)
            tk.Label(self, text=file_name, font=f2, bg=PASTEL).grid(row=6, column=1, sticky="news")
        return

    def rsa_send(self):
        file_name = fd.askdirectory()
        if file_name:
            self.rsa_sen_file.set(file_name)
            tk.Label(self, text=file_name, font=f2, bg=PASTEL).grid(row=7, column=1, sticky="news")
        return

    def make_labels(self):
        for idx, label in enumerate(labels):
            tk.Label(self, text=label, font=f1, bg=PASTEL).grid(row=idx, column=0, sticky="news")

    def make_sym_keys(self):
        tk.Label(self, text="Simetrični ključ:", font=f1, bg=PASTEL).grid(row=0, column=0, columnspan=3, sticky="news")
        for i in range(3):
            tk.Label(self, text=labels[i], font=f2, bg=PASTEL).grid(row=i+1, column=0, sticky="news")

        modes = ["AES", "3DES"]
        frame = tk.Frame(self)
        frame["background"] = PASTEL
        frame.grid(row=1, column=1, columnspan=2, sticky="news")

        for idx, mode in enumerate(modes):
            tk.Radiobutton(frame, text=mode, variable=self.sym_key, value=mode, font=f2, bg=PASTEL).grid(row=0,
                                                                                                         column=idx,
                                                                                                         sticky="news")

        modes = ["CBC", "OFB", "CFB"]
        frame = tk.Frame(self)
        frame["background"] = PASTEL
        frame.grid(row=2, column=1, columnspan=2, sticky="news")

        for idx, mode in enumerate(modes):
            tk.Radiobutton(frame, text=mode, variable=self.sym_key_mode, value=mode, font=f2, bg=PASTEL).grid(row=0,
                                                                                          column=idx, sticky="news")

        modes = [128, 192, 256]
        frame = tk.Frame(self)
        frame["background"] = PASTEL
        frame.grid(row=3, column=1, columnspan=2, sticky="news")

        for idx, mode in enumerate(modes):
            tk.Radiobutton(frame, text=mode, variable=self.sym_key_length, font=f2,
                           value=mode, bg=PASTEL).grid(row=0, column=idx, sticky="news")

    def make_rsa_keys(self):
        tk.Label(self, text="RSA ključ:", font=f1, bg=PASTEL).grid(row=4, column=0, columnspan=3, sticky="news")
        for i in range(3):
            tk.Label(self, text=labels[i+3], font=f2, bg=PASTEL).grid(row=5+i, column=0, sticky="news")

        modes = [1024, 2048, 4096]
        frame = tk.Frame(self)
        frame["background"] = PASTEL
        frame.grid(row=5, column=1, columnspan=2, sticky="news")

        for idx, mode in enumerate(modes):
            tk.Radiobutton(frame, text=mode, variable=self.rsa_length, font=f2,
                           value=mode, bg=PASTEL).grid(row=0, column=idx, sticky="news")

        tk.Button(self, text="Odaberi...", command=self.rsa_rec, bg=PINK, font=f2).grid(row=6, column=2, sticky="news")
        tk.Button(self, text="Odaberi...", command=self.rsa_send, bg=PINK, font=f2).grid(row=7, column=2, sticky="news")

    def make_hash_mode(self):
        tk.Label(self, text="Hash funkcija:", font=f1, bg=PASTEL).grid(row=8, column=0, columnspan=3, sticky="news")
        for i in range(2):
            tk.Label(self, text=labels[6+i], font=f2, bg=PASTEL).grid(row=9+i, column=0, sticky="news")
        modes = ["SHA2", "SHA3"]
        frame = tk.Frame(self)
        frame["background"] = PASTEL
        frame.grid(row=9, column=1, columnspan=2, sticky="news")

        for idx, mode in enumerate(modes):
            tk.Radiobutton(frame, text=mode, variable=self.hash_mode,
                           value=mode, font=f2, bg=PASTEL).grid(row=0, column=idx, sticky="news")

        modes = [224, 256, 384, 512]
        frame = tk.Frame(self)
        frame["background"] = PASTEL
        frame.grid(row=10, column=1, columnspan=2, sticky="news")

        for idx, mode in enumerate(modes):
            tk.Radiobutton(frame, text=mode, variable=self.hash_length,
                           value=mode, font=f2, bg=PASTEL).grid(row=0, column=idx, sticky="news")

    def make_creation_buttons(self):
        tk.Radiobutton(self, text="Stvori", variable=self.make_verify,
                       value="Stvori", font=f2, bg=PASTEL).grid(row=11, column=0, sticky="news")
        tk.Radiobutton(self, text="Provjeri", variable=self.make_verify,
                       value="Provjeri", font=f2, bg=PASTEL).grid(row=11, column=2, sticky="news")

        modes = ["Digitalna omotnica", "Digitalni potpis", "Digitalni pečat"]

        for idx, mode in enumerate(modes):
            tk.Radiobutton(self, text=mode, variable=self.structure,
                           value=mode, font=f2, bg=PASTEL).grid(row=12, column=idx, sticky="news")

        tk.Label(self, text="Učitavanje generiranih datoteka", font=f1, bg=PASTEL).grid(row=13, column=0,
                                                                                        columnspan=3, sticky="news")
        for idx, (label, command) in enumerate(zip(["Datoteka:", "Mapa za spremanje"],
                                                   [self.dat_load, self.path_load])):
            tk.Label(self, text=label, font=f2, bg=PASTEL).grid(row=14+idx, column=0, sticky="news")
            tk.Button(self, text="Odaberi...", command=command, bg=PINK, font=f2).grid(row=14+idx, column=2,
                                                                                       sticky="news")
        tk.Button(self, text="Generiraj!", command=self.generate, bg=PINK, font=f2).grid(row=16, column=0,
                                                                                         columnspan=3, sticky="news")


if __name__ == '__main__':
    app = GUI()
    app.mainloop()
