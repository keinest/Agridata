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

    total_parcelles = 0
    total_rendements = 0
    total_alertes_unread = 0

    for expl in exploitations:
        expl_id = expl.get("id")
        rendements_count = len(db.query("rendements", {"exploitation_id": expl_id}))
        parcelles_count = len(db.query("parcelles", {"exploitation_id": expl_id}))
        alertes_unread = len(db.query("alertes", {"exploitation_id": expl_id, "is_read": False}))

        total_parcelles += parcelles_count
        total_rendements += rendements_count
        total_alertes_unread += alertes_unread

        expl_data = {
            "id": expl_id,
            "name": expl.get("name"),
            "region": expl.get("region"),
            "total_area": expl.get("total_area"),
            "area_unit": expl.get("area_unit"),
            "rendements_count": rendements_count,
            "parcelles_count": parcelles_count,
            "alertes_unread": alertes_unread,
        }
        dashboard_data.append(expl_data)

    return jsonify(
        {
            "exploitations": dashboard_data,
            "summary": {
                "total_exploitations": len(exploitations),
                "total_parcelles": total_parcelles,
                "total_rendements": total_rendements,
                "total_alertes_unread": total_alertes_unread,
            }
        }
    )


@analytics_bp.get("/weather")
@require_auth
def get_weather_data():
    user = g.current_user
    exploitations = db.query("exploitations", {"tenant_id": user.tenant_id})
    if user.role == "agriculteur":
        exploitations = [e for e in exploitations if e.get("owner_id") == user.id]

    exploitation_ids = [e["id"] for e in exploitations]
    weather_data = []
    for eid in exploitation_ids:
        data = db.query("meteo_data", {"exploitation_id": eid})
        weather_data.extend(data)

    # Sort by date descending, take last 50
    weather_data.sort(key=lambda x: x.get("date_observation", ""), reverse=True)
    return jsonify(weather_data[:50])


@analytics_bp.get("/soil")
@require_auth
def get_soil_data():
    user = g.current_user
    parcelles = db.query("parcelles", {"tenant_id": user.tenant_id})
    parcelle_ids = [p["id"] for p in parcelles]
    soil_data = []
    for pid in parcelle_ids:
        data = db.query("sol_qualite", {"parcelle_id": pid})
        soil_data.extend(data)

    # Sort by date descending, take last 50
    soil_data.sort(key=lambda x: x.get("date_analyse", ""), reverse=True)
    return jsonify(soil_data[:50])


@analytics_bp.post("/reports/generate")
@require_auth
def generate_report():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    exploitation_id = body.get("exploitation_id")
    report_type = body.get("report_type", "summary")
    period_start = body.get("period_start")
    period_end = body.get("period_end")

    if not exploitation_id:
        return jsonify({"detail": "'exploitation_id' is required"}), 400

    exploitation, err = get_accessible_exploitation(exploitation_id)
    if err:
        return err

    # Gather data for report
    filters = {"tenant_id": user.tenant_id, "exploitation_id": exploitation_id}
    if period_start:
        filters["created_at"] = {"$gte": period_start}
    if period_end:
        filters["created_at"] = filters.get("created_at", {})
        filters["created_at"]["$lte"] = period_end

    rendements = db.query("rendements", filters)
    meteo_data = db.query("meteo_data", filters)
    sol_data = db.query("sol_qualite", filters)
    intrants = db.query("intrants", filters)

    # Generate report content
    report_content = {
        "exploitation": {
            "id": exploitation.id,
            "name": exploitation.name,
            "region": exploitation.region,
        },
        "period": {
            "start": period_start,
            "end": period_end,
        },
        "summary": {
            "total_rendements": len(rendements),
            "total_meteo_records": len(meteo_data),
            "total_sol_analyses": len(sol_data),
            "total_intrants": len(intrants),
            "avg_temperature": sum(m.get("temperature_avg", 0) for m in meteo_data) / len(meteo_data) if meteo_data else None,
            "avg_humidity": sum(m.get("humidity", 0) for m in meteo_data) / len(meteo_data) if meteo_data else None,
            "avg_ph": sum(s.get("ph", 0) for s in sol_data) / len(sol_data) if sol_data else None,
        },
        "rendements": rendements[:10],  # Last 10
        "meteo_recent": sorted(meteo_data, key=lambda x: x.get("date_observation", ""), reverse=True)[:5],
        "sol_recent": sorted(sol_data, key=lambda x: x.get("date_analyse", ""), reverse=True)[:5],
    }

    # Save report
    report_data = {
        "tenant_id": user.tenant_id,
        "exploitation_id": exploitation.id,
        "created_by": user.id,
        "report_type": report_type,
        "period_start": period_start,
        "period_end": period_end,
        "format": "json",
        "content": report_content,
    }
    report = db.insert("rapports", report_data)

    return jsonify({
        "id": report["id"],
        "message": "Report generated successfully",
        "report": report_content
    }), 201
