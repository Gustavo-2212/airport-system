from sqlalchemy import String, Integer, Column, TIMESTAMP, text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime, timezone

class Sessao(Base):
    __tablename__ = "sessoes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    chave_sessao = Column(String, unique=True, index=True)
    data_criacao = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
    data_expiracao = Column(DateTime)
    ip_acesso = Column(String)
    
    usuario = relationship("Usuario")
    
    added_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

