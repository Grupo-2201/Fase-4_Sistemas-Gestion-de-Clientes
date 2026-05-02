from servicio import Servicio          # heredamos de la clase abstracta Servicio
from excepciones import ServicioError  # importamos la excepción para errores de servicio
from logger import logger              # importamos el logger para registrar eventos


class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones o conferencias.
    Hereda de Servicio e implementa su propia lógica de costo según
    la capacidad de la sala y si tiene proyector o no.
    """

    # definimos los límites de capacidad como constantes de clase
    CAPACIDAD_MINIMA = 2    # mínimo 2 personas para que tenga sentido reservar una sala
    CAPACIDAD_MAXIMA = 100  # máximo 100 personas

    def __init__(self, id_servicio: str, nombre: str, precio_hora: float,
                 capacidad: int, tiene_proyector: bool = False):
        # llamamos al constructor de Servicio para validar id, nombre y precio
        super().__init__(id_servicio, nombre, precio_hora,
                         f"Sala para {capacidad} personas")
        self._capacidad = self._validar_capacidad(capacidad)  # validamos que la capacidad sea válida
        self._tiene_proyector = tiene_proyector  # guardamos si la sala tiene proyector
        logger.info(f"Sala creada: capacidad={capacidad}, proyector={tiene_proyector}")

    # --- Propiedades ---

    @property
    def capacidad(self):
        return self._capacidad  # retornamos la capacidad máxima de la sala

    @property
    def tiene_proyector(self):
        return self._tiene_proyector  # retornamos si la sala tiene proyector

    # --- Validaciones ---

    def _validar_capacidad(self, capacidad: int) -> int:
        try:
            capacidad = int(capacidad)  # intentamos convertir a entero por si viene como string
        except (TypeError, ValueError) as e:
            raise ServicioError("La capacidad debe ser un número entero.") from e
        # verificamos que la capacidad esté dentro del rango permitido
        if not (self.CAPACIDAD_MINIMA <= capacidad <= self.CAPACIDAD_MAXIMA):
            raise ServicioError(
                f"Capacidad inválida: {capacidad}. "
                f"Rango permitido: {self.CAPACIDAD_MINIMA}-{self.CAPACIDAD_MAXIMA}."
            )
        return capacidad

    # --- Implementación del método abstracto heredado de Servicio ---

    def _calcular_costo_base(self, horas: float) -> float:
        """
        Calcula el costo base de la sala según sus características:
        - Si tiene proyector se cobra un 20% adicional
        - Si la sala es grande (más de 20 personas) se cobra un 15% adicional
        Esto es polimorfismo: cada servicio calcula su costo a su manera.
        """
        costo = self._precio_hora * horas  # costo básico: precio por hora multiplicado por las horas
        if self._tiene_proyector:
            costo *= 1.20  # recargo del 20% por uso del proyector
        if self._capacidad > 20:
            costo *= 1.15  # recargo del 15% por sala grande
        return costo

    def validar_parametros(self, asistentes: int = 1, **kwargs) -> bool:
        """
        Verifica que el número de asistentes no supere la capacidad de la sala.
        Se usa antes de confirmar una reserva para evitar sobrecupos.
        """
        try:
            asistentes = int(asistentes)
            if asistentes < 1:
                raise ServicioError(f"El número de asistentes debe ser al menos 1.")
            # verificamos que los asistentes quepan en la sala
            if asistentes > self._capacidad:
                raise ServicioError(
                    f"La sala '{self._nombre}' tiene capacidad para {self._capacidad} personas, "
                    f"pero se requieren {asistentes}."
                )
            return True  # si pasa todas las validaciones, retornamos True
        except ServicioError:
            raise  # dejamos subir los errores de servicio sin modificarlos
        except Exception as e:
            raise ServicioError(f"Error al validar parámetros de sala: {e}") from e

    def describir(self) -> str:
        # llamamos al describir() del padre y le agregamos la info específica de la sala
        base = super().describir()
        extras = (
            f"\n  Capacidad : {self._capacidad} personas"
            f"\n  Proyector : {'Sí' if self._tiene_proyector else 'No'}"
            f"\n  Tipo      : Reserva de sala"
        )
        return base + extras  # combinamos la descripción base con los extras

    def __str__(self):
        return f"Sala({self._id}, cap={self._capacidad}, proy={'✓' if self._tiene_proyector else '✗'})"
