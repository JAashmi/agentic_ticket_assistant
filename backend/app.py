from fastapi import FastAPI
from database import Base, engine
from routes import auth_routes, donor_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(donor_routes.router)