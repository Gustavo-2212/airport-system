from fastapi import APIRouter, Depends, HTTPException, Response, status

from schemas.reserva.reserva import Reserva as ReservaSchema
from schemas.reserva.reserva import ReservaCompra
from schemas.voo.voo import Voo as VooSchema
from routers.auth import gerar_e_ticket, validar_sessao

from models.database import get_db
from models.reserva.reserva import Reserva as ReservaModel
from models.voo.voo import Voo as VooModel
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

@router.get("/reservas")
async def todas_reservas(db: Session = Depends(get_db)):
    reservas = db.query(ReservaModel).all()
    logging.info("GET_ALL_RESERVAS")
    reservas_obj = []
    for reserva in reservas:
        obj = {
            "id": reserva.id,
            "usuario": reserva.usuario,
            "e-tickets": reserva.e_tickets,
            "status": reserva.status,
            "data": reserva.data_reserva
        }
        reservas_obj.append(obj)
    logging.info(reservas_obj)
    return reservas


@router.post("/reserva")
async def criar_reserva(reserva: ReservaSchema, db: Session = Depends(get_db)):
    nova_reserva = ReservaModel(**reserva.model_dump())
    logging.info("POST_RESERVA")
    try:
        db.add(nova_reserva)
        db.commit()
        db.refresh(nova_reserva)
        logging.info(nova_reserva)
        
        return {
            "mensagem": "Registro _reserva criado com sucesso.",
            "reserva": reserva
        }
    except Exception as e:
        logging.error(e)
        
        return {
            "mensagem": "Problemas ao inserir novo registro de _reserva.",
            "reserva": reserva
        }
        
        
@router.put("/reserva/{id}")
async def atualizar_reserva(id: int, reserva: ReservaSchema, db: Session = Depends(get_db)):
    registro = db.query(ReservaModel).filter(ReservaModel.id == id).first() 
    logging.info("PUT_RESERVA")
    
    old = {k.name: getattr(registro, k.name) for k in registro.__table__.columns}
    
    if not registro:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva: {id} não existe no banco de dados."
        )
    
    for key, value in reserva.model_dump().items():
        setattr(registro, key, value) 
    
    db.commit()
    db.refresh(registro)
    
    return {
        "reserva_old": old,
        "reserva_new": registro
    }
    
    
@router.delete("/reserva/{id}")
async def deleta_reserva(id: int, db: Session = Depends(get_db)):
    registro = db.query(ReservaModel).filter(ReservaModel.id == id)
    logging.info("DELETE_RESERVA")
    if registro == None:
        logging.warning(f"Registro {id} inexistente.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reserva: {id} não existe no banco de dados.")
    else:
        registro.delete(synchronize_session=False)
        db.commit()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/voos/reserva")
async def reservar_voo(id_usuario: int, reserva_dados: ReservaCompra, db: Session = Depends(get_db)):
    
    sessao = db.query(SessaoModel).filter(SessaoModel.id_usuario == id_usuario).first()
    
    if not sessao or not validar_sessao(sessao.id, db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça o login.")
    
    voo = db.query(VooModel).filter(VooModel.id == reserva_dados.id_voo).first()
    if not voo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voo não encontrado.")
    
    if voo.data_partida <= datetime.datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voo já partiu.")

    if voo.vagas < reserva_dados.quantidade_passageiros:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vagas insuficientes para o número de passageiros.")

    tarifa_total = voo.tarifa_por_passageiro * reserva_dados.quantidade_passageiros
    
    novo_voo = VooSchema(
        id_aeroporto_org=voo.id_aeroporto_org,
        id_aeroporto_dest=voo.id_aeroporto_dest,
        numero_voo=voo.numero_voo,
        tarifa_por_passageiro=voo.tarifa_por_passageiro,
        data_partida=voo.data_partida,
        data_chegada=voo.data_chegada,
        vagas=(voo.vagas - reserva_dados.quantidade_passageiros),
        status=voo.status
    )
    reg = db.query(VooModel).filter(VooModel.id == voo.id).first()
    for key, value in novo_voo.model_dump().items():
        setattr(reg, key, value)
    db.commit()
    db.refresh(reg)
    
    e_tickets = [gerar_e_ticket() for _ in range(reserva_dados.quantidade_passageiros)]
    
    nova_reserva = ReservaModel(
        id_usuario=id_usuario,
        id_voo=voo.id,
        quantidade_passageiros=reserva_dados.quantidade_passageiros,
        tarifa_total=tarifa_total,
        data_reserva=datetime.datetime.now(),
        status="Confirmada",
        e_tickets=",".join(e_tickets)
    )
    
    db.add(nova_reserva)
    db.commit()
    db.refresh(nova_reserva)

    localizador = nova_reserva.id
    return {
        "localizador": localizador,
        "e_tickets": e_tickets,
        "tarifa_total": tarifa_total
    }