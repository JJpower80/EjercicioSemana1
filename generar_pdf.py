from pathlib import Path
from fpdf import FPDF

content = '''Descripción general del proyecto

Estructura de archivos:
- main.py: punto de entrada principal.
- scraper.py: lógica de extracción web (scraper).
- database.py: gestión de base de datos SQLite.

database.py:
- DatabaseManager crea tabla y gestiona insertar/obtener/contar noticias.
- Esquema: id, titulo, descripcion, enlace (UNIQUE), fecha_publicacion, fecha_scraping.

scraper.py:
- Clase WebScraper con métodos: obtener_html, parsear_html, extraer_noticias_bbc, extraer_noticias_diariosur, extraer_noticias_personalizado.
- Usa requests+BeautifulSoup + pausas (sleep) para respetar servidores.
- Modelo: toma texto de enlace/nodo, guarda en BD con campos.

main.py:
- Inicializa DB y scraper.
- Llama a extraer_noticias_diariosur (5 noticias) y muestra estadísticas.
- Muestra últimas 5 noticias en consola con parseo de autor y descripción.

Flujo general:
1. python main.py
2. Extraer noticias web
3. Guardar en SQLite
4. Mostrar resumen y últimos registros.

Recomendaciones:
- Ajustar selectores si cambian estructuras web.
- Probar scraper personal con selectores CSS.
- Duplicados gestionados por clave UNIQUE en enlace.
'''

pdf_path = Path('descripcion_proyecto.pdf')

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Descripcion del Proyecto', ln=1)

pdf.set_font('Arial', '', 11)
for line in content.split('\n'):
    pdf.multi_cell(0, 8, line)

pdf.output(str(pdf_path))
print(f'PDF generado: {pdf_path.resolve()}')
