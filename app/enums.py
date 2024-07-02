from enum import Enum

class RifaStatus(Enum):
    DISPONIVEL = (1, "Disponível")
    CANCELADA = (2, "Cancelada")
    ENCERRADA = (3, "Encerrada")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    def __str__(self):
        return self.description
