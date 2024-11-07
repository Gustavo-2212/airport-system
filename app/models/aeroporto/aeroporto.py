from sqlalchemy import String, Integer, Column, TIMESTAMP, text
from models.database import Base

class Aeroporto(Base):
    __tablename__ = "aeroportos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(50), nullable=False, index=True)
    cidade = Column(String(50), index=True, nullable=False)
    estado = Column(String(50), index=True, default="-")
    pais = Column(String(50), index=True, nullable=False)
    endereco = Column(String(100), nullable=False, index=True)
    cep = Column(String(10), nullable=False)
    codigo_iata = Column(String(3), unique=False)
    companhias = Column(String(1000), nullable=False)
    
    added_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    
    