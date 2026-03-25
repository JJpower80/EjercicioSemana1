from flask import Flask, render_template, redirect, url_for, flash, request
from database import DatabaseManager
from scraper import WebScraper

app = Flask(__name__)
app.secret_key = "dev-secret-key"

def preparar_noticias(noticias):
    resultado = []

    for noticia in noticias:
        noticia = dict(noticia)

        info_completa = noticia.get("descripcion", "") or ""
        autor = "Sin autor"
        descripcion = "Sin descripción"

        if "|||" in info_completa:
            partes = info_completa.split("|||", 1)
            autor = partes[0].strip() or "Sin autor"
            descripcion = partes[1].strip() or "Sin descripción"
        else:
            descripcion = info_completa or "Sin descripción"

        resultado.append({
            **noticia,
            "autor": autor,
            "descripcion_limpia": descripcion
        })

    return resultado

@app.route("/")
def index():
    db = DatabaseManager("noticias.db")
    noticias = db.obtener_noticias(5)
    total = db.contar_noticias()

    return render_template(
        "index.html",
        noticias=preparar_noticias(noticias),
        total=total
    )

@app.route("/actualizar", methods=["GET", "POST"])
def actualizar():
    if request.method == "GET":
        return redirect(url_for("index"))

    db = DatabaseManager("noticias.db")
    scraper = WebScraper(db)

    try:
        total_scraped = scraper.extraer_noticias_diariosur()
        flash(f"Se agregaron {total_scraped} noticias", "success")
    except Exception as e:
        flash(f"Error al scrapear: {e}", "danger")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)