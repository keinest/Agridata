"""Analytics routes: exploitation stats and dashboard."""
from flask import Blueprint, g, jsonify, request

from backend.app.api.dependencies import get_accessible_exploitation, require_auth
from backend.app.database import db

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/exploitations/stats")
@require_auth
def get_exploitation_stats():
    user = g.current_user
    exploitation_id = request.args.get("exploitation_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not exploitation_id:
        return jsonify({"detail": "'exploitation_id' is required"}), 400

    exploitation, err = get_accessible_exploitation(exploitation_id)
    if err:
        return err

    # Fetch related records
    rendements = db.query("rendements", {"tenant_id": user.tenant_id, "exploitation_id": exploitation_id})
    meteo_data = db.query("meteo_data", {"tenant_id": user.tenant_id, "exploitation_id": exploitation_id})
    intrants = db.query("intrants", {"tenant_id": user.tenant_id, "exploitation_id": exploitation_id})

    # Optional date filtering
    if start_date:
        rendements = [r for r in rendements if r.get("date_recolte", "") >= start_date]
        meteo_data = [m for m in meteo_data if m.get("date_observation", "") >= start_date]
        intrants = [i for i in intrants if i.get("date_application", "") >= start_date]
    if end_date:
        rendements = [r for r in rendements if r.get("date_recolte", "") <= end_date]
        meteo_data = [m for m in meteo_data if m.get("date_observation", "") <= end_date]
        intrants = [i for i in intrants if i.get("date_application", "") <= end_date]

    quantities = [r.get("quantity", 0) for r in rendements if r.get("quantity") is not None]
    total_rendements = len(rendements)
    avg_rendement = sum(quantities) / len(quantities) if quantities else None
    max_rendement = max(quantities) if quantities else None
    min_rendement = min(quantities) if quantities else None
    total_cost_intrants = sum(i.get("cost", 0) or 0 for i in intrants)
    humidities = [m.get("humidity") for m in meteo_data if m.get("humidity") is not None]
    avg_humidity = sum(humidities) / len(humidities) if humidities else None
    temperatures = [m.get("temperature_avg") for m in meteo_data if m.get("temperature_avg") is not None]
    avg_temperature = sum(temperatures) / len(temperatures) if temperatures else None

    return jsonify(
        {
            "total_rendements": total_rendements,
            "avg_rendement": avg_rendement,
            "max_rendement": max_rendement,
            "min_rendement": min_rendement,
            "total_cost_intrants": total_cost_intrants,
            "avg_humidity": avg_humidity,
            "avg_temperature": avg_temperature,
        }
    )


@analytics_bp.get("/dashboard")
@require_auth
def get_dashboard():
    user = g.current_user
    filters: dict = {"tenant_id": user.tenant_id}
    if user.role == "agriculteur":
        filters["owner_id"] = user.id

    exploitations = db.query("exploitations", filters)
    dashboard_data = []

    for expl in exploitations:
        expl_id = expl.get("id")
        rendements_count = len(db.query("rendements", {"exploitation_id": expl_id}))
        parcelles_count = len(db.query("parcelles", {"exploitation_id": expl_id}))
        expl_data = {
            "id": expl_id,
            "name": expl.get("name"),
            "region": expl.get("region"),
            "total_area": expl.get("total_area"),
            "area_unit": expl.get("area_unit"),
            "rendements_count": rendements_count,
            "parcelles_count": parcelles_count,
        }
        dashboard_data.append(expl_data)

    return jsonify(
        {
            "exploitations": dashboard_data,
            "total_exploitations": len(exploitations),
        }
    )


@analytics_bp.get("/health")
def analytics_health():
    return jsonify({"status": "healthy"})
