from pydantic import BaseModel
from datetime import datetime

class Voo(BaseModel):
    id_aeroporto_org: int
    id_aeroporto_dest: int
    numero_voo: str
    tarifa_por_passageiro: float
    data_partida: datetime
    data_chegada: datetime
    vagas: int
    status: str