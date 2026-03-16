import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

# ================= CONFIGURACIÓN DE TEMA =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Paint Pro - OpenCV + Cámara")
        self.root.geometry("500x400")
        self.root.minsize(400, 300)
        
        # Variables de tamaño del lienzo
        self.width = None
        self.height = None
        self.canvas = None
        self.canvas_frame = None
        self.frame_herramientas = None
        
        # Variables de dibujo
        self.old_x = None
        self.old_y = None
        self.color = 'black'
        self.brush_size = 5
        
        # Variable para la imagen de fondo (cámara o imagen cargada)
        self.background_img = None
        
        # ================= HISTORIAL DESHACER/REHACER =================
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 50
        
        # ================= CONFIGURAR ESTILO =================
        self.configurar_estilo()
        
        # ================= CREAR MENÚ =================
        self.crear_menu()
        
        # ================= LABEL DE BIENVENIDA =================
        self.bienvenida_label = ctk.CTkLabel(
            root, 
            text="Bienvenido a Paint Pro\n\nSelecciona 'Archivo > Nuevo' para comenzar",
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="center"
        )
        self.bienvenida_label.pack(expand=True)

    # ================= ESTILO =================
    def configurar_estilo(self):
        self.color_boton_primario = "#3B8ED0"
        self.color_boton_secundario = "#1F538D"
        self.color_boton_peligro = "#DC3545"
        self.color_boton_exito = "#28A745"
        self.root.configure(fg_color="#2B2B2B")

    # ================= MENÚ =================
    def crear_menu(self):
        menubar = tk.Menu(self.root, bg="#1a1a1a", fg="white")
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2B2B2B", fg="white")
        menubar.add_cascade(label="📁 Archivo", menu=file_menu)
        
        file_menu.add_command(label="📄 Nuevo Lienzo", command=self.nuevo_lienzo)
        file_menu.add_command(label="🖼️ Abrir Imagen", command=self.abrir_imagen)  # ← NUEVA OPCIÓN
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Salir", command=self.salir_app)
        
        self.root.bind('<Control-z>', lambda e: self.deshacer())
        self.root.bind('<Control-Z>', lambda e: self.deshacer())
        self.root.bind('<Control-y>', lambda e: self.rehacer())
        self.root.bind('<Control-Y>', lambda e: self.rehacer())
        self.root.bind('<Control-n>', lambda e: self.nuevo_lienzo())
        self.root.bind('<Control-s>', lambda e: self.guardar_imagen())
        self.root.bind('<Control-o>', lambda e: self.abrir_imagen())  # ← Atajo Ctrl+O

    # ================= FUNCIONES DEL MENÚ =================
    def nuevo_lienzo(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Nuevo Lienzo")
        dialog.geometry("350x280")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (280 // 2)
        dialog.geometry(f"350x280+{x}+{y}")
        
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

    # ================= NUEVA FUNCIÓN: ABRIR IMAGEN =================
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
            return  # Usuario canceló
        
        try:
            # Cargar imagen con PIL
            img = Image.open(file_path)
            
            # Obtener dimensiones originales
            img_width, img_height = img.size
            
            # Si no hay lienzo creado, preguntar si quiere usar las dimensiones de la imagen
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
                    # Crear lienzo con dimensiones de la imagen (con límites)
                    max_size = 2000
                    new_w = min(img_width, max_size)
                    new_h = min(img_height, max_size)
                    self.crear_lienzo(new_w, new_h)
                    # Redimensionar imagen si se aplicó límite
                    if img_width != new_w or img_height != new_h:
                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                else:
                    # Crear lienzo por defecto
                    self.crear_lienzo(800, 600)
                    # Ajustar imagen al lienzo manteniendo aspecto
                    img = self._ajustar_imagen_al_lienzo(img, self.width, self.height)
            else:
                # Ya existe lienzo: ajustar imagen a sus dimensiones
                img = self._ajustar_imagen_al_lienzo(img, self.width, self.height)
            
            # Convertir a formato compatible con Tkinter
            self.background_img = img.copy()
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            
            # Limpiar canvas y mostrar imagen
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            
            # Guardar estado para historial
            self.guardar_estado()
            
            # Actualizar título
            filename = file_path.split("/")[-1]
            self.root.title(f"🎨 Paint Pro - {filename}")
            
            print(f"✅ Imagen cargada: {file_path}")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo cargar la imagen:\n{str(e)}")
            print(f"❌ Error al abrir imagen: {e}")

    def _ajustar_imagen_al_lienzo(self, img, canvas_w, canvas_h):
        """Redimensiona imagen manteniendo aspecto para que quepa en el lienzo"""
        img_w, img_h = img.size
        
        # Calcular ratio de escalado
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
        
        # Herramientas primero (arriba), luego el lienzo
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

    # ================= HERRAMIENTAS DE DIBUJO =================
    def crear_herramientas(self):
        """Toolbar organizado en UNA SOLA FILA con grid()"""
        
        # Configurar columnas del grid
        for i in range(9):
            self.frame_herramientas.grid_columnconfigure(i, weight=0)
        
        # Fila 0 - Todos los botones y controles
        ctk.CTkButton(self.frame_herramientas, text="🎨 Color", 
                      command=self.elegir_color, width=90, height=40,
                      fg_color=self.color_boton_primario, corner_radius=8).grid(row=0, column=0, padx=5, pady=5)
        
        ctk.CTkButton(self.frame_herramientas, text="📷 Cámara", 
                      command=self.abrir_camara, width=90, height=40,
                      fg_color=self.color_boton_primario, corner_radius=8).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(self.frame_herramientas, text="↩️ Deshacer", 
                      command=self.deshacer, width=90, height=40,
                      fg_color=self.color_boton_secundario, corner_radius=8).grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkButton(self.frame_herramientas, text="↪️ Rehacer", 
                      command=self.rehacer, width=90, height=40,
                      fg_color=self.color_boton_secundario, corner_radius=8).grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkButton(self.frame_herramientas, text="🧹 Limpiar", 
                      command=self.limpiar_lienzo, width=90, height=40,
                      fg_color=self.color_boton_peligro, corner_radius=8).grid(row=0, column=4, padx=5, pady=5)
        
        ctk.CTkButton(self.frame_herramientas, text="💾 Guardar", 
                      command=self.guardar_imagen, width=90, height=40,
                      fg_color=self.color_boton_exito, corner_radius=8).grid(row=0, column=5, padx=5, pady=5)
        
        # Label Grosor
        ctk.CTkLabel(self.frame_herramientas, text="Grosor:", 
                     text_color="#a0a0a0").grid(row=0, column=6, padx=10, pady=5)
        
        # Slider
        self.size_slider = ctk.CTkSlider(self.frame_herramientas, from_=1, to=20, 
                                          width=120, height=20,
                                          command=self.cambiar_grosor,
                                          progress_color=self.color_boton_primario)
        self.size_slider.set(5)
        self.size_slider.grid(row=0, column=7, padx=5, pady=5)
        
        # Label Color Actual
        self.color_label = ctk.CTkLabel(self.frame_herramientas, text="⬛ Color", 
                                         font=ctk.CTkFont(size=11), text_color="#ffffff")
        self.color_label.grid(row=0, column=8, padx=10, pady=5)
        
        # Fila 1 - Historial
        self.history_label = ctk.CTkLabel(self.frame_herramientas, 
                                           text="📋 Historial: 0/0", 
                                           font=ctk.CTkFont(size=10), 
                                           text_color="#7f8c8d")
        self.history_label.grid(row=1, column=0, columnspan=9, pady=5)

    # ================= FUNCIONES DE DIBUJO =================
    def iniciar_dibujo(self, event):
        self.old_x = event.x
        self.old_y = event.y

    def dibujar(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=self.brush_size, fill=self.color,
                                    capstyle=tk.ROUND, smooth=True)
            self.old_x = event.x
            self.old_y = event.y

    def detener_dibujo(self, event):
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
        if self.canvas:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    self.canvas.postscript(file=file_path + ".eps", colormode='color')
                    # Convertir EPS a PNG si es necesario (opcional, requiere Pillow)
                    messagebox.showinfo("✅ Éxito", f"Imagen guardada en:\n{file_path}")
                    print(f"Imagen guardada en: {file_path}")
                except Exception as e:
                    messagebox.showerror("❌ Error", f"No se pudo guardar la imagen:\n{str(e)}")

    # ================= FUNCIONALIDAD DE CÁMARA =================
    def abrir_camara(self):
        if self.canvas is None:
            messagebox.showwarning("⚠️ Advertencia", "Primero crea un lienzo con 'Archivo > Nuevo'")
            return
        
        cam_window = ctk.CTkToplevel(self.root)
        cam_window.title("📷 Cámara Web")
        cam_window.geometry("680x580")
        cam_window.transient(self.root)
        
        cam_window.update_idletasks()
        x = (cam_window.winfo_screenwidth() // 2) - (680 // 2)
        y = (cam_window.winfo_screenheight() // 2) - (580 // 2)
        cam_window.geometry(f"680x580+{x}+{y}")
        
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
                
                messagebox.showinfo("✅ Foto Capturada", 
                    "La foto se cargó en el lienzo.\n\n¡Ahora puedes dibujar sobre ella!")
                
                is_capturing = False
                cap.release()
                cam_window.destroy()
            else:
                messagebox.showerror("❌ Error", "No se pudo capturar la foto")
        
        ctk.CTkButton(cam_window, text="📸 Capturar Foto", 
                      command=capturar_foto, fg_color=self.color_boton_primario,
                      width=200, height=40, font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10)
        
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

    # ================= DESHACER / REHACER =================
    def guardar_estado(self):
        if self.canvas is None:
            return
        
        estado = self.canvas.find_all()
        elementos = []
        
        for item in estado:
            coords = self.canvas.coords(item)
            tipo = self.canvas.type(item)
            
            if tipo == 'line':
                config = self.canvas.itemconfig(item)
                elementos.append({
                    'tipo': 'line',
                    'coords': coords,
                    'fill': config['fill'][4],
                    'width': config['width'][4],
                    'capstyle': config['capstyle'][4],
                    'smooth': config['smooth'][4]
                })
            elif tipo == 'image':
                if self.background_img:
                    elementos.append({
                        'tipo': 'image',
                        'imagen': self.background_img.copy()
                    })
        
        self.undo_stack.append(elementos)
        
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        
        self.redo_stack = []
        
        self.actualizar_history_label()
        
        print(f"Estado guardado. Historial: {len(self.undo_stack)}/{self.max_history}")

    def deshacer(self):
        if len(self.undo_stack) <= 1:
            messagebox.showinfo("ℹ️ Info", "No hay más acciones para deshacer")
            return
        
        estado_actual = self.undo_stack.pop()
        self.redo_stack.append(estado_actual)
        
        estado_anterior = self.undo_stack[-1]
        self.restaurar_estado(estado_anterior)
        
        self.actualizar_history_label()
        print(f"Deshacer. Historial: {len(self.undo_stack)}/{self.max_history}")

    def rehacer(self):
        if len(self.redo_stack) == 0:
            messagebox.showinfo("ℹ️ Info", "No hay más acciones para rehacer")
            return
        
        estado = self.redo_stack.pop()
        self.undo_stack.append(estado)
        
        self.restaurar_estado(estado)
        
        self.actualizar_history_label()
        print(f"Rehacer. Historial: {len(self.undo_stack)}/{self.max_history}")

    def restaurar_estado(self, estado):
        if self.canvas is None:
            return
        
        self.canvas.delete("all")
        
        for elemento in estado:
            if elemento['tipo'] == 'line':
                self.canvas.create_line(
                    elemento['coords'],
                    fill=elemento['fill'],
                    width=elemento['width'],
                    capstyle=elemento['capstyle'],
                    smooth=elemento['smooth']
                )
            elif elemento['tipo'] == 'image':
                if 'imagen' in elemento:
                    self.background_img = elemento['imagen'].copy()
                    self.imgtk = ImageTk.PhotoImage(image=self.background_img)
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)

    def actualizar_history_label(self):
        undo_count = len(self.undo_stack) - 1
        redo_count = len(self.redo_stack)
        self.history_label.configure(text=f"📋 Historial: {undo_count} disponibles | Rehacer: {redo_count}")

# ================= EJECUCIÓN =================
if __name__ == "__main__":
    root = ctk.CTk()
    app = PaintApp(root)
    root.mainloop()