from servicio import Servicio          # heredamos de la clase abstracta Servicio
from excepciones import ServicioError  # para errores específicos del sistema
from logger import logger              # para registrar eventos

# diccionario con las especialidades disponibles y su factor de costo
# cada especialidad tiene un multiplicador diferente según su complejidad
ESPECIALIDADES = {
    "software":   1.0,   # factor base, sin recargo adicional
    "hardware":   1.1,   # 10% más costoso que software
    "redes":      1.15,  # 15% más costoso
    "seguridad":  1.25,  # 25% más costoso por ser una especialidad crítica
    "datos":      1.20,  # 20% más costoso
    "gestion":    0.95,  # 5% más barato, es la especialidad más general
}


class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría técnica especializada.
    Hereda de Servicio y maneja niveles de urgencia que afectan el costo.
    El precio varía según la especialidad del asesor y la urgencia del servicio.
    """

    # niveles de urgencia disponibles con su factor multiplicador de costo
    NIVELES_URGENCIA = {
        "normal":  1.0,  # precio normal sin recargo
        "urgente": 1.5,  # 50% más costoso por atención prioritaria
        "critico": 2.0,  # doble precio para casos críticos
    }

    def __init__(self, id_servicio: str, nombre: str, precio_hora: float,
                 especialidad: str, asesor: str):
        # llamamos al constructor de Servicio para las validaciones comunes
        super().__init__(id_servicio, nombre, precio_hora,
                         f"Asesoría en {especialidad}")
        self._especialidad = self._validar_especialidad(especialidad)  # validamos que la especialidad exista
        # si no viene nombre de asesor, ponemos un valor por defecto
        self._asesor = asesor.strip() if asesor and asesor.strip() else "Por asignar"
        self._nivel_urgencia = "normal"  # por defecto toda asesoría es normal
        logger.info(f"Asesoría creada: especialidad={especialidad}, asesor={self._asesor}")

    # --- Propiedades ---

    @property
    def especialidad(self):
        return self._especialidad

    @property
    def asesor(self):
        return self._asesor

    @property
    def nivel_urgencia(self):
        return self._nivel_urgencia

    @nivel_urgencia.setter
    def nivel_urgencia(self, nivel: str):
        # cuando cambien el nivel de urgencia, validamos que sea un nivel válido
        nivel = nivel.strip().lower()
        if nivel not in self.NIVELES_URGENCIA:
            raise ServicioError(
                f"Nivel de urgencia '{nivel}' inválido. "
                f"Opciones: {', '.join(self.NIVELES_URGENCIA)}."
            )
        self._nivel_urgencia = nivel
        logger.info(f"Urgencia actualizada para {self._id}: {nivel}")

    # --- Validaciones ---

    def _validar_especialidad(self, esp: str) -> str:
        esp = esp.strip().lower()  # limpiamos el texto antes de validar
        if esp not in ESPECIALIDADES:
            raise ServicioError(
                f"Especialidad '{esp}' no disponible. "
                f"Disponibles: {', '.join(ESPECIALIDADES)}."
            )
        return esp

    # --- Implementación del método abstracto heredado de Servicio ---

    def _calcular_costo_base(self, horas: float) -> float:
        """
        Calcula el costo de la asesoría combinando tres factores:
        1. El precio base por hora
        2. El factor de la especialidad (algunas son más costosas)
        3. El factor de urgencia (urgente o crítico sube el precio)
        Además, sesiones largas de más de 4 horas reciben un 10% de descuento automático.
        """
        factor_esp = ESPECIALIDADES[self._especialidad]          # factor según especialidad
        factor_urg = self.NIVELES_URGENCIA[self._nivel_urgencia] # factor según urgencia
        costo = self._precio_hora * horas * factor_esp * factor_urg  # multiplicamos todos los factores
        if horas > 4:
            costo *= 0.90  # descuento automático del 10% para sesiones largas
        return costo

    def validar_parametros(self, especialidad_requerida: str = None, **kwargs) -> bool:
        """
        Verifica que la especialidad del asesor coincida con lo que el cliente necesita.
        Si no se especifica especialidad requerida, cualquier asesoría es válida.
        """
        try:
            if especialidad_requerida:
                esp = especialidad_requerida.strip().lower()
                if esp != self._especialidad:
                    # si la especialidad no coincide, no podemos atender al cliente
                    raise ServicioError(
                        f"Este servicio es de '{self._especialidad}', "
                        f"se requería '{especialidad_requerida}'."
                    )
            return True
        except ServicioError:
            raise
        except Exception as e:
            raise ServicioError(f"Error al validar parámetros de asesoría: {e}") from e

    def describir(self) -> str:
        base = super().describir()
        factor_urg = self.NIVELES_URGENCIA[self._nivel_urgencia]  # obtenemos el factor para mostrarlo
        extras = (
            f"\n  Especialidad: {self._especialidad.capitalize()}"
            f"\n  Asesor      : {self._asesor}"
            f"\n  Urgencia    : {self._nivel_urgencia} (×{factor_urg})"
            f"\n  Tipo        : Asesoría especializada"
        )
        return base + extras

    def __str__(self):
        return f"Asesoria({self._id}, {self._especialidad}, {self._asesor})"
