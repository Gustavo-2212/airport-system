from sqlalchemy import String, Integer, Column, TIMESTAMP, text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from models.database import Base

class Voo(Base):
    __tablename__ = "voos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    id_aeroporto_org = Column(Integer, ForeignKey("aeroportos.id"), nullable=False)
    id_aeroporto_dest = Column(Integer, ForeignKey("aeroportos.id"), nullable=False)
    
    numero_voo = Column(String, index=True, nullable=False)
    tarifa_por_passageiro = Column(Float, nullable=False)
    data_partida = Column(DateTime, nullable=False)
    data_chegada = Column(DateTime, nullable=False)
    vagas = Column(Integer, nullable=False)
    status = Column(String, default="Programado")
    
    aeroporto_org = relationship("Aeroporto", foreign_keys=[id_aeroporto_org])
    aeroporto_dest = relationship("Aeroporto", foreign_keys=[id_aeroporto_dest])
    
    reservas = relationship("Reserva", back_populates="voo")
    
    added_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
