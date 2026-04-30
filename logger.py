import os       # para crear la carpeta de logs si no existe
import logging  # módulo estándar de Python para manejar registros
from datetime import datetime  # por si necesitamos fechas en algún momento


class Logger:
    """
    Sistema centralizado de registro de eventos y errores.
    Usamos el patrón Singleton para que haya una sola instancia en todo el programa.
    Escribe en el archivo logs/eventos.log y también muestra mensajes en la consola.
    """

    _instancia = None  # guardamos la única instancia aquí (patrón Singleton)

    def __new__(cls):
        # __new__ se ejecuta antes que __init__, lo usamos para controlar la creación
        if cls._instancia is None:
            # solo creamos una nueva instancia si no existe ninguna todavía
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()  # configuramos el logger la primera vez
        return cls._instancia  # siempre retornamos la misma instancia

    def _inicializar(self):
        # creamos la carpeta logs/ si no existe, exist_ok=True evita error si ya existe
        os.makedirs("logs", exist_ok=True)

        # creamos el logger con el nombre de nuestro sistema
        self._logger = logging.getLogger("SoftwareFJ")
        self._logger.setLevel(logging.DEBUG)  # capturamos todos los niveles desde DEBUG en adelante

        if not self._logger.handlers:
            # --- Handler para archivo: guarda TODOS los mensajes en el archivo de log ---
            fh = logging.FileHandler("logs/eventos.log", encoding="utf-8")
            fh.setLevel(logging.DEBUG)  # guardamos todo, incluso los mensajes de debug
            fmt_archivo = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",  # formato: fecha | nivel | mensaje
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            fh.setFormatter(fmt_archivo)
            self._logger.addHandler(fh)  # añadimos el handler al logger

            # --- Handler para consola: solo muestra INFO en adelante ---
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)  # en consola no mostramos debug para no saturar
            fmt_consola = logging.Formatter("%(levelname)-8s | %(message)s")
            ch.setFormatter(fmt_consola)
            self._logger.addHandler(ch)

    # --- Métodos para registrar mensajes según su nivel de importancia ---

    def info(self, mensaje: str):
        """Para eventos normales del sistema, como crear un cliente o confirmar una reserva."""
        self._logger.info(mensaje)

    def advertencia(self, mensaje: str):
        """Para situaciones que no son errores pero merecen atención, como desactivar un servicio."""
        self._logger.warning(mensaje)

    def error(self, mensaje: str, excepcion: Exception = None):
        """Para errores que el sistema pudo manejar y recuperar."""
        if excepcion:
            # si nos pasan la excepción, incluimos el tipo y el mensaje en el log
            self._logger.error(f"{mensaje} | Excepción: {type(excepcion).__name__}: {excepcion}")
        else:
            self._logger.error(mensaje)

    def critico(self, mensaje: str, excepcion: Exception = None):
        """Para errores graves que podrían afectar el funcionamiento del sistema."""
        if excepcion:
            self._logger.critical(f"{mensaje} | Excepción: {type(excepcion).__name__}: {excepcion}")
        else:
            self._logger.critical(mensaje)

    def debug(self, mensaje: str):
        """Para mensajes de depuración, solo se ven en el archivo de log."""
        self._logger.debug(mensaje)

    def separador(self, titulo: str = ""):
        """Añade una línea separadora en el log para organizar mejor los eventos."""
        linea = "=" * 60
        if titulo:
            self._logger.info(f"{linea}")
            self._logger.info(f"  {titulo.upper()}")
            self._logger.info(f"{linea}")
        else:
            self._logger.info(linea)


# creamos la instancia global aquí para que todos los archivos la importen y usen la misma
logger = Logger()
