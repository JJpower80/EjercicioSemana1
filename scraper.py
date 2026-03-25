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
            respuesta.raise_for_status()
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
        
        articulos = soup.find_all('a', {'data-testid': 'internal-link'}, limit=10)
        
        for articulo in articulos:
            try:
                titulo = articulo.get_text(strip=True)
                enlace = articulo.get('href', '')
                
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
            
            time.sleep(0.5)
        
        return noticias_agregadas
    
    def extraer_noticias_diariosur(self, url='https://www.diariosur.es'):
        """Extrae noticias de Diario Sur (Málaga) con mejor manejo de autor y fecha"""
        print(f"📰 Scrapeando Diario Sur: {url}")
        
        html = self.obtener_html(url)
        if not html:
            return 0
        
        soup = self.parsear_html(html)
        noticias_agregadas = 0
        
        # Buscar todos los enlaces que parecen ser noticias
        enlaces_noticias = soup.find_all('a', href=lambda href: href and '-nt.html' in href)
        
        for enlace in enlaces_noticias[:5]:
            try:
                titulo = enlace.get_text(strip=True)
                url_noticia = enlace.get('href', '')
                
                # Completar URL si es relativa
                if url_noticia and not url_noticia.startswith('http'):
                    url_noticia = 'https://www.diariosur.es' + url_noticia
                
                # Filtrar solo URLs válidas
                if not (titulo and url_noticia and 'diariosur.es' in url_noticia):
                    continue
                
                # Inicializar variables
                autor = None
                fecha_publicacion = None
                descripcion = None
                
                # Buscar en elemento padre y sus hermanos
                padre = enlace.parent
                
                if padre:
                    # Buscar AUTOR
                    for elem in padre.find_all('a'):
                        href = elem.get('href', '')
                        if 'autor' in href.lower():
                            autor_text = elem.get_text(strip=True)
                            if autor_text:
                                autor = autor_text
                                break
                    
                    # Buscar FECHA en elemento time o con atributo datetime
                    time_elem = padre.find('time')
                    if time_elem:
                        fecha_publicacion = time_elem.get('datetime') or time_elem.get_text(strip=True)
                    else:
                        # Buscar elemento con atributo datetime
                        elem_datetime = padre.find(attrs={'datetime': True})
                        if elem_datetime:
                            fecha_publicacion = elem_datetime.get('datetime')
                    
                    # Buscar DESCRIPCIÓN en párrafo siguiente
                    parrafo = padre.find_next('p')
                    if parrafo:
                        descripcion = parrafo.get_text(strip=True)
                
                # Si no encontramos en el padre, buscar en contenedor más amplio
                if not (autor or fecha_publicacion or descripcion):
                    contenedor = enlace.find_parent(['div', 'article', 'li', 'section'])
                    
                    if contenedor:
                        # Buscar AUTOR
                        if not autor:
                            for elem in contenedor.find_all('a'):
                                href = elem.get('href', '')
                                if 'autor' in href.lower():
                                    autor_text = elem.get_text(strip=True)
                                    if autor_text:
                                        autor = autor_text
                                        break
                        
                        # Buscar FECHA
                        if not fecha_publicacion:
                            time_elem = contenedor.find('time')
                            if time_elem:
                                fecha_publicacion = time_elem.get('datetime') or time_elem.get_text(strip=True)
                        
                        # Buscar DESCRIPCIÓN
                        if not descripcion:
                            parrafo = contenedor.find('p')
                            if parrafo:
                                descripcion = parrafo.get_text(strip=True)
                
                # Establecer valores por defecto
                autor = autor or "Sin autor"
                descripcion = descripcion or "Sin descripción"
                
                # Limpiar descripción si contiene el autor
                if autor != "Sin autor" and autor in descripcion:
                    descripcion = descripcion.replace(f'{autor}|', '').replace(f'{autor} |', '').strip()
                
                # Limitar longitud de descripción
                if len(descripcion) > 200:
                    descripcion = descripcion[:200].rstrip() + "..."
                
                # Guardar en formato: "AUTOR|||DESCRIPCIÓN"
                info_completa = f"{autor}|||{descripcion}"
                
                # Insertar en BD
                noticia_id = self.db.insertar_noticia(
                    titulo=titulo,
                    descripcion=info_completa,
                    enlace=url_noticia,
                    fecha_publicacion=fecha_publicacion
                )
                
                if noticia_id:
                    print(f"  ✓ {titulo[:50]}...")
                    if autor != "Sin autor":
                        print(f"    👤 {autor}")
                    if fecha_publicacion:
                        print(f"    📅 {fecha_publicacion}")
                    noticias_agregadas += 1
                        
            except Exception as e:
                print(f"  ✗ Error procesando artículo: {e}")
            
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
        
        contenedores = soup.select(selectores['contenedor'], limit=10)
        
        for contenedor in contenedores:
            try:
                # Extraer datos usando los selectores proporcionados
                titulo_elem = contenedor.select_one(selectores['titulo'])
                enlace_elem = contenedor.select_one(selectores['enlace'])
                descripcion_elem = contenedor.select_one(selectores.get('descripcion', ''))
                
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else None
                enlace = enlace_elem.get('href', '') if enlace_elem else None
                descripcion = descripcion_elem.get_text(strip=True) if descripcion_elem else "Sin descripción"
                
                if not titulo or not enlace:
                    continue
                
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
    db = DatabaseManager('noticias.db')
    scraper = WebScraper(db)
    
    selectores = {
        'contenedor': 'article',
        'titulo': 'h2',
        'enlace': 'a',
        'descripcion': 'p'
    }
    
    total = db.contar_noticias()
    print(f"\n📊 Total de noticias en base de datos: {total}")
    
    ultimas = db.obtener_noticias(5)
    print(f"\n📰 Últimas 5 noticias:")
    for noticia in ultimas:
        print(f"  - {noticia['titulo']}")
        print(f"    {noticia['enlace']}")