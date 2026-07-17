
# Librerias para desemcriptar token
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status


import os  # para mis variables deentorno
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext  # libreria para encriptar contraseñas

from dotenv import load_dotenv  # para mis variables deentorno
load_dotenv("../.env")  # para mis variables deentorno


# algoritmo de encriptacion bcrypt para la contraseña
Encriptar = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = os.getenv("SECRET_KEY", "123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


def crear_token(email: str, Tiempo_expiracion=ACCESS_TOKEN_EXPIRE_MINUTES):
    # creo una fecha y hora de expiracion del token
    expire = datetime.utcnow() + timedelta(minutes=Tiempo_expiracion)

    Token = {
        "email": email,
        "exp": expire
    }

    # retorno el token
    return jwt.encode(Token, SECRET_KEY, algorithm=ALGORITHM)


'''
Extructura de un TOKEN
{
    "sub": "jhon",
    "rol": "admin",
    "exp": 1783962156
}
'''


def verificar_token(token: str):
    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=[ALGORITHM])  # desencripto el token
        print(payload)
        return payload
    except JWTError:
        return None


def Encriptar_password(password: str):
    password = Encriptar.hash(password)
    return password


def comparar_password(password, password_DB):
    # compara dos claves encriptadas aver si son iguales
    password = Encriptar.verify(password, password_DB)
    return password  # retorna un booleano


# tipo de autorizacion verifica si es Bearer y le quita ese string y se queda con el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def Extraer_token(token: str = Depends(oauth2_scheme)):

    print("Token: ", token)

    Token_Desemcriptado = verificar_token(token)

    if Token_Desemcriptado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    return Token_Desemcriptado
