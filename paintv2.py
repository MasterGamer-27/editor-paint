import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, font
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
#import threading
#import os

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 FrameArt")
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
        
        # ================= VARIABLES PARA HERRAMIENTA TEXTO =================
        self.text_tool_active = False
        self.text_config = {'size': 24, 'color': '#000000', 'font': 'Arial'}
        
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
        
        # 📁 Archivo
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2B2B2B", fg="white")
        menubar.add_cascade(label="📁 Archivo", menu=file_menu)
        file_menu.add_command(label="📄 Nuevo Lienzo", command=self.nuevo_lienzo)
        file_menu.add_command(label="🖼️ Abrir Imagen", command=self.abrir_imagen)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Salir", command=self.salir_app)
        
        # 🔧 Filtros
        filtros_menu = tk.Menu(menubar, tearoff=0, bg="#2B2B2B", fg="white")
        menubar.add_cascade(label="🔧 Filtros", menu=filtros_menu)
        
        basicos_menu = tk.Menu(filtros_menu, tearoff=0, bg="#2B2B2B", fg="white")
        filtros_menu.add_cascade(label="✨ Filtros Básicos", menu=basicos_menu)
        basicos_menu.add_command(label="⚪ Escala de Grises", command=self.filtro_grises)
        basicos_menu.add_command(label="🔄 Negativo", command=self.filtro_negativo)
        basicos_menu.add_command(label="🔲 Pixelar", command=self.filtro_pixelado)
        basicos_menu.add_command(label="💫 Desenfoque", command=self.filtro_blur)
        basicos_menu.add_command(label="🔍 Nitidez", command=self.filtro_nitidez)

        # ⚙️ Ajustes (NUEVO MENÚ)
        ajustes_menu = tk.Menu(menubar, tearoff=0, bg="#2B2B2B", fg="white")
        menubar.add_cascade(label="⚙️ Ajustes", menu=ajustes_menu)
        ajustes_menu.add_command(label="🎚️ Brillo/Contraste/Saturación", command=self.abrir_ajustes)
        
        # Atajos de teclado
        self.root.bind('<Control-z>', lambda e: self.deshacer())
        self.root.bind('<Control-Z>', lambda e: self.deshacer())
        self.root.bind('<Control-y>', lambda e: self.rehacer())
        self.root.bind('<Control-Y>', lambda e: self.rehacer())
        self.root.bind('<Control-n>', lambda e: self.nuevo_lienzo())
        self.root.bind('<Control-s>', lambda e: self.guardar_imagen())
        self.root.bind('<Control-o>', lambda e: self.abrir_imagen())

    # ================= FILTROS BÁSICOS =================
    
    def _pil_to_cv2(self, pil_img):
        rgb = np.array(pil_img)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
    def _cv2_to_pil(self, cv2_img):
        rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    
    def _aplicar_filtro_a_background(self, filtro_func):
        """Aplica filtro a TODO el canvas (imagen + trazos) SIN postscript"""
        if self.canvas is None:
            messagebox.showwarning("⚠️ Sin lienzo", "Primero crea un lienzo con 'Archivo > Nuevo'")
            return
        
        try:
            # === PASO 1: Obtener imagen base ===
            if self.background_img:
                # Usar imagen de fondo existente
                base_img = self.background_img.copy().convert('RGBA')
            else:
                # Crear lienzo blanco si no hay imagen
                base_img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
            
            # === PASO 2: Dibujar trazos del pincel sobre la imagen ===
            draw = ImageDraw.Draw(base_img)
            
            # Obtener todos los objetos del canvas
            for item_id in self.canvas.find_all():
                if self.canvas.type(item_id) == 'line':
                    coords = self.canvas.coords(item_id)
                    config = self.canvas.itemconfig(item_id)
                    
                    # Extraer propiedades de la línea
                    fill_color = config['fill'][4]
                    width = int(float(config['width'][4]))
                    capstyle = config['capstyle'][4]  # 'round', 'butt', 'projecting'
                    
                    # Dibujar línea en PIL (mismos parámetros que Tkinter)
                    draw.line(coords, fill=fill_color, width=width, 
                            joint='round' if capstyle == 'round' else None)
            
            # === PASO 3: Convertir a OpenCV y aplicar filtro ===
            # Convertir a RGB para OpenCV (quitar canal alpha si existe)
            img_for_cv2 = base_img.convert('RGB')
            cv2_img = self._pil_to_cv2(img_for_cv2)
            
            # Aplicar el filtro
            resultado_cv2 = filtro_func(cv2_img)
            
            # === PASO 4: Actualizar canvas ===
            self.background_img = self._cv2_to_pil(resultado_cv2).convert('RGB')
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            
            # Guardar estado para deshacer
            self.guardar_estado()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo aplicar el filtro:\n{str(e)}")
            print(f"❌ Error en filtro: {e}")

    def filtro_grises(self):
        def _filtro(im):
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        self._aplicar_filtro_a_background(_filtro)
    
    def filtro_negativo(self):
        def _filtro(im):
            return 255 - im
        self._aplicar_filtro_a_background(_filtro)
    
    def filtro_pixelado(self, escala=15):
        def _filtro(im):
            h, w = im.shape[:2]
            small = cv2.resize(im, (max(1, w//escala), max(1, h//escala)), 
                              interpolation=cv2.INTER_LINEAR)
            return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        self._aplicar_filtro_a_background(_filtro)
    
    def filtro_blur(self):
        def _filtro(im):
            return cv2.GaussianBlur(im, (7, 7), 0)
        self._aplicar_filtro_a_background(_filtro)
    
    def filtro_nitidez(self):
        def _filtro(im):
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            return cv2.filter2D(im, -1, kernel)
        self._aplicar_filtro_a_background(_filtro)


    # ================= HERRAMIENTA TEXTO =================
    
    from ui.text import activar_herramienta_texto, _cancelar_texto, _dialogo_configurar_texto, _elegir_color_texto, _es_color_oscuro, _colocar_texto

    # ================= FUNCIONES DEL MENÚ =================
    
    from ui.lienzo import nuevo_lienzo, abrir_imagen, _ajustar_imagen_al_lienzo, salir_app, crear_lienzo

    # ================= HERRAMIENTAS Y FUNCIONES DE DIBUJO =================

    from ui.dibujo import crear_herramientas, iniciar_dibujo, dibujar, detener_dibujo, elegir_color, cambiar_grosor, limpiar_lienzo, guardar_imagen, _mostrar_carga, _proceso_guardado


    # ================= AJUSTES DE IMAGEN (BRILLO/CONTRASTE/SATURACIÓN) =================

    def abrir_ajustes(self):
        """Abre ventana de ajustes de brillo, contraste y saturación con vista previa en vivo"""
        if self.canvas is None:
            messagebox.showwarning("⚠️ Sin lienzo", "Primero crea un lienzo con 'Archivo > Nuevo'")
            return
        
        # === GUARDAR ESTADO ORIGINAL (para restaurar si cancela) ===
        estado_original = {
            'background_img': self.background_img.copy() if self.background_img else None,
            'canvas_items': []
        }
        
        for item_id in self.canvas.find_all():
            if self.canvas.type(item_id) == 'line':
                coords = self.canvas.coords(item_id)
                config = self.canvas.itemconfig(item_id)
                estado_original['canvas_items'].append({
                    'coords': coords,
                    'fill': config['fill'][4],
                    'width': config['width'][4],
                    'capstyle': config['capstyle'][4]
                })
        
        # Crear ventana de ajustes
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("⚙️ Ajustes de Imagen")
        dialog.geometry("450x550")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"450x550+{x}+{y}")
        
        dialog.wait_visibility()
        
        # Título
        ctk.CTkLabel(dialog, text="🎚️ Ajustes de Imagen", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # === Variables de los sliders ===
        brillo_var = tk.IntVar(value=0)
        contraste_var = tk.DoubleVar(value=1.0)
        saturacion_var = tk.DoubleVar(value=1.0)
        
        # Bandera para evitar recursión
        aplicando_en_vivo = [False]
        
        # === Slider Brillo ===
        frame_brillo = ctk.CTkFrame(dialog)
        frame_brillo.pack(pady=10, fill=tk.X, padx=20)
        
        ctk.CTkLabel(frame_brillo, text="☀️ Brillo:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        slider_brillo = ctk.CTkSlider(frame_brillo, from_=-100, to=100, 
                                    variable=brillo_var, width=300,
                                    command=lambda v: self._ajustes_en_vivo(
                                        brillo_var.get(), contraste_var.get(), 
                                        saturacion_var.get(), estado_original, aplicando_en_vivo))
        slider_brillo.set(0)
        slider_brillo.pack(pady=5)
        
        label_brillo = ctk.CTkLabel(frame_brillo, text="0", 
                                    font=ctk.CTkFont(size=12), text_color="#3B8ED0")
        label_brillo.pack()
        
        # === Slider Contraste ===
        frame_contraste = ctk.CTkFrame(dialog)
        frame_contraste.pack(pady=10, fill=tk.X, padx=20)
        
        ctk.CTkLabel(frame_contraste, text="◐ Contraste:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        slider_contraste = ctk.CTkSlider(frame_contraste, from_=0.5, to=2.0, 
                                        variable=contraste_var, width=300,
                                        command=lambda v: self._ajustes_en_vivo(
                                            brillo_var.get(), contraste_var.get(), 
                                            saturacion_var.get(), estado_original, aplicando_en_vivo))
        slider_contraste.set(1.0)
        slider_contraste.pack(pady=5)
        
        label_contraste = ctk.CTkLabel(frame_contraste, text="1.0", 
                                    font=ctk.CTkFont(size=12), text_color="#3B8ED0")
        label_contraste.pack()
        
        # === Slider Saturación ===
        frame_saturacion = ctk.CTkFrame(dialog)
        frame_saturacion.pack(pady=10, fill=tk.X, padx=20)
        
        ctk.CTkLabel(frame_saturacion, text="🎨 Saturación:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        slider_saturacion = ctk.CTkSlider(frame_saturacion, from_=0.0, to=2.0, 
                                        variable=saturacion_var, width=300,
                                        command=lambda v: self._ajustes_en_vivo(
                                            brillo_var.get(), contraste_var.get(), 
                                            saturacion_var.get(), estado_original, aplicando_en_vivo))
        slider_saturacion.set(1.0)
        slider_saturacion.pack(pady=5)
        
        label_saturacion = ctk.CTkLabel(frame_saturacion, text="1.0", 
                                        font=ctk.CTkFont(size=12), text_color="#3B8ED0")
        label_saturacion.pack()
        
        # === Actualizar labels ===
        def actualizar_labels(*args):
            label_brillo.configure(text=str(brillo_var.get()))
            label_contraste.configure(text=f"{contraste_var.get():.1f}")
            label_saturacion.configure(text=f"{saturacion_var.get():.1f}")
        
        brillo_var.trace_add('write', actualizar_labels)
        contraste_var.trace_add('write', actualizar_labels)
        saturacion_var.trace_add('write', actualizar_labels)
        
        # === Información ===
        info_label = ctk.CTkLabel(dialog, text="💡 Los cambios se ven en tiempo real", 
                                font=ctk.CTkFont(size=11), text_color="#888888")
        info_label.pack(pady=10)
        
        # === Botones ===
        btn_container = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_container.pack(pady=20)
        
        def aplicar_ajustes():
            # Confirmar cambios actuales (ya están aplicados en vivo)
            self.guardar_estado()  # Guardar en historial
            aplicando_en_vivo[0] = False
            dialog.destroy()
        
        def cancelar_ajustes():
            # Restaurar estado original
            aplicando_en_vivo[0] = True  # Evitar que se guarde estado durante restauración
            self.background_img = estado_original['background_img'].copy() if estado_original['background_img'] else None
            self.imgtk = ImageTk.PhotoImage(image=self.background_img) if self.background_img else None
            self.canvas.delete("all")
            if self.imgtk:
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            # Restaurar trazos
            for item in estado_original['canvas_items']:
                self.canvas.create_line(item['coords'], fill=item['fill'], 
                                    width=int(float(item['width'])), 
                                    capstyle=item['capstyle'], smooth=True)
            aplicando_en_vivo[0] = False
            dialog.destroy()
        
        def resetear_ajustes():
            brillo_var.set(0)
            contraste_var.set(1.0)
            saturacion_var.set(1.0)
            # Restaurar imagen original en vivo
            self._ajustes_en_vivo(0, 1.0, 1.0, estado_original, aplicando_en_vivo)
        
        ctk.CTkButton(btn_container, text="✅ Confirmar", command=aplicar_ajustes, 
                    fg_color="#28A745", hover_color="#218838",
                    width=130, height=35, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.LEFT, padx=10)
        
        ctk.CTkButton(btn_container, text="🔄 Reset", command=resetear_ajustes, 
                    fg_color="#3B8ED0", hover_color="#2C6FA8",
                    width=100, height=35, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.LEFT, padx=10)
        
        ctk.CTkButton(btn_container, text="❌ Cancelar", command=cancelar_ajustes, 
                    fg_color="#DC3545", hover_color="#C82333",
                    width=130, height=35, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.LEFT, padx=10)
        
        # Manejar cierre de ventana
        def on_close():
            cancelar_ajustes()
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        dialog.wait_window()

    def _vista_previa_ajustes(self, brillo, contraste, saturacion, preview_label):
        """Muestra vista previa de los ajustes (opcional, puede ser pesado)"""
        preview_label.configure(text=f"Brillo: {brillo} | Contraste: {contraste:.1f} | Saturación: {saturacion:.1f}")

    def _aplicar_ajustes_imagen(self, brillo, contraste, saturacion):
        """Aplica los ajustes a TODO el canvas (imagen + trazos + texto)"""
        if self.canvas is None:
            return
        
        try:
            # === PASO 1: Obtener imagen base con trazos y texto ===
            if self.background_img:
                base_img = self.background_img.copy().convert('RGBA')
            else:
                base_img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
            
            # === PASO 2: Dibujar trazos del pincel ===
            draw = ImageDraw.Draw(base_img)
            for item_id in self.canvas.find_all():
                if self.canvas.type(item_id) == 'line':
                    coords = self.canvas.coords(item_id)
                    config = self.canvas.itemconfig(item_id)
                    fill_color = config['fill'][4]
                    width = int(float(config['width'][4]))
                    capstyle = config['capstyle'][4]
                    draw.line(coords, fill=fill_color, width=width,
                            joint='round' if capstyle == 'round' else None)
            
            # === PASO 3: Convertir a OpenCV ===
            img_for_cv2 = base_img.convert('RGB')
            cv2_img = self._pil_to_cv2(img_for_cv2)
            
            # === PASO 4: Aplicar Brillo y Contraste ===
            # alpha = contraste, beta = brillo
            ajustado = cv2.convertScaleAbs(cv2_img, alpha=contraste, beta=brillo)
            
            # === PASO 5: Aplicar Saturación ===
            if saturacion != 1.0:
                hsv = cv2.cvtColor(ajustado, cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv[:,:,1] = np.clip(hsv[:,:,1] * saturacion, 0, 255)
                hsv = hsv.astype(np.uint8)
                ajustado = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # === PASO 6: Actualizar canvas ===
            self.background_img = self._cv2_to_pil(ajustado).convert('RGB')
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            
            # Guardar estado para deshacer
            self.guardar_estado()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudieron aplicar los ajustes:\n{str(e)}")
            print(f"❌ Error en ajustes: {e}")

    def _ajustes_en_vivo(self, brillo, contraste, saturacion, estado_original, aplicando_en_vivo):
        """Aplica ajustes en tiempo real mientras se mueven los sliders"""
        if self.canvas is None or aplicando_en_vivo[0]:
            return
        
        try:
            # === PASO 1: Obtener imagen base original ===
            if estado_original['background_img']:
                base_img = estado_original['background_img'].copy().convert('RGBA')
            else:
                base_img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
            
            # === PASO 2: Dibujar trazos del pincel originales ===
            draw = ImageDraw.Draw(base_img)
            for item in estado_original['canvas_items']:
                coords = item['coords']
                fill_color = item['fill']
                width = int(float(item['width']))
                capstyle = item['capstyle']
                draw.line(coords, fill=fill_color, width=width,
                        joint='round' if capstyle == 'round' else None)
            
            # === PASO 3: Convertir a OpenCV ===
            img_for_cv2 = base_img.convert('RGB')
            cv2_img = self._pil_to_cv2(img_for_cv2)
            
            # === PASO 4: Aplicar Brillo y Contraste ===
            ajustado = cv2.convertScaleAbs(cv2_img, alpha=contraste, beta=brillo)
            
            # === PASO 5: Aplicar Saturación ===
            if saturacion != 1.0:
                hsv = cv2.cvtColor(ajustado, cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv[:,:,1] = np.clip(hsv[:,:,1] * saturacion, 0, 255)
                hsv = hsv.astype(np.uint8)
                ajustado = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # === PASO 6: Actualizar canvas en vivo ===
            self.background_img = self._cv2_to_pil(ajustado).convert('RGB')
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            
            # NO guardar estado aquí (solo al confirmar)
            
        except Exception as e:
            print(f"❌ Error en ajustes en vivo: {e}")
    
    # ================= CÁMARA =================
    
    from ui.camara import abrir_camara
    
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
                    'tipo': 'line', 'coords': coords,
                    'fill': config['fill'][4], 'width': config['width'][4],
                    'capstyle': config['capstyle'][4], 'smooth': config['smooth'][4]
                })
            elif tipo == 'image':
                if self.background_img:
                    elementos.append({'tipo': 'image', 'imagen': self.background_img.copy()})
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
                self.canvas.create_line(elemento['coords'], fill=elemento['fill'],
                    width=elemento['width'], capstyle=elemento['capstyle'], smooth=elemento['smooth'])
            elif elemento['tipo'] == 'image':
                if 'imagen' in elemento:
                    self.background_img = elemento['imagen'].copy()
                    self.imgtk = ImageTk.PhotoImage(image=self.background_img)
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)

    def actualizar_history_label(self):
        undo_count = len(self.undo_stack) - 1
        redo_count = len(self.redo_stack)
        self.history_label.configure(text=f"📋 Historial: {undo_count} disponibles | Rehacer: {redo_count}")
