from fastapi import APIRouter, Depends, HTTPException, Response, status

from schemas.aeroporto.aeroporto import Aeroporto as AeroportoSchema

from models.database import get_db
from models.aeroporto.aeroporto import Aeroporto as AeroportoModel
from sqlalchemy.orm import Session

import logging, coloredlogs

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
@router.get("/")
async def root(): return {"mensagem": "API Aeroporto"}

@router.get("/teste_logs")
async def teste_logs():
    logging.info("Info...")
    logging.error("Error...")
    logging.debug("Debug...")
    logging.warning("Warning...")
    logging.critical("Critical...")
    

@router.get("/aeroportos")
async def todos_aeroportos(db: Session = Depends(get_db)):
    aeroportos = db.query(AeroportoModel).all()
    logging.info("GET_ALL_AEROPORTOS")
    aeroportos_obj = []
    for aeroporto in aeroportos:
        obj = {
            "id": aeroporto.id,
            "nome": aeroporto.nome,
            "IATA": aeroporto.codigo_iata
        }
        aeroportos_obj.append(obj)
    logging.info(aeroportos_obj)
    return aeroportos


@router.post("/aeroporto")
async def criar_aeroporto(aeroporto: AeroportoSchema, db: Session = Depends(get_db)):
    novo_aeroporto = AeroportoModel(**aeroporto.model_dump())
    logging.info("POST_AEROPORTO")
    try:
        db.add(novo_aeroporto)
        db.commit()
        db.refresh(novo_aeroporto)
        logging.info(novo_aeroporto)
        
        return {
            "mensagem": "Registro _aeroporto criado com sucesso.",
            "aeroporto": aeroporto
        }
    except Exception as e:
        logging.error(e)
        
        return {
            "mensagem": "Problemas ao inserir novo registro de _aeroporto.",
            "aeroporto": aeroporto
        }
        
        
@router.put("/aeroporto/{id}")
async def atualizar_aeroporto(id: int, aeroporto: AeroportoSchema, db: Session = Depends(get_db)):
    registro = db.query(AeroportoModel).filter(AeroportoModel.id == id).first() 
    logging.info("PUT_AEROPORTO")
    
    old = {k.name: getattr(registro, k.name) for k in registro.__table__.columns}
    
    if not registro:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aeroporto: {id} não existe no banco de dados."
        )
    
    for key, value in aeroporto.model_dump().items():
        setattr(registro, key, value) 
    
    db.commit()
    db.refresh(registro)
    
    return {
        "aeroporto_old": old,
        "aeroporto_new": registro
    }


@router.delete("/aeroporto/{id}")
async def deleta_aeroporto(id: int, db: Session = Depends(get_db)):
    registro = db.query(AeroportoModel).filter(AeroportoModel.id == id)
    logging.info("DELETE_AEROPORTO")
    if registro == None:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aeroporto: {id} não existe no banco de dados.")
    else:
        registro.delete(synchronize_session=False)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    
@router.get("/aeroportos/companhias/{companhia}")
async def aeroportos_por_companhia(companhia: str, db: Session = Depends(get_db)):
    aeroportos = db.query(AeroportoModel).filter(AeroportoModel.companhias.like(f"%{companhia}%")).all()
    logging.info(f"GET_AEROPORTOS_POR_COMPANHIA: {companhia}")

    if not aeroportos:
        logging.warning(f"Nenhum aeroporto encontrado para a companhia {companhia}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum aeroporto encontrado para a companhia {companhia}."
        )

    aeroportos_obj = []
    for aeroporto in aeroportos:
        obj = {
            "id": aeroporto.id,
            "nome": aeroporto.nome,
            "IATA": aeroporto.codigo_iata,
            "cidade": aeroporto.cidade,
            "estado": aeroporto.estado,
            "pais": aeroporto.pais,
            "endereco": aeroporto.endereco,
            "cep": aeroporto.cep,
            "companhias": aeroporto.companhias
        }
        aeroportos_obj.append(obj)

    logging.info(aeroportos_obj)
    return aeroportos_obj
