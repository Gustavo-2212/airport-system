from pydantic import BaseModel

class Aeroporto(BaseModel):
    nome: str
    cidade: str
    estado: str
    pais: str
    endereco: str
    cep: str
    codigo_iata: str
    companhias: str