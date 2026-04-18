# 🎨 FrameArt
<img width="1339" height="829" alt="image" src="https://github.com/user-attachments/assets/870c1e73-20cc-4235-8087-011d71700cf7" />

Editor de imágenes de escritorio desarrollado en Python con interfaz moderna y herramientas de dibujo y procesamiento.

> **Nota:** Este proyecto no utiliza base de datos. Las imágenes se guardan localmente en formatos PNG/JPG según selección del usuario.

## ✨ Funcionalidades

- 🖌️ **Dibujo libre**: Pincel con selección de color y grosor ajustable
- 🖼️ **Gestión de imágenes**: Abrir, guardar y crear nuevos lienzos
- 🔧 **Filtros básicos**:
  - Escala de grises
  - Negativo
  - Pixelado
  - Desenfoque gaussiano
  - Nitidez (sharpen)
- ⚙️ **Ajustes en vivo**: Brillo, contraste y saturación con vista previa en tiempo real
- 🔤 **Herramienta de texto**: Inserción de texto con fuente, tamaño y color personalizables
- 📷 **Cámara**: Captura de imagen desde webcam para usar como fondo
- ↩️ **Historial**: Deshacer/rehacer con atajos de teclado (`Ctrl+Z` / `Ctrl+Y`)

## 🛠️ Tecnologías

| Tecnología | Propósito |
|------------|-----------|
| Python 3.8+ | Lenguaje base |
| CustomTkinter | Interfaz gráfica moderna con soporte para tema oscuro |
| OpenCV | Procesamiento de imágenes y filtros |
| Pillow (PIL) | Manipulación de imágenes y conversión de formatos |
| NumPy | Operaciones matriciales para ajustes de imagen |
| Tkinter | Diálogos nativos (color, archivos, mensajes) |

## 📦 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. Clonar el repositorio:
```bash
git clone https://github.com/MasterGamer-27/editor-paint.git
cd editor-paint
