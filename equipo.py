from servicio import Servicio          # heredamos de la clase abstracta Servicio
from excepciones import ServicioError  # para lanzar errores específicos del sistema
from logger import logger              # para registrar eventos importantes

# definimos los tipos de equipo válidos en el sistema como un conjunto
# usamos un conjunto (set) porque la búsqueda es más rápida que en una lista
TIPOS_EQUIPO = {"laptop", "proyector", "camara", "servidor", "tablet", "impresora"}


class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    Hereda de Servicio y maneja un inventario de unidades disponibles.
    El costo varía según el tipo de equipo y cuántas unidades se alquilan.
    """

    def __init__(self, id_servicio: str, nombre: str, precio_hora: float,
                 tipo_equipo: str, unidades_disponibles: int = 1):
        # llamamos al constructor padre para validar los campos comunes
        super().__init__(id_servicio, nombre, precio_hora,
                         f"Alquiler de {tipo_equipo}")
        self._tipo_equipo = self._validar_tipo(tipo_equipo)              # validamos que el tipo exista
        self._unidades_disponibles = self._validar_unidades(unidades_disponibles)  # validamos el inventario
        self._unidades_en_uso = 0  # al inicio ninguna unidad está siendo usada
        logger.info(f"Equipo creado: tipo={tipo_equipo}, unidades={unidades_disponibles}")

    # --- Propiedades ---

    @property
    def tipo_equipo(self):
        return self._tipo_equipo

    @property
    def unidades_disponibles(self):
        # las unidades disponibles son las totales menos las que están en uso
        return self._unidades_disponibles - self._unidades_en_uso

    @property
    def unidades_en_uso(self):
        return self._unidades_en_uso

    # --- Validaciones ---

    def _validar_tipo(self, tipo: str) -> str:
        tipo = tipo.strip().lower()  # limpiamos y convertimos a minúsculas para comparar
        if tipo not in TIPOS_EQUIPO:
            # si el tipo no está en nuestra lista, lanzamos un error explicando cuáles son válidos
            raise ServicioError(
                f"Tipo de equipo '{tipo}' no reconocido. "
                f"Tipos válidos: {', '.join(sorted(TIPOS_EQUIPO))}."
            )
        return tipo

    def _validar_unidades(self, unidades: int) -> int:
        try:
            unidades = int(unidades)  # convertimos a entero
        except (TypeError, ValueError) as e:
            raise ServicioError("Las unidades deben ser un número entero.") from e
        if unidades < 1:
            raise ServicioError(f"Debe haber al menos 1 unidad disponible. Recibido: {unidades}.")
        return unidades

    # --- Gestión del inventario ---

    def reservar_unidades(self, cantidad: int):
        """Descuenta unidades del inventario cuando se hace una reserva."""
        if cantidad > self.unidades_disponibles:
            # no podemos prestar más unidades de las que tenemos
            raise ServicioError(
                f"No hay suficientes unidades de '{self._nombre}'. "
                f"Disponibles: {self.unidades_disponibles}, solicitadas: {cantidad}."
            )
        self._unidades_en_uso += cantidad  # aumentamos el contador de unidades en uso

    def liberar_unidades(self, cantidad: int):
        """Devuelve unidades al inventario cuando se cancela o completa una reserva."""
        # usamos max(0,...) para evitar que el contador baje de cero
        self._unidades_en_uso = max(0, self._unidades_en_uso - cantidad)

    # --- Implementación del método abstracto heredado de Servicio ---

    def _calcular_costo_base(self, horas: float) -> float:
        """
        Calcula el costo según el tipo de equipo y las unidades en uso.
        Los servidores tienen un recargo del 30% por ser equipos de alto valor.
        Esto demuestra polimorfismo: cada servicio calcula diferente.
        """
        unidades = max(1, self._unidades_en_uso)  # mínimo 1 unidad para el cálculo
        costo = self._precio_hora * horas * unidades  # multiplicamos por las unidades alquiladas
        if self._tipo_equipo == "servidor":
            costo *= 1.30  # recargo del 30% para servidores por su alto valor
        return costo

    def validar_parametros(self, cantidad: int = 1, **kwargs) -> bool:
        """Verifica que haya suficientes unidades disponibles antes de hacer la reserva."""
        try:
            cantidad = int(cantidad)
            if cantidad < 1:
                raise ServicioError(f"La cantidad debe ser al menos 1. Recibido: {cantidad}.")
            # verificamos que tengamos suficiente inventario
            if cantidad > self.unidades_disponibles:
                raise ServicioError(
                    f"Solo hay {self.unidades_disponibles} unidades disponibles de '{self._nombre}'."
                )
            return True
        except ServicioError:
            raise
        except Exception as e:
            raise ServicioError(f"Error al validar parámetros de equipo: {e}") from e

    def describir(self) -> str:
        # agregamos la info del inventario a la descripción base
        base = super().describir()
        extras = (
            f"\n  Tipo equipo: {self._tipo_equipo.capitalize()}"
            f"\n  Disponibles: {self.unidades_disponibles} / {self._unidades_disponibles}"
            f"\n  Tipo       : Alquiler de equipo"
        )
        return base + extras

    def __str__(self):
        return f"Equipo({self._id}, {self._tipo_equipo}, {self.unidades_disponibles} disp.)"
