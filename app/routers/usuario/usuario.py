from fastapi import APIRouter, Depends, HTTPException, Response, status

from routers.auth import LoginSchema, verifica_senha, get_usuario_by_email, criar_sessao
from schemas.usuario.usuario import Usuario as UsuarioSchema

from models.database import get_db
from models.usuario.usuario import Usuario as UsuarioModel
from sqlalchemy.orm import Session

import logging, coloredlogs, bcrypt

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
@router.get("/usuarios")
async def todos_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(UsuarioModel).all()
    logging.info("GET_ALL_USUARIOS")
    usuarios_obj = []
    for usuario in usuarios:
        obj = {
            "id": usuario.id,
            "nome": usuario.nome,
            "e-mail": usuario.email,
            "tipo": usuario.tipo_usuario
        }
        usuarios_obj.append(obj)
    logging.info(usuarios_obj)
    return usuarios


@router.post("/usuario")
async def criar_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):
    senha_hashed = bcrypt.hashpw(usuario.senha.encode("utf-8"), bcrypt.gensalt())
    usuario.senha = senha_hashed.decode("utf-8")
    novo_usuario = UsuarioModel(**usuario.model_dump())
    logging.info("POST_USUARIO")
    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        logging.info(novo_usuario)
        
        return {
            "mensagem": "Registro _usuario criado com sucesso.",
            "usuario": usuario
        }
    except Exception as e:
        logging.error(e)
        
        return {
            "mensagem": "Problemas ao inserir novo registro de _usuario.",
            "usuario": usuario
        }
        
        
        
@router.put("/usuario/{id}")
async def atualizar_usuario(id: int, usuario: UsuarioSchema, db: Session = Depends(get_db)):
    senha_hashed = bcrypt.hashpw(usuario.senha.encode("utf-8"), bcrypt.gensalt())
    usuario.senha = senha_hashed.decode("utf-8")
    registro = db.query(UsuarioModel).filter(UsuarioModel.id == id).first() 
    logging.info("PUT_USUARIO")
    
    old = {k.name: getattr(registro, k.name) for k in registro.__table__.columns}
    
    if not registro:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario: {id} não existe no banco de dados."
        )
    
    for key, value in usuario.model_dump().items():
        setattr(registro, key, value) 
    
    db.commit()
    db.refresh(registro)
    
    return {
        "usuario_old": old,
        "usuario_new": registro
    }
    
    
@router.delete("/usuario/{id}")
async def deleta_usuario(id: int, db: Session = Depends(get_db)):
    registro = db.query(UsuarioModel).filter(UsuarioModel.id == id)
    logging.info("DELETE_USUARIO")
    if registro == None:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario: {id} não existe no banco de dados.")
    else:
        registro.delete(synchronize_session=False)
        db.commit()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    
@router.post("/login")
async def login(credenciais: LoginSchema, db: Session = Depends(get_db)):
    usuario = get_usuario_by_email(credenciais.email, db)
    if not usuario:
        logging.warning(f"Tentativa de login falha: Usuário com email {credenciais.email} não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_UNAUTHORIZED,
            detail="Email não cadastrado."
        )
        
    if not verifica_senha(credenciais.senha, usuario.senha):
        logging.warning(f"Tentativa de login falha: Senha incorreta para o usuário {credenciais.email}.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas."
        )
        
    sessao = criar_sessao(usuario.id, db)
    logging.info(f"Usuário {credenciais.email} efetuou o login com sucesso. Sessão ID: {sessao.id}.")
    
    return {
        "mensagem": "Login realizado com sucesso.",
        "sessao": sessao
    }
    
 
from models.sessao.sessao import Sessao as SessaoModel 
@router.delete("/logout")
async def logout(chave_sessao: str, db: Session = Depends(get_db)):
    sessao = db.query(SessaoModel).filter(SessaoModel.chave_sessao == chave_sessao).first()
    
    if not sessao:
        logging.warning(f"Tentativa de logout falha: Sessão com chave {chave_sessao} não encontrada.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada ou já foi encerrada."
        )
    
    db.delete(sessao)
    db.commit()
    logging.info(f"Sessão com chave {chave_sessao} encerrada com sucesso.")
    