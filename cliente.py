import re  # re es el módulo de expresiones regulares, lo usamos para validar correos y teléfonos
from entidad import Entidad  # importamos la clase base abstracta
from excepciones import ValidacionError, ClienteError  # importamos las excepciones que vamos a usar
from logger import logger    # importamos el logger para registrar eventos


class Cliente(Entidad):
    """
    Representa a un cliente de Software FJ.
    Hereda de Entidad e implementa encapsulación estricta con validaciones.
    """

    # definimos los patrones de validación como constantes de clase
    # así no los repetimos cada vez que validamos
    CORREO_REGEX = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")   # patrón para correos válidos
    TELEFONO_REGEX = re.compile(r"^\+?[\d\s\-]{7,15}$")                   # patrón para teléfonos válidos

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        try:
            super().__init__(id_cliente, nombre)  # llamamos al constructor de Entidad para validar id y nombre
            self._correo = self._validar_correo(correo)      # validamos y guardamos el correo
            self._telefono = self._validar_telefono(telefono) # validamos y guardamos el teléfono
            self._activo = True  # por defecto todo cliente nuevo está activo
            logger.info(f"Cliente creado: {id_cliente} | {nombre} | {correo}")  # registramos en el log
        except ValidacionError:
            raise  # si es un error de validación, lo dejamos subir sin modificarlo
        except Exception as e:
            # cualquier otro error inesperado lo envolvemos en un ClienteError con más contexto
            raise ClienteError(f"Error al crear cliente '{id_cliente}': {e}") from e

    # --- Propiedades (encapsulación) ---

    @property
    def correo(self):
        return self._correo  # retornamos el correo de forma controlada

    @correo.setter
    def correo(self, valor):
        # cuando alguien quiera cambiar el correo, primero lo validamos
        self._correo = self._validar_correo(valor)

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = self._validar_telefono(valor)

    @property
    def activo(self):
        return self._activo  # indica si el cliente está habilitado en el sistema

    # --- Métodos privados de validación ---

    def _validar_correo(self, correo: str) -> str:
        # primero verificamos que no venga vacío
        if not correo or not correo.strip():
            raise ValidacionError("correo", "No puede estar vacío.")
        correo = correo.strip().lower()  # lo limpiamos y convertimos a minúsculas
        # verificamos que tenga el formato correcto usando la expresión regular
        if not self.CORREO_REGEX.match(correo):
            raise ValidacionError("correo", f"Formato inválido: '{correo}'.")
        return correo  # si todo está bien, retornamos el correo limpio

    def _validar_telefono(self, telefono: str) -> str:
        if not telefono or not telefono.strip():
            raise ValidacionError("telefono", "No puede estar vacío.")
        telefono = telefono.strip()
        # verificamos que el teléfono tenga entre 7 y 15 dígitos con el formato correcto
        if not self.TELEFONO_REGEX.match(telefono):
            raise ValidacionError("telefono", f"Formato inválido: '{telefono}'.")
        return telefono

    # --- Métodos públicos ---

    def desactivar(self):
        """Marca el cliente como inactivo, es una baja lógica (no lo borramos del sistema)."""
        if not self._activo:
            # si ya estaba inactivo, no tiene sentido desactivarlo de nuevo
            raise ClienteError(f"El cliente '{self._id}' ya está inactivo.")
        self._activo = False
        logger.advertencia(f"Cliente desactivado: {self._id}")  # lo registramos como advertencia

    def activar(self):
        """Reactiva un cliente que estaba inactivo."""
        self._activo = True
        logger.info(f"Cliente reactivado: {self._id}")

    # --- Implementación de métodos abstractos heredados de Entidad ---

    def describir(self) -> str:
        # mostramos toda la información del cliente de forma organizada
        estado = "Activo" if self._activo else "Inactivo"
        return (
            f"Cliente: {self._nombre}\n"
            f"  ID      : {self._id}\n"
            f"  Correo  : {self._correo}\n"
            f"  Teléfono: {self._telefono}\n"
            f"  Estado  : {estado}\n"
            f"  Registro: {self._fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
        )

    def validar(self) -> bool:
        """Verifica que los datos del cliente siguen siendo válidos."""
        try:
            self._validar_correo(self._correo)
            self._validar_telefono(self._telefono)
            return True  # si no lanzó excepciones, todo está bien
        except ValidacionError:
            return False  # si alguna validación falla, retornamos False

    def __str__(self):
        return f"Cliente({self._id}, {self._nombre}, {self._correo})"
