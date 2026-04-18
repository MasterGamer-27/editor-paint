<h1 align="center">🎨 FrameArt</h1>
<img width="1339" height="829" alt="Captura de pantalla 2026-04-18 130543" src="https://github.com/user-attachments/assets/aed0bf11-8b1a-419b-b98a-6616bca23d79" />
<br>
FrameArt es una aplicación de escritorio desarrollada en Python para la edición interactiva de imágenes. Combina herramientas de dibujo estilo Paint con funcionalidades de procesamiento basadas en visión artificial, ofreciendo una experiencia completa en un solo entorno.

Permite crear y editar lienzos digitales de forma intuitiva, aplicar filtros como pixelado, desenfoque y nitidez, y ajustar en tiempo real parámetros como brillo, contraste y saturación. Además, incluye la opción de capturar imágenes desde la cámara web e integrarlas directamente en el lienzo.

Para facilitar el flujo de trabajo, cuenta con un sistema de deshacer y rehacer acciones. Su interfaz, desarrollada con CustomTkinter, presenta un diseño moderno y fácil de usar, adaptado tanto para principiantes como para usuarios más experimentados.
<br>
> **Nota:** Este proyecto no utiliza base de datos. Las imágenes se guardan localmente en formatos PNG/JPG según selección del usuario.
<h2>Funcionalidades</h2>


- **Dibujo libre**: Pincel con selección de color y grosor ajustable
- **Gestión de imágenes**: Abrir, guardar y crear nuevos lienzos
- **Filtros básicos**:
  - Escala de grises
  - Negativo
  - Pixelado
  - Desenfoque gaussiano
  - Nitidez (sharpen)
- **Ajustes en vivo**: Brillo, contraste y saturación con vista previa en tiempo real
- **Herramienta de texto**: Inserción de texto con fuente, tamaño y color personalizables
- **Cámara**: Captura de imagen desde webcam para usar como fondo
- **Historial**: Deshacer/rehacer con atajos de teclado (`Ctrl+Z` / `Ctrl+Y`)

<h2>Instalación y Ejecución</h2>

<h4>1. Requisitos previos</h4>
<p>Asegúrate de tener instalado:</p>
<ul>
  <li><b>Python 3.10 o superior</b></li>
  <li><b>pip</b> (incluido con Python)</li>
</ul>

<p>Verifica tu instalación con:</p>
<pre><code>python --version
pip --version</code></pre>

<hr>

<h4>2. Clonar el repositorio</h4>
<pre><code>git clone https://github.com/tu-usuario/frameart.git
</code></pre>

<hr>

<h4>3. Crear entorno virtual (recomendado)</h4>

<p><b>En Windows:</b></p>
<pre><code>python -m venv venv
venv\Scripts\activate</code></pre>

<p><b>En Linux / Mac:</b></p>
<pre><code>python3 -m venv venv
source venv/bin/activate</code></pre>

<hr>

<h4>4. Instalar dependencias</h4>
<p>Instala todas las librerías necesarias:</p>

<pre><code>pip install opencv-python pillow customtkinter numpy</code></pre>

<p><b>Opcional:</b> puedes crear un archivo <code>requirements.txt</code> con:</p>

<pre><code>pip freeze &gt; requirements.txt</code></pre>

<p>Y luego instalar con:</p>

<pre><code>pip install -r requirements.txt</code></pre>

<hr>

<h4>5. Ejecutar la aplicación</h4>

<pre><code>python main.py</code></pre>

<p></p>

<hr>

<h3>Permisos importantes</h3>
<ul>
  <li><b>Windows:</b> Permitir acceso a la cámara en Configuración de privacidad</li>
  <li><b>Linux:</b> Verificar permisos de <code>/dev/video0</code></li>
  <li><b>Mac:</b> Dar permisos de cámara al terminal o IDE</li>
</ul>

<hr>

<h4>Solución de problemas comunes</h4>

<p> <b>Error: No module named PIL</b></p>
<pre><code>pip install pillow</code></pre>

<p><b>Error con OpenCV</b></p>
<pre><code>pip install opencv-python</code></pre>

<p><b>La cámara no funciona</b></p>
<ul>
  <li>Verifica que no esté siendo usada por otra aplicación</li>
  <li>Prueba cambiar:</li>
</ul>

<pre><code>cv2.VideoCapture(0)</code></pre>

<p>por:</p>

<pre><code>cv2.VideoCapture(1)</code></pre>

<hr>

<p><b></b></p>


<h2>Tecnologías</h2>
<br>
<table>
  <thead>
    <tr>
      <th>Tecnología</th>
      <th>Propósito</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Python 3.8+</td>
      <td>Lenguaje base</td>
    </tr>
    <tr>
      <td>CustomTkinter</td>
      <td>Interfaz gráfica moderna con soporte para tema oscuro</td>
    </tr>
    <tr>
      <td>OpenCV</td>
      <td>Procesamiento de imágenes y filtros</td>
    </tr>
    <tr>
      <td>Pillow (PIL)</td>
      <td>Manipulación de imágenes y conversión de formatos</td>
    </tr>
    <tr>
      <td>NumPy</td>
      <td>Operaciones matriciales para ajustes de imagen</td>
    </tr>
    <tr>
      <td>Tkinter</td>
      <td>Diálogos nativos (color, archivos, mensajes)</td>
    </tr>
  </tbody>
</table>

<h2 align="center">Autores</h2>

<p >
   <b>Cristrian</b><br>
    Ingeniero en *****

  <b>Carlos</b><br>
  Ingeniero en ******
  
  <b>Franklin Dario Ramirez Diaz</b><br>
  Ingeniero en Desarrollo de Aplicaciones
</p>
