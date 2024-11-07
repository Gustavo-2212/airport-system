from pydantic import BaseModel
from datetime import datetime

class Reserva(BaseModel):
    id_usuario: int
    id_voo: int
    quantidade_passageiros: int
    tarifa_total: float
    data_reserva: datetime
    status: str
    e_tickets: str
    
class ReservaCompra(BaseModel):
    id_voo: int
    quantidade_passageiros: int
    