# Importamos ABC y abstractmethod para poder crear clases abstractas
# ABC es la clase base y abstractmethod nos obliga a implementar ciertos métodos en las clases hijas
from abc import ABC, abstractmethod
from datetime import datetime  # lo usamos para guardar cuando se crea cada entidad


# Esta es la clase base de todo el sistema, es abstracta así que no se puede usar directamente
# todas las demás clases del sistema van a heredar de esta
class Entidad(ABC):
    """Clase abstracta base para todas las entidades del sistema Software FJ."""

    def __init__(self, id_entidad: str, nombre: str):
        # verificamos que el id no venga vacío o con puros espacios
        if not id_entidad or not id_entidad.strip():
            raise ValueError("El ID de la entidad no puede estar vacío.")

        # lo mismo para el nombre, no tiene sentido una entidad sin nombre
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la entidad no puede estar vacío.")

        # guardamos los atributos con _ al inicio para indicar que son privados (encapsulación)
        self._id = id_entidad.strip()          # quitamos espacios extra al inicio y al final
        self._nombre = nombre.strip()
        self._fecha_creacion = datetime.now()  # guardamos la fecha exacta en que se creó

    # con @property convertimos el atributo privado en una propiedad de solo lectura
    @property
    def id(self):
        return self._id  # retornamos el id sin permitir modificarlo directamente

    @property
    def nombre(self):
        return self._nombre

    # este setter permite cambiar el nombre pero con validación, no directamente
    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()  # si pasa la validación, lo actualizamos

    @property
    def fecha_creacion(self):
        return self._fecha_creacion  # la fecha no se puede cambiar una vez creada

    # este método es abstracto, significa que cada clase hija DEBE implementarlo
    # si no lo implementan, Python lanza un error automáticamente
    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción detallada de la entidad."""
        pass

    # igual que describir(), cada clase hija debe tener su propia versión de validar()
    @abstractmethod
    def validar(self) -> bool:
        """Valida que los datos de la entidad son correctos."""
        pass

    # __str__ define cómo se ve el objeto cuando lo imprimimos con print()
    def __str__(self):
        return f"[{self.__class__.__name__}] ID: {self._id} | Nombre: {self._nombre}"

    # __repr__ es más técnico, se usa cuando imprimimos el objeto en la consola directamente
    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self._id}', nombre='{self._nombre}')"
