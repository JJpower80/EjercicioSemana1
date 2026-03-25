# Web News - Scraping con Flask, SQLite y BeautifulSoup

Proyecto académico para extraer noticias, guardarlas en SQLite y visualizarlas desde una interfaz web con Flask.

## Que hace este proyecto

- Extrae noticias desde Diario Sur.
- Guarda noticias en SQLite evitando duplicados por enlace.
- Muestra los datos en una vista web moderna.
- Permite lanzar el scraping desde la web con un boton.
- Incluye un flujo por consola para pruebas rapidas.

## Tecnologias

- Python
- Flask
- Requests
- BeautifulSoup4
- SQLite
- Bootstrap 5
- FPDF (script auxiliar para generar PDF)

## Estructura del proyecto

```text
Scraping Web News/
|- app.py                 # App Flask (interfaz web)
|- main.py                # Ejecucion por consola
|- scraper.py             # Logica de scraping
|- database.py            # Acceso y gestion de SQLite
|- generar_pdf.py         # Script auxiliar para crear PDF descriptivo
|- requirements.txt       # Dependencias
|- templates/
|  |- index.html          # Vista principal
|- static/
|  |- img/
|     |- logo.png
|- noticias.db            # Se crea automaticamente al ejecutar
`- README.md
```

## Instalacion

1. Clona el repositorio.
2. Entra en la carpeta del proyecto.
3. Instala dependencias:

```bash
pip install -r requirements.txt
```

Nota: si no tienes Flask o FPDF instalados en tu entorno, instalalos con:

```bash
pip install flask fpdf2
```

## Ejecucion

### Opcion A: interfaz web (recomendada)

```bash
python app.py
```

Despues abre en el navegador:

```text
http://127.0.0.1:5000/
```

Desde la interfaz puedes:

- Ver el total de noticias guardadas.
- Consultar las ultimas noticias.
- Pulsar Actualizar scraping para extraer nuevas noticias.

### Opcion B: script por consola

```bash
python main.py
```

Muestra por terminal el resultado del scraping y estadisticas de la base de datos.

## Endpoints de Flask

- GET /: pagina principal con las noticias.
- POST /actualizar: ejecuta scraping y redirige al inicio.
- GET /actualizar: redirige al inicio para evitar error 405 al refrescar.

## Base de datos

Tabla principal: noticias

- id
- titulo
- descripcion
- enlace (UNIQUE)
- fecha_publicacion
- fecha_scraping

Formato de descripcion para Diario Sur:

```text
AUTOR|||DESCRIPCION
```

La app web separa ese campo para mostrar autor y descripcion limpia.

## Personalizar scraping para otro sitio

Puedes usar el metodo extraer_noticias_personalizado(url, selectores) con selectores CSS:

```python
selectores = {
    "contenedor": ".article",
    "titulo": "h2",
    "enlace": "a",
    "descripcion": "p"
}
```

## Troubleshooting rapido

- Error 405 al refrescar: solucionado en la ruta /actualizar (ahora acepta GET y redirige).
- No encuentra noticias: revisa selectores y posibles cambios en el HTML del sitio.
- Timeout de red: comprueba conexion y vuelve a intentar.
- Modulo no encontrado: reinstala dependencias con requirements.txt.

## Consideraciones

- Respeta robots.txt y terminos de uso del sitio origen.
- Evita hacer demasiadas requests seguidas.
- El scraper ya aplica User-Agent y pequenas pausas para reducir bloqueos.
