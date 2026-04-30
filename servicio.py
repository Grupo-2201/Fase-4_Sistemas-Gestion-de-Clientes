from abc import abstractmethod  # necesitamos abstractmethod para definir métodos que las clases hijas deben implementar
from entidad import Entidad      # heredamos de la clase base del sistema
from excepciones import ServicioError, ServicioNoDisponibleError, DuracionInvalidaError
from logger import logger

# definimos el IVA como constante global para no repetir el número en todo el código
# en Colombia el IVA es del 19%
IVA = 0.19


class Servicio(Entidad):
    """
    Clase abstracta que representa un servicio de Software FJ.
    Define la estructura común para sala, equipo y asesoría.
    No se puede instanciar directamente, cada tipo de servicio hereda de esta.
    """

    DURACION_MINIMA = 0.5  # mínimo media hora por reserva

    def __init__(self, id_servicio: str, nombre: str, precio_hora: float, descripcion: str = ""):
        try:
            super().__init__(id_servicio, nombre)  # validamos id y nombre en la clase padre
            self._precio_hora = self._validar_precio(precio_hora)  # validamos que el precio sea positivo
            self._descripcion = descripcion.strip()  # guardamos la descripción sin espacios extra
            self._disponible = True  # todo servicio nuevo está disponible por defecto
            logger.info(f"Servicio creado: {id_servicio} | {nombre} | ${precio_hora}/h")
        except ServicioError:
            raise
        except Exception as e:
            raise ServicioError(f"Error al crear servicio '{id_servicio}': {e}") from e

    # --- Propiedades ---

    @property
    def precio_hora(self):
        return self._precio_hora

    @property
    def disponible(self):
        return self._disponible  # indica si el servicio puede ser reservado

    @property
    def descripcion(self):
        return self._descripcion

    # --- Validaciones internas ---

    def _validar_precio(self, precio: float) -> float:
        try:
            precio = float(precio)  # intentamos convertir a float por si viene como string
        except (TypeError, ValueError) as e:
            raise ServicioError("El precio debe ser un número.") from e
        if precio <= 0:
            # un precio de 0 o negativo no tiene sentido en el sistema
            raise ServicioError(f"El precio debe ser mayor a 0. Recibido: {precio}")
        return precio

    def _validar_duracion(self, horas: float) -> float:
        try:
            horas = float(horas)  # convertimos a float para aceptar decimales como 1.5
        except (TypeError, ValueError) as e:
            raise DuracionInvalidaError(horas) from e
        if horas < self.DURACION_MINIMA:
            # no permitimos reservas de menos de media hora
            raise DuracionInvalidaError(horas, self.DURACION_MINIMA)
        return horas

    # --- Métodos para habilitar/deshabilitar el servicio ---

    def habilitar(self):
        self._disponible = True
        logger.info(f"Servicio habilitado: {self._id}")

    def deshabilitar(self):
        self._disponible = False
        logger.advertencia(f"Servicio deshabilitado: {self._id}")

    def verificar_disponibilidad(self):
        """Lanza una excepción si el servicio no está disponible, se usa antes de crear reservas."""
        if not self._disponible:
            raise ServicioNoDisponibleError(self._id)

    # --- Cálculo de costos con parámetros opcionales (simulando sobrecarga de métodos) ---

    def calcular_costo(self, horas: float, descuento: float = 0.0, incluir_iva: bool = True) -> float:
        """
        Calcula el costo total de un servicio.
        Tiene parámetros opcionales para simular la sobrecarga de métodos:
        - sin parámetros extra: solo calcula precio base
        - con descuento: aplica un porcentaje de descuento
        - con incluir_iva=False: retorna el precio sin IVA
        """
        horas = self._validar_duracion(horas)  # validamos que la duración sea válida

        # el descuento debe estar entre 0 y 100
        if not (0 <= descuento <= 100):
            raise ServicioError(f"El descuento debe estar entre 0 y 100. Recibido: {descuento}")

        costo_base = self._calcular_costo_base(horas)           # cada servicio calcula su costo a su manera
        costo_con_descuento = costo_base * (1 - descuento / 100) # aplicamos el descuento si hay
        total = costo_con_descuento * (1 + IVA) if incluir_iva else costo_con_descuento  # aplicamos IVA si se pide

        logger.debug(
            f"Costo calculado [{self._id}]: base=${costo_base:.2f} "
            f"desc={descuento}% iva={'sí' if incluir_iva else 'no'} total=${total:.2f}"
        )
        return round(total, 2)  # redondeamos a 2 decimales para evitar problemas con flotantes

    # --- Métodos abstractos que cada tipo de servicio debe implementar ---

    @abstractmethod
    def _calcular_costo_base(self, horas: float) -> float:
        """Cada tipo de servicio tiene su propia lógica para calcular el costo."""
        pass

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Cada servicio valida sus propios parámetros específicos."""
        pass

    # --- Implementación de métodos abstractos de Entidad ---

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio: {self._nombre}\n"
            f"  ID        : {self._id}\n"
            f"  Precio/h  : ${self._precio_hora:,.0f}\n"
            f"  Descripción: {self._descripcion or 'N/A'}\n"
            f"  Estado    : {estado}"
        )

    def validar(self) -> bool:
        return self._precio_hora > 0  # un servicio es válido si tiene precio positivo

    def __str__(self):
        return f"Servicio({self._id}, {self._nombre}, ${self._precio_hora}/h)"
