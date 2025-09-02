from fastapi import FastAPI
from app.routes import auth, competition, users, teams
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


app = FastAPI(title="Competencias Universitarias - Backend")

# Incluir rutas
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
#app.include_router(problems.router, prefix="/problems", tags=["Problems"])
app.include_router(competition.router, prefix="/competition", tags=["Competition"])

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Competencias Universitarias"}
