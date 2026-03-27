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

    def _obtener_meta_contenido(self, soup, candidatos):
        """Devuelve el contenido del primer meta tag que coincida"""
        for attrs in candidatos:
            meta = soup.find('meta', attrs=attrs)
            if meta:
                contenido = (meta.get('content') or '').strip()
                if contenido:
                    return contenido
        return None

    def _extraer_detalle_noticia(self, url_noticia):
        """Extrae autor, fecha y descripcion desde la pagina de detalle"""
        html = self.obtener_html(url_noticia)
        if not html:
            return None, None, None

        soup = self.parsear_html(html)

        autor = self._obtener_meta_contenido(soup, [
            {'name': 'author'},
            {'property': 'article:author'},
            {'name': 'parsely-author'},
            {'name': 'twitter:creator'}
        ])

        if not autor:
            autor_elem = (
                soup.select_one('a[rel="author"]')
                or soup.select_one('[itemprop="author"]')
                or soup.select_one('.author')
                or soup.select_one('.article-author')
            )
            if autor_elem:
                autor = autor_elem.get_text(strip=True)

        fecha_publicacion = self._obtener_meta_contenido(soup, [
            {'property': 'article:published_time'},
            {'property': 'og:published_time'},
            {'name': 'pubdate'},
            {'name': 'date'}
        ])

        if not fecha_publicacion:
            time_elem = soup.find('time')
            if time_elem:
                fecha_publicacion = time_elem.get('datetime') or time_elem.get_text(strip=True)

        descripcion = self._obtener_meta_contenido(soup, [
            {'name': 'description'},
            {'property': 'og:description'}
        ])

        if not descripcion:
            parrafo = (
                soup.select_one('article p')
                or soup.select_one('main p')
                or soup.find('p')
            )
            if parrafo:
                descripcion = parrafo.get_text(strip=True)

        return autor, fecha_publicacion, descripcion
    
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
        
        noticias_actualizadas = 0

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
                
                # Completar datos desde la noticia completa para mejorar cobertura
                autor_detalle, fecha_detalle, descripcion_detalle = self._extraer_detalle_noticia(url_noticia)

                if (not autor or autor == "Sin autor") and autor_detalle:
                    autor = autor_detalle
                if not fecha_publicacion and fecha_detalle:
                    fecha_publicacion = fecha_detalle
                if (not descripcion or descripcion == "Sin descripción") and descripcion_detalle:
                    descripcion = descripcion_detalle

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
                resultado = self.db.guardar_o_actualizar_noticia(
                    titulo=titulo,
                    descripcion=info_completa,
                    enlace=url_noticia,
                    fecha_publicacion=fecha_publicacion
                )
                
                if resultado.get("insertado"):
                    print(f"  ✓ {titulo[:50]}...")
                    if autor != "Sin autor":
                        print(f"    👤 {autor}")
                    if fecha_publicacion:
                        print(f"    📅 {fecha_publicacion}")
                    noticias_agregadas += 1
                elif resultado.get("actualizado"):
                    print(f"  ↻ Actualizada: {titulo[:50]}...")
                    noticias_actualizadas += 1
                        
            except Exception as e:
                print(f"  ✗ Error procesando artículo: {e}")
            
            time.sleep(0.3)
        
        if noticias_actualizadas:
            print(f"  ℹ Noticias actualizadas con mas datos: {noticias_actualizadas}")

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