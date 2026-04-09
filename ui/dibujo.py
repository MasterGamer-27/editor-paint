import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading

# ================= HERRAMIENTAS DE DIBUJO =================
def crear_herramientas(self):
    """Toolbar con botón de TEXTO agregado"""
    for i in range(10):
        self.frame_herramientas.grid_columnconfigure(i, weight=0)
        
    # Fila 0 - Botones y controles
    ctk.CTkButton(self.frame_herramientas, text="🎨 Color", 
                      command=self.elegir_color, width=90, height=40,
                      fg_color=self.color_boton_primario, corner_radius=8).grid(row=0, column=0, padx=5, pady=5)
        
    ctk.CTkButton(self.frame_herramientas, text="📷 Cámara", 
                      command=self.abrir_camara, width=90, height=40,
                      fg_color=self.color_boton_primario, corner_radius=8).grid(row=0, column=1, padx=5, pady=5)
        
    # 🔤 BOTÓN TEXTO (NUEVO)
    ctk.CTkButton(self.frame_herramientas, text="🔤 Texto", 
                      command=self.activar_herramienta_texto, width=90, height=40,
                      fg_color="#9B59B6", corner_radius=8).grid(row=0, column=2, padx=5, pady=5)
        
    ctk.CTkButton(self.frame_herramientas, text="↩️ Deshacer", 
                      command=self.deshacer, width=90, height=40,
                      fg_color=self.color_boton_secundario, corner_radius=8).grid(row=0, column=3, padx=5, pady=5)
        
    ctk.CTkButton(self.frame_herramientas, text="↪️ Rehacer", 
                      command=self.rehacer, width=90, height=40,
                      fg_color=self.color_boton_secundario, corner_radius=8).grid(row=0, column=4, padx=5, pady=5)
        
    ctk.CTkButton(self.frame_herramientas, text="🧹 Limpiar", 
                      command=self.limpiar_lienzo, width=90, height=40,
                      fg_color=self.color_boton_peligro, corner_radius=8).grid(row=0, column=5, padx=5, pady=5)
        
    ctk.CTkButton(self.frame_herramientas, text="💾 Guardar", 
                      command=self.guardar_imagen, width=90, height=40,
                      fg_color=self.color_boton_exito, corner_radius=8).grid(row=0, column=6, padx=5, pady=5)
        
    # Label Grosor
    ctk.CTkLabel(self.frame_herramientas, text="Grosor:", 
                 text_color="#a0a0a0").grid(row=0, column=7, padx=10, pady=5)
        
    # Slider
    self.size_slider = ctk.CTkSlider(self.frame_herramientas, from_=1, to=20, 
                                          width=120, height=20,
                                          command=self.cambiar_grosor,
                                          progress_color=self.color_boton_primario)
    self.size_slider.set(5)
    self.size_slider.grid(row=0, column=8, padx=5, pady=5)
        
    # Label Color Actual
    self.color_label = ctk.CTkLabel(self.frame_herramientas, text="⬛ Color", 
                                         font=ctk.CTkFont(size=11), text_color="#ffffff")
    self.color_label.grid(row=0, column=9, padx=10, pady=5)
        
    # Fila 1 - Historial
    self.history_label = ctk.CTkLabel(self.frame_herramientas, 
                                           text="📋 Historial: 0/0", 
                                           font=ctk.CTkFont(size=10), 
                                           text_color="#7f8c8d")
    self.history_label.grid(row=1, column=0, columnspan=10, pady=5)


# ================= FUNCIONES DE DIBUJO =================
def iniciar_dibujo(self, event):
    if self.text_tool_active:
        return  # No dibujar si está activo el modo texto
    self.old_x = event.x
    self.old_y = event.y

def dibujar(self, event):
        if self.old_x and self.old_y and not self.text_tool_active:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=self.brush_size, fill=self.color,
                                    capstyle=tk.ROUND, smooth=True)
            self.old_x = event.x
            self.old_y = event.y

def detener_dibujo(self, event):
        if not self.text_tool_active:
            self.old_x = None
            self.old_y = None
            self.guardar_estado()

def elegir_color(self):
        color = colorchooser.askcolor(title="🎨 Elige un color")[1]
        if color:
            self.color = color
            self.color_label.configure(text=f"█ Color", text_color=color)
            print(f"Color cambiado a: {color}")    

def cambiar_grosor(self, val):
        self.brush_size = int(val)
        print(f"Grosor cambiado a: {self.brush_size}")

def limpiar_lienzo(self):
        if self.canvas:
            if messagebox.askyesno("🧹 Limpiar", "¿Estás seguro de limpiar el lienzo?"):
                self.canvas.delete("all")
                self.background_img = None
                self.guardar_estado()
                print("✅ Lienzo limpiado")

def guardar_imagen(self):
        if self.canvas is None:
            messagebox.showwarning("⚠️ Advertencia", "Primero crea un lienzo")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"), 
                ("JPG files", "*.jpg *.jpeg"), 
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return
        
        ext = file_path.split('.')[-1].lower()
        if ext not in ['png', 'jpg', 'jpeg']:
            file_path += '.png'
            ext = 'png'
        
        loading_window = self._mostrar_carga("Guardando imagen...", "Por favor espera")
        loading_window.update()
        
        threading.Thread(
            target=self._proceso_guardado, 
            args=(file_path, ext, loading_window), 
            daemon=True
        ).start()


def _mostrar_carga(self, titulo, mensaje):
        win = ctk.CTkToplevel(self.root)
        win.title(titulo)
        win.geometry("350x160")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (160 // 2)
        win.geometry(f"350x160+{x}+{y}")
        
        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text=mensaje, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 15))
        
        progress = ctk.CTkProgressBar(frame, width=280, height=20, mode="indeterminate", progress_color="#3B8ED0")
        progress.pack(pady=10)
        progress.set(0)
        
        def iniciar_animacion():
            progress.start()
        win.after(100, iniciar_animacion)
        
        ctk.CTkLabel(frame, text="⏳ Procesando, por favor espera...", font=ctk.CTkFont(size=11), text_color="#888888").pack(pady=(10, 0))
        return win

def _proceso_guardado(self, file_path, ext, loading_window):
        try:
            import os, tempfile
            from PIL import Image
            
            with tempfile.NamedTemporaryFile(suffix='.eps', delete=False) as tmp:
                temp_eps = tmp.name
            
            self.canvas.postscript(file=temp_eps, colormode='color')
            img = Image.open(temp_eps)
            
            if ext in ['jpg', 'jpeg']:
                img = img.convert('RGB')
                img.save(file_path, 'JPEG', quality=95)
            else:
                img.save(file_path, 'PNG')
            
            os.unlink(temp_eps)
            loading_window.destroy()
            self.root.after(0, lambda: messagebox.showinfo("✅ Éxito", f"Imagen guardada en:\n{file_path}"))
            print(f"✅ Imagen guardada: {file_path}")
            
        except Exception as e:
            loading_window.destroy()
            if "Ghostscript" in str(e) or "gs" in str(e).lower():
                msg = ("Para guardar imágenes se requiere Ghostscript instalado.\n\n"
                    "Instálalo con:\n"
                    "• Linux Mint/Debian: sudo apt install ghostscript\n"
                    "• Windows: https://ghostscript.com/releases/gsdnld.html\n"
                    "• Mac: brew install ghostscript")
                self.root.after(0, lambda: messagebox.showerror("❌ Dependencia faltante", msg))
            else:
                self.root.after(0, lambda: messagebox.showerror("❌ Error", f"No se pudo guardar:\n{str(e)}"))
            print(f"❌ Error al guardar: {e}")