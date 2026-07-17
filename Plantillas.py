# define modelos de datos con validación automática.
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Usuario(BaseModel):  # alcrear esta clase eredada pydantic crea un constructor automaticamente y se encarga de validar los datos estipulados aqui
    username: str | None = None  # opcional
    email: str
    password: str


class Consulta(BaseModel):
    pregunta: str
    numero_usuario: str
    historial: Optional[List[Dict[str, Any]]] = []
