# En este archivo definimos todas las excepciones personalizadas del sistema
# Tener excepciones propias nos permite identificar exactamente qué salió mal
# y dar mensajes de error más claros que los errores genéricos de Python


# Esta es la excepción base de todo el sistema
# todas las demás heredan de esta para que sea fácil capturarlas todas con un solo except
class SoftwareFJError(Exception):
    """Excepción base del sistema."""
    def __init__(self, mensaje: str, codigo: str = "ERR_000"):
        super().__init__(mensaje)   # llamamos al constructor de Exception con el mensaje
        self.codigo = codigo        # guardamos un código para identificar el tipo de error
        self.mensaje = mensaje      # guardamos el mensaje para poder mostrarlo después

    def __str__(self):
        # cuando imprimamos el error, mostramos el código y el mensaje juntos
        return f"[{self.codigo}] {self.mensaje}"


# --- Excepciones relacionadas con clientes ---

class ClienteError(SoftwareFJError):
    """Errores relacionados con operaciones de clientes."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLI")  # usamos el código ERR_CLI para errores de cliente


class ClienteNoEncontradoError(ClienteError):
    """Se lanza cuando buscamos un cliente que no existe en el sistema."""
    def __init__(self, id_cliente: str):
        # guardamos el id para poder usarlo si necesitamos saber cuál cliente falló
        super().__init__(f"Cliente con ID '{id_cliente}' no encontrado.")
        self.id_cliente = id_cliente


class ClienteDuplicadoError(ClienteError):
    """Se lanza cuando intentamos registrar un cliente que ya existe."""
    def __init__(self, campo: str, valor: str):
        super().__init__(f"Ya existe un cliente con {campo} '{valor}'.")


# --- Excepciones relacionadas con servicios ---

class ServicioError(SoftwareFJError):
    """Errores relacionados con servicios."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SRV")  # código ERR_SRV para errores de servicio


class ServicioNoDisponibleError(ServicioError):
    """Se lanza cuando intentamos reservar un servicio que está deshabilitado."""
    def __init__(self, id_servicio: str):
        super().__init__(f"El servicio '{id_servicio}' no está disponible actualmente.")
        self.id_servicio = id_servicio  # guardamos el id del servicio que causó el error


class ServicioNoEncontradoError(ServicioError):
    """Se lanza cuando buscamos un servicio que no existe."""
    def __init__(self, id_servicio: str):
        super().__init__(f"Servicio con ID '{id_servicio}' no encontrado.")


# --- Excepciones relacionadas con reservas ---

class ReservaError(SoftwareFJError):
    """Errores relacionados con reservas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RES")


class ReservaNoEncontradaError(ReservaError):
    """Se lanza cuando buscamos una reserva que no existe."""
    def __init__(self, id_reserva: str):
        super().__init__(f"Reserva con ID '{id_reserva}' no encontrada.")


class ReservaYaCanceladaError(ReservaError):
    """Se lanza cuando intentamos cancelar una reserva que ya estaba cancelada."""
    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva '{id_reserva}' ya fue cancelada previamente.")


class DuracionInvalidaError(ReservaError):
    """Se lanza cuando la duración de una reserva es menor al mínimo permitido."""
    def __init__(self, duracion: float, minimo: float = 0.5):
        super().__init__(
            f"Duración inválida: {duracion}h. El mínimo permitido es {minimo}h."
        )
        self.duracion = duracion  # guardamos la duración que causó el error


# --- Excepciones de validación general ---

class ValidacionError(SoftwareFJError):
    """Se lanza cuando un campo tiene un formato o valor incorrecto."""
    def __init__(self, campo: str, mensaje: str):
        super().__init__(f"Error en campo '{campo}': {mensaje}", "ERR_VAL")
        self.campo = campo  # guardamos qué campo falló para mostrarlo en el mensaje
