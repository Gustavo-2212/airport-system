from pydantic import BaseModel
from datetime import datetime

class Sessao(BaseModel):
    id_usuario: int