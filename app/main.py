from fastapi import FastAPI

from routers.aeroporto.aeroporto import router as AeroportoRouter
from routers.reserva.reserva import router as ReservaRouter
from routers.sessao.sessao import router as SessaoRouter
from routers.usuario.usuario import router as UsuarioRouter
from routers.voo.voo import router as VooRouter
from routers.auth import remover_sessoes_expiradas

from models.database import engine
from models.aeroporto.aeroporto import Base

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

Base.metadata.create_all(bind=engine)

app = FastAPI()

scheduler = AsyncIOScheduler()
scheduler.add_job(
    func=remover_sessoes_expiradas,
    trigger=IntervalTrigger(minutes=10)
)
scheduler.start()


app.include_router(AeroportoRouter)
app.include_router(ReservaRouter)
app.include_router(SessaoRouter)
app.include_router(UsuarioRouter)
app.include_router(VooRouter)
