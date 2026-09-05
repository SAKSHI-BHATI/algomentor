from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.routes.ai_routes import router as ai_router
from Backend.routes.auth_routes import router as auth_router
from Backend.routes.execute_routes import router as execute_router
from Backend.data_seeder import seed_database

app = FastAPI(
    title="AlgoMentor API",
    description="Backend services for AI-assisted DSA learning and simulation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    seed_database()

app.include_router(auth_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(execute_router)

@app.get("/")
def home():
    return {"message": "Algomentor Backend Running 🚀", "docs_url": "/docs"}