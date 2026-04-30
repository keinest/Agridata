"""Data collection routes: rendements, meteo, sol_qualite, intrants."""
from flask import Blueprint, g, jsonify, request

from backend.app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    require_auth,
)
from backend.app.database import db

data_collection_bp = Blueprint("data_collection", __name__)


# ─────────────────────────────── RENDEMENTS ────────────────────────────────

@data_collection_bp.post("/rendements/")
@require_auth
def create_rendement():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    parcelle_id = body.get("parcelle_id")
    if not parcelle_id:
        return jsonify({"detail": "'parcelle_id' is required"}), 400

    parcelle, err = get_accessible_parcelle(int(parcelle_id))
    if err:
        return err

    rendement_data = {
        "tenant_id": user.tenant_id,
        "parcelle_id": parcelle.id,
        "exploitation_id": parcelle.exploitation_id,
        "date_recolte": body.get("date_recolte", ""),
        "quantity": body.get("quantity"),
        "unit": body.get("unit"),
        "crop_type": body.get("crop_type"),
        "quality_rating": body.get("quality_rating"),
        "notes": body.get("notes"),
    }
    result = db.insert("rendements", rendement_data)
    return jsonify(result), 201


@data_collection_bp.get("/rendements/")
@require_auth
def list_rendements():
    user = g.current_user
    parcelle_id = request.args.get("parcelle_id", type=int)

    filters: dict = {"tenant_id": user.tenant_id}
    if parcelle_id:
        filters["parcelle_id"] = parcelle_id

    rendements_data = db.query("rendements", filters)
    return jsonify(sorted(rendements_data, key=lambda r: r.get("date_recolte", ""), reverse=True))


@data_collection_bp.delete("/rendements/<int:rendement_id>")
@require_auth
def delete_rendement(rendement_id: int):
    user = g.current_user
    rendement = db.get_by_id("rendements", rendement_id)
    if not rendement or rendement.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Rendement not found"}), 404
    db.delete("rendements", rendement_id)
    return jsonify({"detail": "Rendement deleted"})


# ─────────────────────────────── METEO DATA ────────────────────────────────

@data_collection_bp.post("/meteo/")
@require_auth
def create_meteo():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    exploitation_id = body.get("exploitation_id")
    if not exploitation_id:
        return jsonify({"detail": "'exploitation_id' is required"}), 400

    exploitation, err = get_accessible_exploitation(int(exploitation_id))
    if err:
        return err

    meteo_data = {
        "tenant_id": user.tenant_id,
        "exploitation_id": exploitation.id,
        "date_observation": body.get("date_observation", ""),
        "temperature_min": body.get("temperature_min"),
        "temperature_max": body.get("temperature_max"),
        "temperature_avg": body.get("temperature_avg"),
        "precipitation": body.get("precipitation"),
        "humidity": body.get("humidity"),
        "wind_speed": body.get("wind_speed"),
        "pressure": body.get("pressure"),
        "source": body.get("source", "manual"),
    }
    result = db.insert("meteo_data", meteo_data)
    return jsonify(result), 201


@data_collection_bp.get("/meteo/")
@require_auth
def list_meteo():
    user = g.current_user
    exploitation_id = request.args.get("exploitation_id", type=int)

    filters: dict = {"tenant_id": user.tenant_id}
    if exploitation_id:
        filters["exploitation_id"] = exploitation_id

    meteo_data = db.query("meteo_data", filters)
    return jsonify(sorted(meteo_data, key=lambda m: m.get("date_observation", ""), reverse=True))


@data_collection_bp.delete("/meteo/<int:meteo_id>")
@require_auth
def delete_meteo(meteo_id: int):
    user = g.current_user
    record = db.get_by_id("meteo_data", meteo_id)
    if not record or record.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Meteo data not found"}), 404
    db.delete("meteo_data", meteo_id)
    return jsonify({"detail": "Meteo data deleted"})


# ─────────────────────────────── SOL QUALITE ───────────────────────────────

@data_collection_bp.post("/sol/")
@require_auth
def create_sol_qualite():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    parcelle_id = body.get("parcelle_id")
    if not parcelle_id:
        return jsonify({"detail": "'parcelle_id' is required"}), 400

    parcelle, err = get_accessible_parcelle(int(parcelle_id))
    if err:
        return err

    sol_data = {
        "tenant_id": user.tenant_id,
        "parcelle_id": parcelle.id,
        "exploitation_id": parcelle.exploitation_id,
        "date_analyse": body.get("date_analyse", ""),
        "ph": body.get("ph"),
        "azote": body.get("azote"),
        "phosphore": body.get("phosphore"),
        "potassium": body.get("potassium"),
        "matiere_organique": body.get("matiere_organique"),
        "calcium": body.get("calcium"),
        "magnesium": body.get("magnesium"),
    }
    result = db.insert("sol_qualite", sol_data)
    return jsonify(result), 201


@data_collection_bp.get("/sol/")
@require_auth
def list_sol_qualite():
    user = g.current_user
    parcelle_id = request.args.get("parcelle_id", type=int)

    filters: dict = {"tenant_id": user.tenant_id}
    if parcelle_id:
        filters["parcelle_id"] = parcelle_id

    sol_data = db.query("sol_qualite", filters)
    return jsonify(sol_data)


@data_collection_bp.delete("/sol/<int:sol_id>")
@require_auth
def delete_sol_qualite(sol_id: int):
    user = g.current_user
    record = db.get_by_id("sol_qualite", sol_id)
    if not record or record.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Sol data not found"}), 404
    db.delete("sol_qualite", sol_id)
    return jsonify({"detail": "Sol data deleted"})


# ─────────────────────────────── INTRANTS ──────────────────────────────────

@data_collection_bp.post("/intrants/")
@require_auth
def create_intrant():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    parcelle_id = body.get("parcelle_id")
    if not parcelle_id:
        return jsonify({"detail": "'parcelle_id' is required"}), 400

    parcelle, err = get_accessible_parcelle(int(parcelle_id))
    if err:
        return err

    intrant_data = {
        "tenant_id": user.tenant_id,
        "parcelle_id": parcelle.id,
        "exploitation_id": parcelle.exploitation_id,
        "type": body.get("type", ""),
        "name": body.get("name", ""),
        "quantity": body.get("quantity"),
        "date_application": body.get("date_application", ""),
        "cost": body.get("cost"),
        "effectiveness": body.get("effectiveness"),
    }
    result = db.insert("intrants", intrant_data)
    return jsonify(result), 201


@data_collection_bp.get("/intrants/")
@require_auth
def list_intrants():
    user = g.current_user
    parcelle_id = request.args.get("parcelle_id", type=int)

    filters: dict = {"tenant_id": user.tenant_id}
    if parcelle_id:
        filters["parcelle_id"] = parcelle_id

    intrants_data = db.query("intrants", filters)
    return jsonify(intrants_data)


@data_collection_bp.delete("/intrants/<int:intrant_id>")
@require_auth
def delete_intrant(intrant_id: int):
    user = g.current_user
    record = db.get_by_id("intrants", intrant_id)
    if not record or record.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Intrant not found"}), 404
    db.delete("intrants", intrant_id)
    return jsonify({"detail": "Intrant deleted"})
