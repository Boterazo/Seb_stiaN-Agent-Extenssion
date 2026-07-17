# XXXXXXXXXXXXXXXXXXXXXXX MONGO DB XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import *


# XXXXXXXXXXXX PLANTILLAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from Plantillas import Usuario
from TOKEN.Token import Encriptar_password
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from bson import json_util
import json


client: AsyncIOMotorClient | None = None
Base_Datos: AsyncIOMotorDatabase | None = None
UsuarioBD: AsyncIOMotorCollection | None = None


async def Buscar_Usuario(email: str):
    if UsuarioBD is None:
        raise RuntimeError("La base de datos no ha sido inicializada.")

    #print("Coleccion: ", UsuarioBD.name," Base de datos: ", UsuarioBD.database.name)
    # print("Usuarios: ", await UsuarioBD.find().to_list(length=None))
    user = await UsuarioBD.find_one({"email": email})

    if not user:
        return False

    user = json.loads(json_util.dumps(user))
    # borro el id para que no se vea a la hora dellamar a la base de datos completa
    user.pop("_id", None)
    print("Usuario_BD: ", user)
    return user


async def Crear_Usuario(user: Usuario):
    if UsuarioBD is not None:

        password = Encriptar_password(user.password)
        user.password = password

        try:
            await UsuarioBD.insert_one(user.dict())
            return {"INFO": "USUARIO REGISTRADO", "NOMBRE": user.email}

        except DuplicateKeyError as e:
            print("error:", type(e))
            raise RuntimeError("Email ya reguistrado en la base de datos")

        except Exception as e:
            print("ERROR:", e)
            raise RuntimeError("Error DESCONOCIDO")


async def Eliminar_Usuario(email: str):
    if UsuarioBD is not None:

        resultado = await UsuarioBD.delete_one({"email": email})

        # se enfiara true sicumple condision si no un false
        return resultado.deleted_count == 1


async def Actualizar_Usuario(email: str, user: Usuario):
    if UsuarioBD is None:
        raise RuntimeError("La base de datos no ha sido inicializada.")

    datos = user.model_dump()

    datos["password"] = Encriptar_password(datos["password"])

    resultado = await UsuarioBD.update_one(
        {"email": email},
        {"$set": datos}
    )

    # se enfiara true sicumple condision si no un false
    return resultado.modified_count == 1
