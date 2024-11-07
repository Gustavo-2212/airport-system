from fastapi import APIRouter, status, Response, HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy import func

from schemas.voo.voo import Voo as VooSchema

from models.database import get_db
from models.voo.voo import Voo as VooModel
from models.aeroporto.aeroporto import Aeroporto as AeroportoModel
from sqlalchemy.orm import Session
import datetime

import coloredlogs, logging

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
@router.get("/voos")
async def todos_voos(db: Session = Depends(get_db)):
    voos = db.query(VooModel).all()
    logging.info("GET_ALL_VOOS")
    voos_obj = []
    for voo in voos:
        obj = {
            "id": voo.id,
            "data_partida": voo.data_partida,
            "data_chegada": voo.data_chegada,
            "status": voo.status,
            "codigo": voo.numero_voo
        }
        voos_obj.append(voo)
    logging.info(voos_obj)
    return voos


@router.post("/voo")
async def criar_voo(voo: VooSchema, db: Session = Depends(get_db)):
    novo_voo = VooModel(**voo.model_dump())
    logging.info("POST_VOO")
    try:
        db.add(novo_voo)
        db.commit()
        db.refresh(novo_voo)
        logging.info(novo_voo)
        
        return {
            "mensagem": "Registro _voo criado com sucesso.",
            "voo": voo
        }
    except Exception as e:
        logging.error(e)
        
        return {
            "mensagem": "Problemas ao inserir novo registro de _voo.",
            "voo": voo
        }
        
    
@router.put("/voo/{id}")
async def atualizar_voo(id: int, voo: VooSchema, db: Session = Depends(get_db)):
    registro = db.query(VooModel).filter(VooModel.id == id).first()
    
    old = {k.name: getattr(registro, k.name) for k in registro.__table__.columns}
    
    logging.info("PUT_VOO")
    if not registro:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voo: {id} não existe no banco de dados."
        )
    
    for key, value in voo.model_dump().items():
        setattr(registro, key, value)
    
    db.commit()
    db.refresh(registro)  
    
    return {
        "voo_old": old, 
        "voo_new": registro 
    }
    
    
@router.delete("/voo/{id}")
async def deleta_voo(id: int, db: Session = Depends(get_db)):
    registro = db.query(VooModel).filter(VooModel.id == id)
    logging.info("DELETE_VOO")
    if registro == None:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Voo: {id} não existe no banco de dados.")
    else:
        registro.delete(synchronize_session=False)
        db.commit()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/aeroportos/destinos/{aeroporto_origem_nome}")
async def aeroportos_destinos_por_origem(aeroporto_origem_nome: str, db: Session = Depends(get_db)):
    # Busca o aeroporto de origem pelo nome
    aeroporto_origem = db.query(AeroportoModel).filter(AeroportoModel.nome == aeroporto_origem_nome).first()
    
    if not aeroporto_origem:
        logging.warning(f"Aeroporto de origem '{aeroporto_origem_nome}' não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aeroporto de origem '{aeroporto_origem_nome}' não encontrado."
        )

    voos = db.query(VooModel).filter(VooModel.id_aeroporto_org == aeroporto_origem.id).all()
    
    if not voos:
        logging.warning(f"Nenhum voo encontrado partindo do aeroporto '{aeroporto_origem_nome}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum voo encontrado partindo do aeroporto '{aeroporto_origem_nome}'."
        )
    
    aeroportos_destinos = []
    for voo in voos:
        aeroporto_dest = {
            "id": voo.aeroporto_dest.id,
            "nome": voo.aeroporto_dest.nome,
            "IATA": voo.aeroporto_dest.codigo_iata,
            "cidade": voo.aeroporto_dest.cidade,
            "estado": voo.aeroporto_dest.estado,
            "pais": voo.aeroporto_dest.pais,
            "endereco": voo.aeroporto_dest.endereco,
            "cep": voo.aeroporto_dest.cep,
            "numero_voo": voo.numero_voo,
            "data_partida": voo.data_partida,
            "data_chegada": voo.data_chegada,
            "tarifa_por_passageiro": voo.tarifa_por_passageiro,
            "status": voo.status
        }
        aeroportos_destinos.append(aeroporto_dest)
    
    logging.info(f"Destinos a partir do aeroporto '{aeroporto_origem_nome}': {aeroportos_destinos}")
    return aeroportos_destinos


@router.get("/voos/companhia/data_partida")
async def voos_por_data_companhia(
    data_partida: datetime.datetime,
    companhia: str,
    db: Session = Depends(get_db)
):
    voos = db.query(VooModel).join(AeroportoModel, VooModel.id_aeroporto_org == AeroportoModel.id)\
                        .filter(func.date(VooModel.data_partida) == data_partida.date())\
                        .filter(AeroportoModel.companhias.like(f"%{companhia}%")).all()
    
    if not voos:
        logging.warning(f"Nenhum voo encontrado para a companhia '{companhia}' na data {data_partida}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum voo encontrado para a companhia '{companhia}' na data {data_partida}."
        )
    
    voos_data = []
    for voo in voos:
        voo_info = {
            "numero_voo": voo.numero_voo,
            "data_partida": voo.data_partida,
            "data_chegada": voo.data_chegada,
            "tarifa_por_passageiro": voo.tarifa_por_passageiro,
            "vagas": voo.vagas,
            "status": voo.status,
            "aeroporto_origem": {
                "nome": voo.aeroporto_org.nome,
                "cidade": voo.aeroporto_org.cidade,
                "codigo_iata": voo.aeroporto_org.codigo_iata,
            },
            "aeroporto_destino": {
                "nome": voo.aeroporto_dest.nome,
                "cidade": voo.aeroporto_dest.cidade,
                "codigo_iata": voo.aeroporto_dest.codigo_iata,
            }
        }
        voos_data.append(voo_info)
    
    logging.info(f"Voos encontrados para a companhia '{companhia}' na data {data_partida}: {voos_data}")
    return voos_data


@router.get("/voos/tarifa_minima/{num_passageiros}")
async def voos_tarifa_minima(num_passageiros: int, db: Session = Depends(get_db)):
    if num_passageiros < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Número de passageiros deve ser pelo menos 1.")
    
    try:
        voos = (
            db.query(VooModel)
            .filter(
                and_(
                    VooModel.data_partida > datetime.datetime.now(),
                    VooModel.vagas >= num_passageiros
                )
            )
            .order_by(VooModel.tarifa_por_passageiro)
            .all()
        )
        
        if not voos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum voo disponível encontrado.")

        return [
            {
                "id": voo.id,
                "numero_voo": voo.numero_voo,
                "id_aeroporto_org": voo.id_aeroporto_org,
                "id_aeroporto_dest": voo.id_aeroporto_dest,
                "tarifa_por_passageiro": voo.tarifa_por_passageiro,
                "data_partida": voo.data_partida,
                "data_chegada": voo.data_chegada,
                "vagas": voo.vagas,
                "status": voo.status,
            }
            for voo in voos
        ]
    
    except Exception as e:
        logging.error(f"Erro ao buscar voos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar voos disponíveis.")
