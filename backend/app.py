from backend.routes import agent_routes, donation_routes
from fastapi import FastAPI
from database import Base, engine

from routes import auth_routes, org_routes, admin_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(donation_routes.router, prefix="/donor")
app.include_router(agent_routes.router, prefix="/ngo")
app.include_router(org_routes.router, prefix="/org")
app.include_router(admin_routes.router, prefix="/admin")