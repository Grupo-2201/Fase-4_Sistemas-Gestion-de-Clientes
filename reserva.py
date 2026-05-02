from datetime import datetime  # para guardar las fechas de cada evento de la reserva
from cliente import Cliente    # necesitamos la clase Cliente para validar
from servicio import Servicio  # necesitamos la clase Servicio para validar
from excepciones import (
    ReservaError, ReservaYaCanceladaError, ReservaNoEncontradaError,
    DuracionInvalidaError, ServicioNoDisponibleError
)
from logger import logger


class Reserva:
    """
    Representa una reserva del sistema. Integra un cliente, un servicio,
    la duración y el estado actual. Maneja todo el ciclo de vida de la reserva:
    pendiente → confirmada → completada (o cancelada en cualquier momento).
    """

    # estados válidos que puede tener una reserva
    ESTADOS = {"pendiente", "confirmada", "cancelada", "completada"}

    def __init__(self, id_reserva: str, cliente: Cliente,
                 servicio: Servicio, horas: float,
                 descuento: float = 0.0, incluir_iva: bool = True):
        try:
            self._id = self._validar_id(id_reserva)
            self._cliente = self._validar_cliente(cliente)    # verificamos que el cliente sea válido
            self._servicio = self._validar_servicio(servicio) # verificamos que el servicio esté disponible
            self._horas = float(horas)       # duración de la reserva en horas
            self._descuento = descuento      # porcentaje de descuento (0 por defecto)
            self._incluir_iva = incluir_iva  # si se aplica IVA al costo
            self._estado = "pendiente"       # toda reserva empieza en estado pendiente
            self._fecha_creacion = datetime.now()   # guardamos cuándo se creó
            self._fecha_confirmacion = None  # se llena cuando se confirme
            self._fecha_cancelacion = None   # se llena si se cancela
            self._costo_total = None         # se calcula cuando se confirme
            logger.info(
                f"Reserva creada: {id_reserva} | "
                f"Cliente: {cliente.id} | Servicio: {servicio.id} | {horas}h"
            )
        except (ReservaError, ServicioNoDisponibleError, DuracionInvalidaError):
            raise  # dejamos subir estos errores sin modificarlos
        except Exception as e:
            raise ReservaError(f"Error al crear reserva '{id_reserva}': {e}") from e

    # --- Validaciones privadas ---

    def _validar_id(self, id_reserva: str) -> str:
        if not id_reserva or not str(id_reserva).strip():
            raise ReservaError("El ID de la reserva no puede estar vacío.")
        return str(id_reserva).strip()

    def _validar_cliente(self, cliente) -> Cliente:
        # verificamos que sea una instancia de Cliente y que esté activo
        if not isinstance(cliente, Cliente):
            raise ReservaError("El parámetro 'cliente' debe ser una instancia de Cliente.")
        if not cliente.activo:
            # no podemos hacer reservas para clientes desactivados
            raise ReservaError(f"El cliente '{cliente.id}' está inactivo.")
        return cliente

    def _validar_servicio(self, servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise ReservaError("El parámetro 'servicio' debe ser una instancia de Servicio.")
        servicio.verificar_disponibilidad()  # lanza excepción si el servicio no está disponible
        return servicio

    # --- Propiedades ---

    @property
    def id(self):
        return self._id

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total  # None si todavía no se ha confirmado

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    # --- Ciclo de vida de la reserva ---

    def confirmar(self):
        """
        Confirma la reserva y calcula el costo total.
        Usa try/except/else/finally para manejar los diferentes escenarios.
        """
        try:
            # verificamos que el estado actual permita confirmar
            if self._estado == "cancelada":
                raise ReservaYaCanceladaError(self._id)
            if self._estado == "confirmada":
                raise ReservaError(f"La reserva '{self._id}' ya está confirmada.")
            if self._estado == "completada":
                raise ReservaError(f"La reserva '{self._id}' ya fue completada.")

            # calculamos el costo usando el método del servicio con los parámetros de la reserva
            self._costo_total = self._servicio.calcular_costo(
                self._horas,
                descuento=self._descuento,
                incluir_iva=self._incluir_iva
            )
        except (ReservaYaCanceladaError, ReservaError):
            logger.error(f"No se pudo confirmar reserva {self._id}: estado inválido.")
            raise  # dejamos subir el error para que lo maneje quien llamó este método
        except DuracionInvalidaError as e:
            logger.error(f"Duración inválida en reserva {self._id}.", e)
            raise
        except Exception as e:
            logger.critico(f"Error inesperado al confirmar reserva {self._id}.", e)
            raise ReservaError(f"Error al confirmar: {e}") from e
        else:
            # el bloque else solo se ejecuta si no hubo ninguna excepción
            self._estado = "confirmada"
            self._fecha_confirmacion = datetime.now()
            logger.info(
                f"Reserva confirmada: {self._id} | "
                f"Costo: ${self._costo_total:,.2f}"
            )
        finally:
            # el bloque finally siempre se ejecuta, haya error o no
            logger.debug(f"Proceso de confirmación finalizado para reserva {self._id}.")

    def cancelar(self):
        """
        Cancela la reserva si está en un estado que lo permite.
        También usa try/except/else/finally.
        """
        try:
            if self._estado == "cancelada":
                raise ReservaYaCanceladaError(self._id)  # no se puede cancelar dos veces
            if self._estado == "completada":
                raise ReservaError(
                    f"No se puede cancelar la reserva '{self._id}': ya fue completada."
                )
        except ReservaError:
            logger.advertencia(f"Cancelación fallida para reserva {self._id}.")
            raise
        else:
            # si no hubo errores, procedemos a cancelar
            self._estado = "cancelada"
            self._fecha_cancelacion = datetime.now()
            logger.advertencia(f"Reserva cancelada: {self._id}")
        finally:
            logger.debug(f"Proceso de cancelación finalizado para reserva {self._id}.")

    def completar(self):
        """Marca la reserva como completada, es decir el servicio ya fue prestado."""
        if self._estado != "confirmada":
            # solo se pueden completar reservas que estén confirmadas
            raise ReservaError(
                f"Solo se pueden completar reservas confirmadas. "
                f"Estado actual: '{self._estado}'."
            )
        self._estado = "completada"
        logger.info(f"Reserva completada: {self._id}")

    def procesar(self):
        """
        Procesa la reserva completa en un solo paso: confirma y completa.
        Usa encadenamiento de excepciones (raise ... from e) para preservar
        el error original mientras añadimos contexto.
        """
        try:
            self.confirmar()  # primero confirmamos
            self.completar()  # luego completamos
        except ReservaError as e:
            # encadenamos la excepción para saber que falló en el procesamiento
            raise ReservaError(
                f"Fallo en procesamiento de reserva '{self._id}'."
            ) from e  # 'from e' preserva el error original como causa

    def describir(self) -> str:
        # mostramos toda la información de la reserva de forma organizada
        costo_str = f"${self._costo_total:,.2f}" if self._costo_total is not None else "No calculado"
        conf_str = (
            self._fecha_confirmacion.strftime("%Y-%m-%d %H:%M")
            if self._fecha_confirmacion else "—"
        )
        return (
            f"Reserva: {self._id}\n"
            f"  Cliente   : {self._cliente.nombre} ({self._cliente.id})\n"
            f"  Servicio  : {self._servicio.nombre} ({self._servicio.id})\n"
            f"  Duración  : {self._horas}h\n"
            f"  Descuento : {self._descuento}%\n"
            f"  IVA       : {'Sí' if self._incluir_iva else 'No'}\n"
            f"  Costo     : {costo_str}\n"
            f"  Estado    : {self._estado.upper()}\n"
            f"  Creación  : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
            f"  Confirmada: {conf_str}"
        )

    def __str__(self):
        return f"Reserva({self._id}, {self._cliente.id}, {self._servicio.id}, {self._estado})"

    def __repr__(self):
        return self.__str__()


# ─────────────────────────────────────────────────────────────────
# Clase para administrar todas las reservas del sistema
# ─────────────────────────────────────────────────────────────────

class GestorReservas:
    """
    Administra el listado completo de reservas del sistema.
    Usa un diccionario interno para acceso rápido por ID.
    """

    def __init__(self):
        self._reservas: dict[str, Reserva] = {}  # diccionario: id_reserva → objeto Reserva

    def agregar(self, reserva: Reserva):
        """Agrega una reserva al sistema verificando que no esté duplicada."""
        if not isinstance(reserva, Reserva):
            raise ReservaError("Solo se pueden agregar instancias de Reserva.")
        if reserva.id in self._reservas:
            raise ReservaError(f"Ya existe una reserva con ID '{reserva.id}'.")
        self._reservas[reserva.id] = reserva  # guardamos con el id como clave

    def obtener(self, id_reserva: str) -> Reserva:
        """Busca y retorna una reserva por su ID."""
        if id_reserva not in self._reservas:
            raise ReservaNoEncontradaError(id_reserva)
        return self._reservas[id_reserva]

    def listar(self, estado: str = None) -> list[Reserva]:
        """Retorna todas las reservas, o solo las de un estado específico si se indica."""
        if estado:
            # filtramos solo las reservas que tengan el estado solicitado
            return [r for r in self._reservas.values() if r.estado == estado]
        return list(self._reservas.values())  # si no se filtra, retornamos todas

    def total_ingresos(self) -> float:
        """Calcula el total de ingresos sumando las reservas confirmadas y completadas."""
        return sum(
            r.costo_total for r in self._reservas.values()
            if r.estado in ("confirmada", "completada") and r.costo_total
        )
