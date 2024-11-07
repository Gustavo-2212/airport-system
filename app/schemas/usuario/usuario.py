from pydantic import BaseModel

class Usuario(BaseModel):
    nome: str
    cpf: str
    email: str
    senha: str
    tipo_usuario: str