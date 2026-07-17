from motor.motor_asyncio import AsyncIOMotorClient


from fastapi import FastAPI, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware

# XXXXXXX RUTAS XXXXXXXXXXXXXXXXXXXXXXXX
from Login.Login import Ruta_Login
from Registro.Registro import Ruta_Registro

# para correr el server se usa uvicorn main:app --reload
# XXXXXXXXXX MOFULOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from Plantillas import Usuario, Consulta

import MongoDB.Base_Datos as BD
import TOKEN.Token


from openai import AsyncOpenAI


import json
import time


import os
from dotenv import load_dotenv  # para mis variables deentorno
load_dotenv()  # para mis variables deentorno

uri = os.getenv("URL_MongoDB")
api_key = os.getenv("OPENAI_API_KEY", "")


app = FastAPI()

# Cliente ASYNC de OpenAI: permite usar "await" en las llamadas y no bloquea
# el event loop de FastAPI. Esto hace que múltiples peticiones a /whatsapp
# se puedan procesar de forma concurrente en vez de en serie.
client = AsyncOpenAI(
    api_key=api_key
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # idealmente restringe esto a tu extensión
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(Ruta_Login)
app.include_router(Ruta_Registro)


@app.on_event("startup")
async def Inicio_API():
    BD.client = AsyncIOMotorClient(os.getenv("URL_MongoDB"))
    # Me da la direccion de la Base de datos
    BD.Base_Datos = BD.client["Usuarios"]
    # Me da la direccion de donde tengo almacenados los usuarios en la Base de datos
    BD.UsuarioBD = BD.Base_Datos["Usuarios_plantilla"]
    await BD.UsuarioBD.create_index("email", unique=True)


@app.on_event("shutdown")
async def Cerrar_API():
    if BD.client is not None:
        BD.client.close()

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


@app.get("/Perfil")
async def Perfil(Usuario_data: str = Depends(TOKEN.Token.Extraer_token)):
    print("Usuario_data: ", Usuario_data)
    return Usuario_data


@app.post("/whatsapp")
async def webhook(data: Consulta, Usuario=Depends(TOKEN.Token.Extraer_token)):

    print("Datos recibidos de Extension:")
    mensaje_usuario = data.pregunta
    numero_usuario = data.numero_usuario
    historial = data.historial or []

    print(
        f"\nmensaje_usuario: {mensaje_usuario}\n"
        f"numero_usuario: {numero_usuario}\n"
    )

    inicio = time.time()

    # Con AsyncOpenAI, esta llamada ahora se espera con "await" en vez de
    # ser una llamada bloqueante. Esto libera el event loop mientras se
    # espera la respuesta de OpenAI, permitiendo atender otras peticiones
    # concurrentemente.
    response = await client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": """- Descripción general\nEres mi asistente, te daré documentos y con base en ellos me ayudarás a gestionar dudas de los clientes que me contactan, mi canal principal es chat (WhatsApp), necesito saber qué procedimientos realizar de forma concisa para dar solución a los problemas, identificar cuándo debo gestionarlos directamente y cuándo debo conferir,
                         transferir o agendar una llamada al área encargada.\n- Líneas de atención\nWhatsApp (chats), llamadas, quejas y reclamos, fidelización, les básica, les konecta, soporte crédito hipotecario, Cardif, referidos, Sura, asistencias AXA, leasing, televenta Bancolombia, fiduciaria Bancolombia, entre otras.\n- Conferencias y transferencias\nLas conferencias se realizan únicamente desde la línea telefónica, 
                         las transferencias por chat (WhatsApp) solo se permiten en dos casos: línea de quejas y reclamos, línea de colombianos en el exterior, si no es posible transferir o conferir desde WhatsApp se debe agendar una llamada, las transferencias por llamadas no tienen límite y se pueden realizar sin inconveniente, las conferencias solo se realizan por llamada.
                         \n- Procedimiento de respuesta\nPrimero indicar si el caso lo atiendo yo (chat WhatsApp), si se transfiere o si se confiere, después dar una descripción de la solución, si existe un procedimiento incluirlo paso a paso, sugerir un código de tipificación según el archivo “codificacion.docx” (solo se puede usar un código pero se pueden recomendar máximo tres), 
                         si la solución requiere radicar el proceso incluir el paso a paso, si no hay requerimiento dentro de la solución no se incluye nada adicional, si la información se puede obtener a través de AS400 poner los pasos, si no aplica escribir “AS400 no aplica”.\n- Notas adicionales\nAS400 es una herramienta de consultas en consola de comandos, sucursal virtual personas es un aplicativo web de Bancolombia, 
                         sucursal virtual personas es la página web de Bancolombia para los usuarios y se abrevia SVP, gestor transaccional es una herramienta también, es un aplicativo pero para los agentes de Bancolombia, TD es tarjeta débito, TDC es tarjeta de crédito, CxC es cuentas por cobrar."""
                    }
                ]
            }, *historial,
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": mensaje_usuario
                    }
                ]
            },
        ],
        text={
            "format": {
                "type": "text"
            },
            "verbosity": "medium"
        },
        reasoning={
            "effort": "medium",
            "summary": "auto"
        },
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [
                    "vs_6a4472c79fdc8191bee1d8968140255e"
                ]
            }
        ],
        store=True,
        include=[
            "reasoning.encrypted_content",
            "web_search_call.action.sources"
        ]
    )

    print("Tiempo:", time.time() - inicio)

    respuesta_ia = response.output_text
    print("Respuesta IA: Enviada")
    # print(respuesta_ia)

    return {
        "respuestaIA": respuesta_ia
    }
