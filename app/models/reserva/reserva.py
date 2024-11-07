from sqlalchemy import String, Integer, Column, TIMESTAMP, text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime, timezone

class Reserva(Base):
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_voo = Column(Integer, ForeignKey("voos.id"), nullable=False)
    
    quantidade_passageiros = Column(Integer, nullable=False)
    tarifa_total = Column(Float, nullable=False)
    data_reserva = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
    status = Column(String, default="Pendente")
    e_tickets = Column(String, nullable=False)
    
    usuario = relationship("Usuario", back_populates="reservas")
    voo = relationship("Voo", back_populates="reservas")
    
    added_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))