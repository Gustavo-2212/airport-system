from fastapi import Depends, HTTPException, status

from models.database import get_db
from models.usuario.usuario import Usuario as UsuarioModel
from models.sessao.sessao import Sessao as SessaoModel

from sqlalchemy.orm import Session

from pydantic import BaseModel

class LoginSchema(BaseModel):
    email: str
    senha: str

import secrets, random, bcrypt, string
import datetime
from datetime import timedelta

def verifica_senha(senha: str, senha_hashed: str):
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hashed.encode("utf-8"))


def get_usuario_by_email(email: str, db: Session):
    return db.query(UsuarioModel).filter(UsuarioModel.email == email).first()


def gerar_ip():
    return f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"


def criar_sessao(usuario_id: int, db: Session):
    chave_sessao = secrets.token_hex(16)
    data_criacao = datetime.now()
    data_expiracao = data_criacao + timedelta(hours=15)
    
    nova_sessao = SessaoModel(
        id_usuario=usuario_id,
        chave_sessao=chave_sessao,
        data_criacao=data_criacao,
        data_expiracao=data_expiracao,
        ip_acesso=gerar_ip()
    )
    
    db.add(nova_sessao)
    db.commit()
    db.refresh(nova_sessao)
    
    return nova_sessao
    
    
def validar_sessao(sessao_id: int, db: Session):
    sessao = db.query(SessaoModel).filter(SessaoModel.id == sessao_id).first()
    
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada."
        )
        
    if datetime.now() < sessao.data_expiracao:
        return True
    
    return False


from datetime import datetime
import logging, coloredlogs

log_colors = {
    "DEBUG": "cyan",
    "INFO": "light_white",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red"
}
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
coloredlogs.install()

def remover_sessoes_expiradas():
    agora = datetime.now()
    logging.info("Verificando sessões expiradas...")

    db = next(get_db())
    
    try:
        sessoes_expiradas = db.query(SessaoModel).filter(SessaoModel.data_expiracao < agora).all()
        
        if not sessoes_expiradas:
            logging.info("Nenhuma sessão expirada encontrada.")
            return {"mensagem": "Nenhuma sessão expirada para remover."}

        for sessao in sessoes_expiradas:
            db.delete(sessao)
            logging.info(f"Removendo sessão expirada: ID {sessao.id} - Usuário {sessao.id_usuario}")

        db.commit()
        logging.info("Sessões expiradas removidas com sucesso.")
        
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao remover as seções expisradas: {e}")
        
    finally:
        db.close()

    return {"mensagem": "Sessões expiradas removidas com sucesso."}

    
def gerar_e_ticket():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
