import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

# ================= CÁMARA =================

def abrir_camara(self):
    if self.canvas is None:
        messagebox.showwarning("⚠️ Advertencia", "Primero crea un lienzo con 'Archivo > Nuevo'")
        return
        
    cam_window = ctk.CTkToplevel(self.root)
    cam_window.title("📷 Cámara Web")
    cam_window.geometry("680x640")
    cam_window.transient(self.root)
        
    cam_window.update_idletasks()
    x = (cam_window.winfo_screenwidth() // 2) - (680 // 2)
    y = (cam_window.winfo_screenheight() // 2) - (640 // 2)
    cam_window.geometry(f"680x640+{x}+{y}")
        
    ctk.CTkLabel(cam_window, text="📷 Cámara Web - Presiona ESPACIO o click para capturar", 
                 font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
    cam_label = ctk.CTkLabel(cam_window, text="")
    cam_label.pack(pady=10)
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("❌ Error", "No se pudo acceder a la cámara")
        cam_window.destroy()
        return
        
    is_capturing = True
        
    def update_frame():
        if is_capturing:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                cam_label.configure(image=imgtk)
                cam_label.imgtk = imgtk
            cam_window.after(10, update_frame)
        
    def capturar_foto(event=None):
        nonlocal is_capturing
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.background_img = Image.fromarray(frame_rgb)
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            self.guardar_estado()
            messagebox.showinfo("✅ Foto Capturada", "La foto se cargó en el lienzo.\n\n¡Ahora puedes dibujar sobre ella!")
            is_capturing = False
            cap.release()
            cam_window.destroy()
        else:
            messagebox.showerror("❌ Error", "No se pudo capturar la foto")
        
    ctk.CTkButton(cam_window, text="📸 Capturar Foto", command=capturar_foto, 
                  fg_color=self.color_boton_primario, width=200, height=40, 
                  font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10)
        
    ctk.CTkLabel(cam_window, text="💡 Tip: Presiona ESPACIO para capturar más rápido", 
                     text_color="gray", font=ctk.CTkFont(size=11)).pack()
    cam_window.bind('<space>', capturar_foto)
    update_frame()
        
    def on_close():
        nonlocal is_capturing
        is_capturing = False
        cap.release()
        cam_window.destroy()
    cam_window.protocol("WM_DELETE_WINDOW", on_close)