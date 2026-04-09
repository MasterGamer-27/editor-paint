# ARCHIVO MAIN - LLAMA A METODO PAINT APP
import customtkinter as ctk
from paintv2 import PaintApp

if __name__ == "__main__":

    # ================= CONFIGURACIÓN DE TEMA =================
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    root = ctk.CTk()
    app = PaintApp(root)
    root.mainloop()