import sqlite3
from datetime import datetime

class DatabaseManager:
    """Gestor de base de datos SQLite para almacenar noticias"""
    
    def __init__(self, db_name='noticias.db'):
        self.db_name = db_name
        self.crear_tabla()
    
    def crear_tabla(self):
        """Crea la tabla de noticias si no existe"""
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS noticias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    enlace TEXT UNIQUE,
                    fecha_publicacion TEXT,
                    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conexion.commit()
            print(f"✓ Base de datos '{self.db_name}' iniciada correctamente")
            
        except sqlite3.Error as e:
            print(f"✗ Error al crear tabla: {e}")
        finally:
            conexion.close()
    
    def insertar_noticia(self, titulo, descripcion, enlace, fecha_publicacion=None):
        """Inserta una noticia en la base de datos"""
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            
            cursor.execute('''
                INSERT INTO noticias (titulo, descripcion, enlace, fecha_publicacion)
                VALUES (?, ?, ?, ?)
            ''', (titulo, descripcion, enlace, fecha_publicacion))
            
            conexion.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            print(f"⚠ Noticia duplicada: {enlace}")
            return None
        except sqlite3.Error as e:
            print(f"✗ Error al insertar: {e}")
            return None
        finally:
            conexion.close()

    def guardar_o_actualizar_noticia(self, titulo, descripcion, enlace, fecha_publicacion=None):
        """Inserta una noticia o actualiza campos faltantes si ya existe por enlace"""
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()

            cursor.execute(
                '''
                SELECT id, titulo, descripcion, fecha_publicacion
                FROM noticias
                WHERE enlace = ?
                ''',
                (enlace,)
            )
            existente = cursor.fetchone()

            if not existente:
                cursor.execute(
                    '''
                    INSERT INTO noticias (titulo, descripcion, enlace, fecha_publicacion)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (titulo, descripcion, enlace, fecha_publicacion)
                )
                conexion.commit()
                return {"id": cursor.lastrowid, "insertado": True, "actualizado": False}

            noticia_id, titulo_actual, descripcion_actual, fecha_actual = existente

            nuevo_titulo = titulo or titulo_actual
            nueva_descripcion = descripcion_actual
            nueva_fecha = fecha_actual

            if descripcion and (
                not descripcion_actual
                or descripcion_actual.startswith("Sin autor|||")
                or "|||Sin descripción" in descripcion_actual
            ):
                nueva_descripcion = descripcion

            if fecha_publicacion and not fecha_actual:
                nueva_fecha = fecha_publicacion

            hay_cambios = (
                nuevo_titulo != titulo_actual
                or nueva_descripcion != descripcion_actual
                or nueva_fecha != fecha_actual
            )

            if hay_cambios:
                cursor.execute(
                    '''
                    UPDATE noticias
                    SET titulo = ?, descripcion = ?, fecha_publicacion = ?
                    WHERE id = ?
                    ''',
                    (nuevo_titulo, nueva_descripcion, nueva_fecha, noticia_id)
                )
                conexion.commit()

            return {"id": noticia_id, "insertado": False, "actualizado": hay_cambios}

        except sqlite3.Error as e:
            print(f"✗ Error al guardar o actualizar: {e}")
            return {"id": None, "insertado": False, "actualizado": False}
        finally:
            conexion.close()
    
    def obtener_noticias(self, limite=10):
        """Obtiene las últimas noticias de la base de datos"""
        try:
            conexion = sqlite3.connect(self.db_name)
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()
            
            cursor.execute('''
                SELECT * FROM noticias 
                ORDER BY fecha_scraping DESC 
                LIMIT ?
            ''', (limite,))
            
            noticias = cursor.fetchall()
            return noticias
            
        except sqlite3.Error as e:
            print(f"✗ Error al obtener noticias: {e}")
            return []
        finally:
            conexion.close()
    
    def contar_noticias(self):
        """Cuenta el total de noticias en la base de datos"""
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM noticias')
            total = cursor.fetchone()[0]
            return total
            
        except sqlite3.Error as e:
            print(f"✗ Error: {e}")
            return 0
        finally:
            conexion.close()
