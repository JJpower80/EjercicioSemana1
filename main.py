"""
Script principal para ejecutar el web scraper
"""
from scraper import WebScraper
from database import DatabaseManager

def main():
    # Inicializar manager de base de datos
    db = DatabaseManager('noticias.db')
    
    # Inicializar scraper
    scraper = WebScraper(db)
    
    print("=" * 60)
    print("🕷️  WEB SCRAPER CON BEAUTIFULSOUP, REQUESTS Y SQLITE")
    print("=" * 60)
    
    # Ejemplo 1: Buscar noticias en Diario Sur
    print("\n1️⃣  Scrapeando Diario Sur...")
    try:
        total_scraped = scraper.extraer_noticias_diariosur()
        print(f"   ✓ Se agregaron {total_scraped} noticias")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Ejemplo 2: Buscar noticias en otro sitio (personalizado)
    # Descomenta esto y ajusta los selectores según el sitio web que quieras scrapear
    """
    print("\n2️⃣  Scrapeando sitio personalizado...")
    selectores = {
        'contenedor': '.article',
        'titulo': '.article-title',
        'enlace': 'a.article-link',
        'descripcion': '.article-excerpt'
    }
    total_scraped = scraper.extraer_noticias_personalizado(
        'https://tudominio.com/noticias', 
        selectores
    )
    print(f"   ✓ Se agregaron {total_scraped} noticias")
    """
    
    # Mostrar estadísticas
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS:")
    print("=" * 60)
    total = db.contar_noticias()
    print(f"Total de noticias en BD: {total}")
    
    print(f"\n📰 Últimas 5 noticias:")
    noticias = db.obtener_noticias(5)
    for i, noticia in enumerate(noticias, 1):
        print(f"\n{i}. 📌 {noticia['titulo']}")
        
        # Parsear autor y descripción del campo descripcion
        info_completa = noticia['descripcion']
        autor_display = "Sin autor"
        descripcion_display = "Sin descripción"
        
        if "|||" in info_completa:
            partes = info_completa.split("|||", 1)
            autor_display = partes[0].strip()
            descripcion_display = partes[1].strip()
        else:
            descripcion_display = info_completa
        
        print(f"   👤 Autor: {autor_display}")
        print(f"   📝 {descripcion_display}")
        print(f"   🔗 {noticia['enlace']}")
        if noticia['fecha_publicacion']:
            print(f"   📅 Publicado: {noticia['fecha_publicacion']}")
        print(f"   🕒 Scraped: {noticia['fecha_scraping']}")
        print(f"   {'─' * 60}")

if __name__ == '__main__':
    main()
