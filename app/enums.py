from enum import Enum

class RifaStatus(Enum):
    DISPONIVEL = 1
    CANCELADA = 2
    ENCERRADA = 3
    
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    def __str__(self):
        return self.description()
    
    def description(self):
        if self.name == 'DISPONIVEL':
            return 'Disponível'
        elif self.name == 'CANCELADA':
            return 'Cancelada'
        elif self.name == 'ENCERRADA':
            return 'Encerrada'
