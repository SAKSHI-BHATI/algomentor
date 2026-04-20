from fastapi import FastAPI
from Backend.routes.ai_routes import router
from fastapi.middleware.cors import CORSMiddleware
from Backend.routes.ai_routes import router as ai_router
app = FastAPI()
app.include_router(ai_router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Algomentor Backend Running 🚀"}