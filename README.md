# 🕷️ Web Scraper con Python

Proyecto de web scraping con **BeautifulSoup**, **Requests** y **SQLite**.

## 📦 Instalación

```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
Scraping Web News/
├── requirements.txt      # Dependencias del proyecto
├── database.py          # Gestor de base de datos SQLite
├── scraper.py           # Clase para hacer scraping
├── main.py              # Script principal
├── noticias.db          # Base de datos (se crea automáticamente)
└── README.md            # Este archivo
```

## 🚀 Uso

### Opción 1: Ejecutar el script principal (Diario Sur)

```bash
python main.py
```

Este comando extrae automáticamente **5 noticias** de Diario Sur con:
- ✅ Título de la noticia
- ✅ Autor (cuando está disponible)
- ✅ Descripción breve
- ✅ Enlace completo
- ✅ Fecha de publicación (si está disponible)
- ✅ Fecha de scraping

### Opción 2: Usar en tu propio script

```python
from scraper import WebScraper
from database import DatabaseManager

# Inicializar
db = DatabaseManager('noticias.db')
scraper = WebScraper(db)

# Scrapear 5 noticias de Diario Sur
scraper.extraer_noticias_diariosur()

# Ver noticias
noticias = db.obtener_noticias(5)
for noticia in noticias:
    print(f"Título: {noticia['titulo']}")
    # La descripción contiene "AUTOR|||DESCRIPCION"
    info = noticia['descripcion'].split('|||')
    autor = info[0] if len(info) > 0 else 'Sin autor'
    descripcion = info[1] if len(info) > 1 else ''
    print(f"Autor: {autor}")
    print(f"Descripción: {descripcion}")
```

## 🔍 Cómo Scrapear Otros Sitios

### Pasos:

1. **Inspecciona el sitio web**: Abre el sitio en navegador y presiona `F12` (Herramientas de Desarrollo)

2. **Identifica los selectores CSS**:
   - Right-click en el elemento → "Inspeccionar"
   - Busca los selectores CSS para:
     - Contenedor del artículo
     - Título
     - Enlace
     - Descripción

3. **Usa el scraper personalizado**:

```python
selectores = {
    'contenedor': '.article',        # Selector de cada artículo
    'titulo': '.headline',           # Selector del título
    'enlace': 'a.article-link',     # Selector del enlace
    'descripcion': '.summary'        # Selector de descripción
}

scraper.extraer_noticias_personalizado(
    'https://ejemplo.com/noticias',
    selectores
)
```

## 📚 Componentes Principales

### DatabaseManager
- `crear_tabla()`: Crea la tabla en SQLite
- `insertar_noticia()`: Guarda una noticia
- `obtener_noticias()`: Recupera noticias
- `contar_noticias()`: Cuenta total de noticias

### WebScraper
- `obtener_html()`: Descarga contenido HTML
- `parsear_html()`: Parsea con BeautifulSoup
- `extraer_noticias_diariosur()`: **Nuevo** - Extrae 5 noticias de Diario Sur con autor y fecha
- `extraer_noticias_bbc()`: Ejemplo con BBC News
- `extraer_noticias_personalizado()`: Para cualquier sitio con selectores CSS

## ⚙️ Configuración

### Headers HTTP
```python
self.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### Delays
```python
time.sleep(0.5)  # Pausa entre requests para no sobrecargar servidores
```

## 🛡️ Consideraciones Éticas

- ✅ Respeta el archivo `robots.txt` del sitio
- ✅ No hagas demasiadas requests por segundo
- ✅ Verifica los términos de servicio del sitio
- ✅ Usa User-Agent adecuado
- ✅ Identifícate si el sitio lo requiere

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'bs4'"
```bash
pip install beautifulsoup4
```

### Error: "Connection timeout"
- Incrementa el delay entre requests
- Verifica tu conexión a internet

### No se encuentran elementos
- Recarga el sitio y revisa los selectores CSS
- Algunos sitios usan JavaScript (necesitarías Selenium)

## 📝 Notas

- SQLite se crea automáticamente
- Los duplicados se ignoran (enlace UNIQUE)
- Las fechas de scraping se guardan automáticamente

## 📚 Recursos

- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Docs](https://requests.readthedocs.io/)
- [SQLite Docs](https://www.sqlite.org/docs.html)
