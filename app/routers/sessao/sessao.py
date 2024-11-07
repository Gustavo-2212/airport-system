from fastapi import APIRouter, Depends, HTTPException, Response, status

from schemas.sessao.sessao import Sessao as SessaoSchema

from models.database import get_db
from models.sessao.sessao import Sessao as SessaoModel
from sqlalchemy.orm import Session

import logging, coloredlogs, datetime

router = APIRouter()

log_colors = {
    "DEBUG": "cyan",
    "INFO": "light_white",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red"
}
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
coloredlogs.install()


# =-=-=-=-=-=-=-| CRUD |-=-=-=-=-=-=-=-=-=
@router.get("/sessoes")
async def todas_sessoes(db: Session = Depends(get_db)):
    sessoes = db.query(SessaoModel).all()
    logging.info("GET_ALL_SESSOES")
    sessoes_obj = []
    for sessao in sessoes:
        obj = {
            "id": sessao.id,
            "ip_acesso": sessao.ip_acesso,
            "data_criacao": sessao.data_criacao,
            "data_expiracao": sessao.data_expiracao
        }
        sessoes_obj.append(obj)
    logging.info(sessoes_obj)
    return sessoes


from routers.auth import criar_sessao
@router.post("/sessao")
async def criar_sessao_endpoint(sessao: SessaoSchema, db: Session = Depends(get_db)):
    try:
        nova_sessao = criar_sessao(sessao.id, db)
        logging.info("POST_SESSAO")
        logging.info(nova_sessao)
        
        return {
            "mensagem": "Registro _sessao criado com sucesso.",
            "sessao": sessao
        }
        
    except Exception as e:
        logging.error(e)
        
        return {
            "mensagem": "Problemas ao inserir novo registro de _sessao.",
            "sessao": sessao
        }
        
        
@router.put("/sessao/{id}")
async def atualizar_sessao(id: int, sessao: SessaoSchema, db: Session = Depends(get_db)):
    registro = db.query(SessaoModel).filter(SessaoModel.id == id).first() 
    logging.info("PUT_SESSAO")
    
    old = {k.name: getattr(registro, k.name) for k in registro.__table__.columns}
    
    if not registro:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sessao: {id} não existe no banco de dados."
        )
    
    for key, value in sessao.model_dump().items():
        setattr(registro, key, value) 
    
    db.commit()
    db.refresh(registro)
    
    return {
        "sessao_old": old,
        "sessao_new": registro
    }
    
    
@router.delete("/sessao/{id}")
async def deleta_sessao(id: int, db: Session = Depends(get_db)):
    registro = db.query(SessaoModel).filter(SessaoModel.id == id)
    logging.info("DELETE_SESSAO")
    if registro == None:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sessao: {id} não existe no banco de dados.")
    else:
        registro.delete(synchronize_session=False)
        db.commit()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sessao/validar/{id}")
async def validar_sessao(id: int, ip: str, db: Session = Depends(get_db)):
    registro = db.query(SessaoModel).filter(SessaoModel.id == id).first()
    
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sessao: {id} não existe no banco de dados."
        )
    
    if registro.data_expiracao > datetime.datetime.now():
        if ip != registro.ip_acesso:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Acesso negado para o seguinte IP: {ip}."
            )
        return {
            "mensagem": "Sessão válida.",
            "sessao": {
                "id": registro.id,
                "ip_acesso": registro.ip_acesso,
                "data_criacao": registro.data_criacao,
                "data_expiracao": registro.data_expiracao
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada."
        )