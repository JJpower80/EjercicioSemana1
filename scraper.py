import requests
from bs4 import BeautifulSoup
from database import DatabaseManager
import time

class WebScraper:
    """Scraper para obtener noticias de sitios web"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def obtener_html(self, url):
        """Obtiene el contenido HTML de una URL"""
        try:
            respuesta = requests.get(url, headers=self.headers, timeout=10)
            respuesta.raise_for_status()  # Lanza excepción si hay error HTTP
            return respuesta.text
        except requests.RequestException as e:
            print(f"✗ Error al obtener {url}: {e}")
            return None
    
    def parsear_html(self, html):
        """Parsea HTML con BeautifulSoup"""
        return BeautifulSoup(html, 'html.parser')
    
    def extraer_noticias_bbc(self, url='https://www.bbc.com/news'):
        """Ejemplo: extrae noticias de BBC News"""
        print(f"📰 Scrapeando: {url}")
        
        html = self.obtener_html(url)
        if not html:
            return 0
        
        soup = self.parsear_html(html)
        noticias_agregadas = 0
        
        # Buscar elementos de noticias (esto depende de la estructura del sitio)
        articulos = soup.find_all('a', {'data-testid': 'internal-link'}, limit=10)
        
        for articulo in articulos:
            try:
                titulo = articulo.get_text(strip=True)
                enlace = articulo.get('href', '')
                
                # Completar URL si es relativa
                if enlace and not enlace.startswith('http'):
                    enlace = 'https://www.bbc.com' + enlace
                
                if titulo and enlace:
                    noticia_id = self.db.insertar_noticia(
                        titulo=titulo,
                        descripcion='BBC News',
                        enlace=enlace
                    )
                    if noticia_id:
                        print(f"  ✓ {titulo[:50]}...")
                        noticias_agregadas += 1
                        
            except Exception as e:
                print(f"  ✗ Error procesando artículo: {e}")
            
            # Pequeña pausa para no sobrecargar el servidor
            time.sleep(0.5)
        
        return noticias_agregadas
    
    def extraer_noticias_diariosur(self, url='https://www.diariosur.es'):
        """Extrae noticias de Diario Sur (Málaga) - Solo 5 noticias con fecha y autor"""
        print(f"📰 Scrapeando Diario Sur: {url}")
        
        html = self.obtener_html(url)
        if not html:
            return 0
        
        soup = self.parsear_html(html)
        noticias_agregadas = 0
        
        # Buscar todos los enlaces que parecen ser noticias (terminan en -nt.html)
        enlaces_noticias = soup.find_all('a', href=lambda href: href and '-nt.html' in href)
        
        for enlace in enlaces_noticias[:5]:  # Solo 5 noticias
            try:
                titulo = enlace.get_text(strip=True)
                url_noticia = enlace.get('href', '')
                
                # Completar URL si es relativa
                if url_noticia and not url_noticia.startswith('http'):
                    url_noticia = 'https://www.diariosur.es' + url_noticia
                
                # Filtrar solo URLs válidas de Diario Sur
                if titulo and url_noticia and 'diariosur.es' in url_noticia:
                    # Intentar obtener descripción, autor y fecha
                    descripcion = 'Diario Sur'
                    autor = 'Sin autor'
                    fecha_publicacion = None
                    
                    # Buscar información adicional en el elemento padre
                    padre = enlace.parent
                    if padre:
                        # Buscar autor (normalmente en enlaces con clase autor)
                        autor_link = padre.find('a', href=lambda href: href and 'autor' in href)
                        if autor_link:
                            autor = autor_link.get_text(strip=True)
                        
                        # Buscar fecha (puede estar en diferentes formatos)
                        # Intentar buscar elementos con fechas
                        fecha_elem = padre.find('time') or padre.find(attrs={'datetime': True})
                        if fecha_elem:
                            fecha_publicacion = fecha_elem.get('datetime') or fecha_elem.get_text(strip=True)
                        
                        # Buscar párrafo con descripción
                        parrafo = padre.find_next('p')
                        if parrafo and len(parrafo.get_text(strip=True)) > 10:
                            desc_text = parrafo.get_text(strip=True)
                            # Limpiar la descripción removiendo el autor si está incluido
                            if autor != 'Sin autor' and autor in desc_text:
                                desc_text = desc_text.replace(f'{autor} |', '').replace(f'{autor}|', '').strip()
                            descripcion = desc_text[:200]  # Limitar longitud
                    
                    # Si no encontramos autor en el padre, buscar en elementos cercanos
                    if autor == 'Sin autor':
                        # Buscar en el contenedor más amplio
                        contenedor = enlace.find_parent(['div', 'article', 'li'])
                        if contenedor:
                            autor_link = contenedor.find('a', href=lambda href: href and 'autor' in href)
                            if autor_link:
                                autor = autor_link.get_text(strip=True)
                    
                    # Crear descripción limpia y guardar autor por separado en el formato
                    desc_limpia = descripcion
                    if autor != 'Sin autor':
                        # Si encontramos autor, limpiamos la descripción
                        if f'{autor}|' in desc_limpia:
                            desc_limpia = desc_limpia.replace(f'{autor}|', '').strip()
                        elif f'{autor} |' in desc_limpia:
                            desc_limpia = desc_limpia.replace(f'{autor} |', '').strip()
                    
                    # Guardar en formato especial para fácil parsing: "AUTOR|||DESCRIPCION"
                    info_completa = f"{autor}|||{desc_limpia}"
                    
                    noticia_id = self.db.insertar_noticia(
                        titulo=titulo,
                        descripcion=info_completa,
                        enlace=url_noticia,
                        fecha_publicacion=fecha_publicacion
                    )
                    if noticia_id:
                        print(f"  ✓ {titulo[:50]}...")
                        if autor != 'Sin autor':
                            print(f"    👤 {autor}")
                        if fecha_publicacion:
                            print(f"    📅 {fecha_publicacion}")
                        noticias_agregadas += 1
                        
            except Exception as e:
                print(f"  ✗ Error procesando artículo: {e}")
            
            # Pausa para no sobrecargar el servidor
            time.sleep(0.3)
        
        return noticias_agregadas
    
    def extraer_noticias_personalizado(self, url, selectores):
        """
        Extrae noticias usando selectores CSS personalizados
        
        Args:
            url: URL del sitio
            selectores: dict con keys 'contenedor', 'titulo', 'enlace', 'descripcion'
        """
        print(f"📰 Scrapeando: {url}")
        
        html = self.obtener_html(url)
        if not html:
            return 0
        
        soup = self.parsear_html(html)
        noticias_agregadas = 0
        
        # Buscar todos los contenedores
        contenedores = soup.select(selectores['contenedor'], limit=10)
        
        for contenedor in contenedores:
            try:
                # Extraer datos usando los selectores proporcionados
                titulo_elem = contenedor.select_one(selectores['titulo'])
                enlace_elem = contenedor.select_one(selectores['enlace'])
                descripcion_elem = contenedor.select_one(selectores.get('descripcion', ''))
                
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else 'Sin título'
                enlace = enlace_elem.get('href', '') if enlace_elem else ''
                descripcion = descripcion_elem.get_text(strip=True) if descripcion_elem else ''
                
                if titulo and enlace:
                    # Completar URL si es relativa
                    if not enlace.startswith('http'):
                        from urllib.parse import urljoin
                        enlace = urljoin(url, enlace)
                    
                    noticia_id = self.db.insertar_noticia(
                        titulo=titulo,
                        descripcion=descripcion,
                        enlace=enlace
                    )
                    if noticia_id:
                        print(f"  ✓ {titulo[:50]}...")
                        noticias_agregadas += 1
                        
            except Exception as e:
                print(f"  ✗ Error procesando artículo: {e}")
            
            time.sleep(0.5)
        
        return noticias_agregadas


# Ejemplo de uso
if __name__ == '__main__':
    # Inicializar
    db = DatabaseManager('noticias.db')
    scraper = WebScraper(db)
    
    # Opción 1: Usar scraper predefinido (BBC)
    # noticias = scraper.extraer_noticias_bbc()
    
    # Opción 2: Usar scraper personalizado
    # Necesitas inspeccionar el HTML del sitio y proporcionar los selectores CSS
    selectores = {
        'contenedor': 'article',  # Ajusta según el sitio
        'titulo': 'h2',           # Ajusta según el sitio
        'enlace': 'a',            # Ajusta según el sitio
        'descripcion': 'p'        # Ajusta según el sitio
    }
    
    # noticias = scraper.extraer_noticias_personalizado('https://ejemplo.com', selectores)
    
    # Ver noticias guardadas
    total = db.contar_noticias()
    print(f"\n📊 Total de noticias en base de datos: {total}")
    
    ultimas = db.obtener_noticias(5)
    print(f"\n📰 Últimas 5 noticias:")
    for noticia in ultimas:
        print(f"  - {noticia['titulo']}")
        print(f"    {noticia['enlace']}")
