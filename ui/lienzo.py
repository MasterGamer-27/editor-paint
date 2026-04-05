import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Crear nuevo lienzo
def nuevo_lienzo(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Nuevo Lienzo")
        dialog.geometry("420x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (420 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"420x350+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="📐 Configurar Nuevo Lienzo", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        frame_width = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_width.pack(pady=8)
        ctk.CTkLabel(frame_width, text="Ancho (píxeles):", width=120).pack(side=tk.LEFT, padx=10)
        self.entry_width = ctk.CTkEntry(frame_width, width=100)
        self.entry_width.pack(side=tk.LEFT)
        self.entry_width.insert(0, "800")
        
        frame_height = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_height.pack(pady=8)
        ctk.CTkLabel(frame_height, text="Alto (píxeles):", width=120).pack(side=tk.LEFT, padx=10)
        self.entry_height = ctk.CTkEntry(frame_height, width=100)
        self.entry_height.pack(side=tk.LEFT)
        self.entry_height.insert(0, "600")
        
        ctk.CTkLabel(dialog, text="Tamaños rápidos:").pack(pady=(15, 5))
        
        def set_tamano(w, h):
            self.entry_width.delete(0, tk.END)
            self.entry_width.insert(0, str(w))
            self.entry_height.delete(0, tk.END)
            self.entry_height.insert(0, str(h))
        
        frame_presets = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_presets.pack(pady=5)
        ctk.CTkButton(frame_presets, text="HD (1280x720)", width=100,
                      command=lambda: set_tamano(1280, 720)).grid(row=0, column=0, padx=5)
        ctk.CTkButton(frame_presets, text="Full HD (1920x1080)", width=120,
                      command=lambda: set_tamano(1920, 1080)).grid(row=0, column=1, padx=5)
        ctk.CTkButton(frame_presets, text="Cuadrado (800x800)", width=120,
                      command=lambda: set_tamano(800, 800)).grid(row=0, column=2, padx=5)
        
        def aplicar_tamano():
            try:
                new_width = int(self.entry_width.get())
                new_height = int(self.entry_height.get())
                
                if new_width < 100 or new_height < 100:
                    messagebox.showwarning("⚠️ Advertencia", 
                        "El tamaño mínimo es 100x100 píxeles", parent=dialog)
                    return
                
                if new_width > 2000 or new_height > 2000:
                    messagebox.showwarning("⚠️ Advertencia", 
                        "El tamaño máximo es 2000x2000 píxeles", parent=dialog)
                    return
                
                if self.canvas is not None:
                    if not messagebox.askyesno("⚠️ Confirmar", 
                        f"¿Crear nuevo lienzo de {new_width}x{new_height}?\n\nSe perderá el contenido actual.",
                        parent=dialog):
                        return
                
                self.crear_lienzo(new_width, new_height)
                dialog.destroy()
                    
            except ValueError:
                messagebox.showerror("❌ Error", 
                    "Por favor ingresa números válidos", parent=dialog)
        
        ctk.CTkButton(dialog, text="✅ Crear Lienzo", command=aplicar_tamano, 
                      fg_color=self.color_boton_exito, width=200, height=40,
                      font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)
        
        ctk.CTkButton(dialog, text="❌ Cancelar", command=dialog.destroy, 
                      fg_color=self.color_boton_peligro, width=200, height=35).pack()
        

def abrir_imagen(self):
        """Abre una imagen desde el sistema de archivos y la carga en el lienzo"""
        file_path = filedialog.askopenfilename(
            title="🖼️ Abrir Imagen",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            img = Image.open(file_path)
            img_width, img_height = img.size
            
            if self.canvas is None:
                response = messagebox.askyesno(
                    "📐 Crear lienzo",
                    f"La imagen tiene {img_width}x{img_height} píxeles.\n\n"
                    f"¿Quieres crear un lienzo con estas dimensiones?\n"
                    f"• Sí: Lienzo exacto al tamaño de la imagen\n"
                    f"• No: Usar lienzo por defecto (800x600) y ajustar imagen",
                    parent=self.root
                )
                
                if response:
                    max_size = 2000
                    new_w = min(img_width, max_size)
                    new_h = min(img_height, max_size)
                    self.crear_lienzo(new_w, new_h)
                    if img_width != new_w or img_height != new_h:
                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                else:
                    self.crear_lienzo(800, 600)
                    img = self._ajustar_imagen_al_lienzo(img, self.width, self.height)
            else:
                img = self._ajustar_imagen_al_lienzo(img, self.width, self.height)
            
            self.background_img = img.copy()
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            self.guardar_estado()
            
            filename = file_path.split("/")[-1]
            self.root.title(f"🎨 Paint Pro - {filename}")
            print(f"✅ Imagen cargada: {file_path}")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo cargar la imagen:\n{str(e)}")
            print(f"❌ Error al abrir imagen: {e}")

def _ajustar_imagen_al_lienzo(self, img, canvas_w, canvas_h):
        img_w, img_h = img.size
        ratio = min(canvas_w / img_w, canvas_h / img_h)
        new_size = (int(img_w * ratio), int(img_h * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)

def salir_app(self):
    if messagebox.askyesno("🚪 Salir", "¿Estás seguro de que deseas salir?"):
        self.root.destroy()

# ================= CREAR LIENZO =================
def crear_lienzo(self, width, height):
    self.width = width
    self.height = height
    self.background_img = None
    self.undo_stack = []
    self.redo_stack = []
        
    if self.bienvenida_label:
        self.bienvenida_label.destroy()
        self.bienvenida_label = None
        
    if self.canvas:
        self.canvas.destroy()
        self.canvas = None
        
    if self.frame_herramientas is None:
        self.frame_herramientas = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
        self.frame_herramientas.pack(pady=10, padx=10, fill=tk.X)
        self.crear_herramientas()
        
    if self.canvas_frame is None:
        self.canvas_frame = ctk.CTkFrame(self.root, fg_color="#1a1a1a")
        self.canvas_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
    self.canvas = tk.Canvas(self.canvas_frame, width=self.width, height=self.height, 
                                bg='white', highlightthickness=0)
    self.canvas.pack(pady=10, expand=True)
        
    self.canvas.bind('<Button-1>', self.iniciar_dibujo)
    self.canvas.bind('<B1-Motion>', self.dibujar)
    self.canvas.bind('<ButtonRelease-1>', self.detener_dibujo)
        
    self.root.title(f"🎨 Paint Pro - {self.width}x{self.height}")
        
    window_width = min(self.width + 100, 1600)
    window_height = self.height + 250
    self.root.geometry(f"{window_width}x{window_height}")
        
    self.guardar_estado()
    print(f"✅ Lienzo creado: {self.width}x{self.height}")