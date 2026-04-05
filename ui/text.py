import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

def activar_herramienta_texto(self):
        """Activa el modo de inserción de texto"""
        if self.canvas is None:
            messagebox.showwarning("⚠️ Sin lienzo", "Primero crea un lienzo con 'Archivo > Nuevo'")
            return
        
        # Abrir diálogo de configuración de texto
        config = self._dialogo_configurar_texto()
        if not config:
            return  # Usuario canceló
        
        self.text_config = config
        self.text_tool_active = True
        
        # CORRECCIÓN: Usar cursor "xterm" en lugar de "text"
        self.canvas.config(cursor="xterm")
        self.canvas.bind('<Button-1>', self._colocar_texto)
        
        messagebox.showinfo("✏️ Texto", 
            "Configuración aplicada.\n\nHaz click en el lienzo para colocar el texto.\nPresiona ESC para cancelar.",
            parent=self.root)
        
        # Bind para cancelar con ESC
        self.root.bind('<Escape>', lambda e: self._cancelar_texto())


def _cancelar_texto(self, event=None):
        """Desactiva el modo de inserción de texto"""
        self.text_tool_active = False
        if self.canvas:
            self.canvas.config(cursor="")  # Cursor normal
            self.canvas.bind('<Button-1>', self.iniciar_dibujo)
        try:
            self.root.unbind('<Escape>')
        except:
            pass


def _dialogo_configurar_texto(self):
        """Diálogo modal para configurar tamaño, color y tipografía del texto"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("✏️ Configurar Texto")
        dialog.geometry("450x570")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (570 // 2)
        dialog.geometry(f"450x+570{x}+{y}")
        
        # SOLUCIÓN: Esperar a que la ventana sea visible antes de hacer grab
        dialog.wait_visibility()  # Espera a que la ventana sea visible
        dialog.grab_set()         # Ahora sí funciona
        
        # Título
        ctk.CTkLabel(dialog, text="⚙️ Configuración de Texto", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # --- Tamaño de letra ---
        frame_size = ctk.CTkFrame(dialog)
        frame_size.pack(pady=10, fill=tk.X, padx=20)
        
        ctk.CTkLabel(frame_size, text="📏 Tamaño de letra:", 
                    font=ctk.CTkFont(size=13)).pack(pady=(10, 5))
        
        size_var = tk.StringVar(value="32 - Mediano")
        size_combo = ctk.CTkComboBox(frame_size, 
                                    values=["16 - Pequeño", "32 - Mediano", "64 - Grande"], 
                                    variable=size_var, 
                                    width=250, 
                                    state="readonly",
                                    font=ctk.CTkFont(size=12))
        size_combo.pack(pady=5, padx=20)
        
        # --- Color del texto ---
        frame_color = ctk.CTkFrame(dialog)
        frame_color.pack(pady=10, fill=tk.X, padx=20)
        
        ctk.CTkLabel(frame_color, text="🎨 Color del texto:", 
                    font=ctk.CTkFont(size=13)).pack(pady=(10, 5))
        
        color_var = tk.StringVar(value="#000000")
        
        def elegir_color():
            color = colorchooser.askcolor(title="🎨 Color del texto", initialcolor=color_var.get())[1]
            if color:
                color_var.set(color)
                color_preview.configure(fg_color=color)
        
        btn_frame = ctk.CTkFrame(frame_color, fg_color="transparent")
        btn_frame.pack(pady=5)
        
        color_preview = ctk.CTkButton(btn_frame, text="   ", width=40, height=30, 
                                    fg_color="#000000", state="disabled")
        color_preview.pack(side=tk.LEFT, padx=(20, 10))
        
        ctk.CTkButton(btn_frame, text="Elegir Color", command=elegir_color, 
                    width=150).pack(side=tk.LEFT, padx=10)
        
        # --- Tipografía ---
        frame_font = ctk.CTkFrame(dialog)
        frame_font.pack(pady=10, fill=tk.X, padx=20)
        
        ctk.CTkLabel(frame_font, text="🔤 Tipografía:", 
                    font=ctk.CTkFont(size=13)).pack(pady=(10, 5))
        
        fonts_available = ['Arial', 'Times New Roman', 'Courier New', 'Verdana', 
                        'Georgia', 'Comic Sans MS', 'Impact', 'Tahoma', 'Arial Black']
        font_var = tk.StringVar(value="Arial")
        
        font_combo = ctk.CTkComboBox(frame_font, values=fonts_available, 
                                    variable=font_var, 
                                    width=250, 
                                    state="readonly",
                                    font=ctk.CTkFont(size=12))
        font_combo.pack(pady=5, padx=20)
        
        # --- Vista previa ---
        preview_frame = ctk.CTkFrame(dialog, fg_color="#f0f0f0")
        preview_frame.pack(pady=20, fill=tk.X, padx=20)
        
        preview_label = ctk.CTkLabel(preview_frame, text="Paint Pro - Vista previa", 
                                    font=ctk.CTkFont(family="Arial", size=24),
                                    text_color="#000000")
        preview_label.pack(pady=15)
        
        def actualizar_preview(*args):
            try:
                size_map = {"16 - Pequeño": 16, "32 - Mediano": 32, "64 - Grande": 64}
                size = size_map.get(size_var.get(), 32)
                fam = font_var.get()
                col = color_var.get()
                preview_label.configure(text=f"Paint Pro - Vista previa", 
                                    font=ctk.CTkFont(family=fam, size=size),
                                    text_color=col)
            except Exception as e:
                print(f"Error en preview: {e}")
        
        size_var.trace_add('write', actualizar_preview)
        font_var.trace_add('write', actualizar_preview)
        color_var.trace_add('write', actualizar_preview)
        
        # --- Botones ---
        btn_container = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_container.pack(pady=20)
        
        resultado = {'cancelado': True}
        
        def aceptar():
            try:
                size_map = {"16 - Pequeño": 16, "32 - Mediano": 32, "64 - Grande": 64}
                resultado.update({
                    'size': size_map.get(size_var.get(), 32),
                    'color': color_var.get(),
                    'font': font_var.get(),
                    'cancelado': False
                })
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Configuración inválida: {str(e)}", parent=dialog)
        
        ctk.CTkButton(btn_container, text="✅ Aplicar", command=aceptar, 
                    fg_color="#28A745", hover_color="#218838",
                    width=120, height=35, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.LEFT, padx=15)
        
        ctk.CTkButton(btn_container, text="❌ Cancelar", command=dialog.destroy, 
                    fg_color="#DC3545", hover_color="#C82333",
                    width=120, height=35, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.LEFT, padx=15)
        
        # Esperar a que se cierre el diálogo
        dialog.wait_window()
        
        if resultado.get('cancelado', True):
            return None
        
        return {k: v for k, v in resultado.items() if k != 'cancelado'}

def _elegir_color_texto(self, color_var, btn_widget):
        """Abre selector de color y actualiza el botón"""
        color = colorchooser.askcolor(title="🎨 Color del texto", initialcolor=color_var.get())[1]
        if color:
            color_var.set(color)
            btn_widget.configure(fg_color=color, text_color=("white" if self._es_color_oscuro(color) else "black"))

def _es_color_oscuro(self, hex_color):
        """Determina si un color hex es oscuro para elegir contraste de texto"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            luminosidad = (0.299*r + 0.587*g + 0.114*b)
            return luminosidad < 128
        except:
            return True

