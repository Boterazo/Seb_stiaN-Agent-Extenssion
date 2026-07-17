from fastapi import APIRouter
from Plantillas import Usuario
import MongoDB.Base_Datos as BD

# prefix indica desde dondeempieza el end point
# tags es para que ladocumentacion este mejor ordenada con las rutas
Ruta_Registro = APIRouter(prefix="/Registrar", tags=["/Registrar"])


@Ruta_Registro.post("/")
async def Registrar(dato: Usuario):

    estado = await BD.Crear_Usuario(dato)

    return estado
