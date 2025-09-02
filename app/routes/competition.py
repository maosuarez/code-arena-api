from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Body
from app.models_entity.competition import Competition, RequestCompetition
from app.database import db
import uuid

router = APIRouter()

@router.post("/create")
async def create_competition(req: RequestCompetition):
    # Validación de campos obligatorios
    required_fields = ["title", "date", "status"]
    missing = [field for field in required_fields if not getattr(req, field, None)]
    if missing:
        raise HTTPException(status_code=400, detail=f"Faltan campos: {', '.join(missing)}")

    dict_req = req.dict()
    dict_req['id'] = str(uuid.uuid4())  # Asegúrate de convertirlo a string si el modelo espera str

    # Validar y transformar el modelo
    try:
        comp = Competition.model_validate(dict_req, strict=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando el Competition: {str(e)}")


    # Verificar si ya existe una competición con ese título
    existing = await db["competition"].find_one({"id": comp.id})
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una competición")

    # Serializar para MongoDB
    comp_doc = comp.model_dump(mode="json")

    # Insertar en la base de datos
    try:
        result = await db["competition"].insert_one(comp_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")

    return {
        "message": "Competición creada exitosamente",
        "id": comp.title,
        "title": comp.title,
        "status": comp.status
    }


@router.get("/all")
async def get_all_competitions():
    try:
        raw_comps = await db["competition"].find().to_list(length=100)

        competitions = []
        for comp in raw_comps:
            comp.pop("_id")

            # Convertir fechas a datetime si están como string
            if "date" in comp and isinstance(comp["date"], str):
                try:
                    comp["date"] = datetime.fromisoformat(comp["date"])
                except Exception:
                    pass  # Si falla, se deja como está

            # Si hay fechas anidadas, como en problems
            if "problems" in comp:
                for p in comp["problems"]:
                    if "_id" in p:
                        p["id"] = str(p.pop("_id"))

            competitions.append(comp)

        return {"list": competitions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener competiciones: {str(e)}")


@router.post("/join")
async def join_team_to_competition(
    teamCode: str = Body(...),
    competitionId: str = Body(...)
):
    competition = await db["competition"].find_one({'id': competitionId})
    if not competition:
        raise HTTPException(status_code=404, detail="Competición no encontrada para ese usuario")

    teams = competition.get("teams", [])
    if teamCode in teams:
        raise HTTPException(status_code=400, detail="El equipo ya está registrado")

    teams.append(teamCode)

    try:
        await db["competition"].update_one(
            {"id": competitionId},
            {"$set": {"teams": teams}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar equipos: {str(e)}")

    return {
        "message": "Equipo registrado exitosamente",
        "username": competitionId,
        "teamCode": teamCode,
        "totalTeams": len(teams)
    }

@router.get("/{competitionId}")
async def get_competition_by_id(competitionId: str):
    competition = await db["competition"].find_one({"id": competitionId})
    if not competition:
        raise HTTPException(status_code=404, detail="Competición no encontrada")

    # Opcional: eliminar '_id' si no quieres exponerlo
    competition.pop("_id", None)

    # Asegurar que 'date' esté como datetime
    if "date" in competition and isinstance(competition["date"], str):
        try:
            competition["date"] = datetime.fromisoformat(competition["date"])
        except Exception:
            pass  # Si ya es datetime o falla la conversión, se deja como está

    return {"competition": competition}

