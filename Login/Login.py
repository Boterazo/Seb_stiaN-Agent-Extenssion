from fastapi import APIRouter
from fastapi import HTTPException, status

from Plantillas import Usuario

import MongoDB.Base_Datos as BD
import TOKEN.Token as Token
# prefix indica desde dondeempieza el end point
# tags es para que ladocumentacion este mejor ordenada con las rutas
Ruta_Login = APIRouter(prefix="/Login", tags=["/Login"])


@Ruta_Login.post("/")
async def login(datos: Usuario):
    print("email ", datos.email)
    print("password ", datos.password)

    # ESTA FUNCION DEVUELVE UN DICCIONARIO
    User = await BD.Buscar_Usuario(datos.email)

    if not User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email no registrado"
        )

    password = Token.comparar_password(
        password=datos.password,
        password_DB=User["password"]
    )

    if not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta"
        )

    token = Token.crear_token(email=User["email"])

    return {"access_token": token, "token_type": "bearer"}
