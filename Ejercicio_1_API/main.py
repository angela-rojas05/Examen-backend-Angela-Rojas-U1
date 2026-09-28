from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Laptop


app = FastAPI()


# Crear tablas

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Crear laptops

class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


# Insertar datos iniciales

def cargar_datos_iniciales():
    db = SessionLocal()

    try:
        cantidad = db.query(Laptop).count()

        if cantidad == 0:

            laptops_iniciales = [
                Laptop(
                    marca="Dell",
                    modelo="Latitude 5440",
                    ram_gb=16,
                    disponible=True
                ),
                Laptop(
                    marca="Lenovo",
                    modelo="ThinkPad E14",
                    ram_gb=8,
                    disponible=False
                ),
                Laptop(
                    marca="HP",
                    modelo="ProBook 450",
                    ram_gb=16,
                    disponible=True
                )
            ]

            db.add_all(laptops_iniciales)
            db.commit()

    finally:
        db.close()


cargar_datos_iniciales()

# GET /

@app.get("/")
def inicio():
    return {
        "mensaje": "API del laboratorio de cómputo"
    }


# GET /laptops

@app.get("/laptops")
def obtener_laptops(db: Session = Depends(get_db)):

    laptops = db.query(Laptop).order_by(Laptop.id).all()

    return laptops


# GET /laptops/disponibles

@app.get("/laptops/disponibles")
def obtener_laptops_disponibles(
    db: Session = Depends(get_db)
):

    laptops = (
        db.query(Laptop)
        .filter(Laptop.disponible == True)
        .order_by(Laptop.id)
        .all()
    )

    return laptops


# GET /laptops/{laptop_id}

@app.get("/laptops/{laptop_id}")
def obtener_laptop(
    laptop_id: int,
    db: Session = Depends(get_db)
):

    laptop = (
        db.query(Laptop)
        .filter(Laptop.id == laptop_id)
        .first()
    )

    if laptop is None:
        raise HTTPException(
            status_code=404,
            detail="Laptop no encontrada"
        )

    return laptop


# POST /laptops

@app.post("/laptops")
def crear_laptop(
    datos: LaptopCreate,
    db: Session = Depends(get_db)
):

    nueva_laptop = Laptop(
        marca=datos.marca,
        modelo=datos.modelo,
        ram_gb=datos.ram_gb,
        disponible=True
    )

    db.add(nueva_laptop)

    db.commit()

    db.refresh(nueva_laptop)

    return nueva_laptop