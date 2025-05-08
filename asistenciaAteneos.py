import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd

IMAGE_DIR = "fotos"
EXCEL_FILE = "participantes.xlsx"
CHECKIN_LOG = "checkin_log.xlsx"
LOGO_FILE = "fotos/logo subse azul_Mesa de trabajo 1.png"

# Asegurarse de que exista la carpeta de imágenes
def ensure_dirs():
    os.makedirs(IMAGE_DIR, exist_ok=True)

# Cargar datos desde Excel
def load_participants():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, dtype=str)
        return df.set_index("dni")
    return pd.DataFrame()

# Guardar check-in en un archivo Excel independiente
def log_checkin(dni, nombre):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = pd.DataFrame([[dni, nombre, now]], columns=["dni", "nombre", "checkin"])
    if os.path.exists(CHECKIN_LOG):
        df = pd.read_excel(CHECKIN_LOG)
        df = pd.concat([df, row], ignore_index=True)
    else:
        df = row
    df.to_excel(CHECKIN_LOG, index=False)

class AsistenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Offline de Asistencia")
        self.geometry("900x700")

        self.participantes = load_participants()
        self.after_id = None
        self.info_mostrada = False
        self.tiempo_mostrado = 0

        self.tab_control = ttk.Notebook(self)
        self.checkin_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.checkin_tab, text="Check-in")
        self.tab_control.pack(expand=1, fill="both")

        self.build_checkin_tab()

    def build_checkin_tab(self):
        frame = ttk.Frame(self.checkin_tab, padding=(10, 10, 10, 0))
        frame.pack(fill="both", expand=True)

        # Logo
        try:
            logo_img = Image.open(LOGO_FILE)
            logo_img = logo_img.resize((400, 250), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            ttk.Label(frame, image=self.logo_photo).grid(row=0, column=0, columnspan=3, pady=(10, 0))
        except:
            pass

        # DNI input
        ttk.Label(frame, text="DNI:", font=("Arial", 16)).grid(row=1, column=0, sticky="e", pady=10)
        self.checkin_dni_var = tk.StringVar()
        self.dni_entry = ttk.Entry(frame, textvariable=self.checkin_dni_var, font=("Arial", 16), width=30)
        self.dni_entry.grid(row=1, column=1, sticky="w")
        self.dni_entry.bind("<Return>", self.handle_enter)

        self.buscar_btn = ttk.Button(frame, text="Buscar", command=self.lookup_participante)
        self.buscar_btn.grid(row=1, column=2, padx=10)

        # Result area
        self.result_frame = ttk.Frame(frame, borderwidth=2, relief="solid", padding=20)
        self.result_frame.grid(row=2, column=0, columnspan=3, pady=20, sticky="nsew")
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(1, weight=1)

    def handle_enter(self, event):
        if self.info_mostrada:
            if (datetime.now() - self.tiempo_mostrado).total_seconds() >= 7:
                self.clear_result()
                self.checkin_dni_var.set("")
                self.buscar_btn.config(state="normal")
                self.info_mostrada = False
            return

        if self.after_id:
            self.after_cancel(self.after_id)

        self.buscar_btn.config(state="disabled")
        self.lookup_participante(auto=True)

    def lookup_participante(self, auto=False):
        dni = self.checkin_dni_var.get().strip()
        if not dni:
            return

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if dni not in self.participantes.index:
            messagebox.showerror("No encontrado", "DNI no registrado.")
            self.buscar_btn.config(state="normal")
            return

        participante = self.participantes.loc[dni]
        apellido = participante["apellido"]
        nombre = participante["nombre"]
        correo = participante["correo"]
        foto_path = participante["foto_path"]

        content_frame = ttk.Frame(self.result_frame)
        content_frame.pack(fill="both", expand=True)

        # Foto a la derecha
        try:
            img = Image.open(foto_path)
            img.thumbnail((400, 500), Image.LANCZOS)  # Mantener proporción
            self.photo_img = ImageTk.PhotoImage(img)
            img_label = ttk.Label(content_frame, image=self.photo_img)
            img_label.pack(side="right", padx=30, pady=10)
        except:
            ttk.Label(content_frame, text="Foto no disponible", font=("Arial", 14)).pack(side="right", padx=30, pady=10)

        # Info personal a la izquierda
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side="left", padx=30, pady=10, anchor="n")

        ttk.Label(info_frame, text=f"Apellido: {apellido}", font=("Arial", 20, "bold")).pack(anchor="w", pady=5)
        ttk.Label(info_frame, text=f"Nombre: {nombre}", font=("Arial", 20, "bold")).pack(anchor="w", pady=5)
        ttk.Label(info_frame, text=f"Correo: {correo}", font=("Arial", 18)).pack(anchor="w", pady=5)

        log_checkin(dni, nombre)

        self.tiempo_mostrado = datetime.now()
        self.info_mostrada = True

    def clear_result(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    ensure_dirs()
    app = AsistenciaApp()
    app.mainloop()