def _colocar_texto(self, event):
        """Coloca texto preservando trazos (SIN postscript)"""
        if not self.text_tool_active:
            return
        
        texto = tk.simpledialog.askstring("✏️ Insertar Texto", 
                                        "Escribe el texto:", 
                                        parent=self.root,
                                        initialvalue="Texto")
        
        if not texto or not texto.strip():
            self._cancelar_texto()
            return
        
        try:
            # === PASO 1: Obtener imagen base con trazos ===
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
            
            # === PASO 3: Crear capa de texto ===
            txt_img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            
            # Cargar fuente (tu lógica original)
            try:
                font_paths = [
                    f"/usr/share/fonts/truetype/msttcorefonts/{self.text_config['font'].replace(' ', '_')}.ttf",
                    f"/usr/share/fonts/truetype/dejavu/{self.text_config['font'].replace(' ', '')}-Regular.ttf",
                    f"/usr/share/fonts/truetype/liberation/{self.text_config['font'].replace(' ', '')}-Regular.ttf",
                    f"/usr/share/fonts/TTF/{self.text_config['font'].replace(' ', '')}.ttf",
                    f"C:/Windows/Fonts/{self.text_config['font'].replace(' ', '')}.ttf",
                    f"C:/Windows/Fonts/{self.text_config['font']}.ttf",
                ]
                font_path = next((p for p in font_paths if os.path.exists(p)), None)
                pil_font = ImageFont.truetype(font_path, self.text_config['size']) if font_path else ImageFont.load_default()
            except:
                pil_font = ImageFont.load_default()
            
            # Dibujar texto
            txt_draw.text((event.x, event.y), texto, 
                        fill=self.text_config['color'], 
                        font=pil_font, 
                        anchor='lt')
            
            # === PASO 4: Combinar y actualizar ===
            base_img = Image.alpha_composite(base_img, txt_img).convert('RGB')
            self.background_img = base_img
            self.imgtk = ImageTk.PhotoImage(image=self.background_img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
            self.guardar_estado()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo agregar el texto:\n{str(e)}")
            print(f"❌ Error al insertar texto: {e}")
        
        self._cancelar_texto()