from sqlalchemy import String, Integer, Column, TIMESTAMP, text
from sqlalchemy.orm import relationship
from models.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(50), index=True, nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    tipo_usuario = Column(String, default="Cliente")
    
    reservas = relationship("Reserva", back_populates="usuario")
    
    added_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))