"""CSV export route."""

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models.property import Property, PropertyScore

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/csv")
def export_csv(
    scenario: str = Query("general"),
    persona: str = Query("city_console"),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Export the ranked property list as CSV."""
    stmt = (
        select(PropertyScore)
        .where(PropertyScore.scenario == scenario)
        .order_by(PropertyScore.overall_score.desc())  # type: ignore[union-attr]
    )
    scores = session.exec(stmt).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "rank",
            "property_id",
            "parcel_id",
            "address",
            "neighborhood",
            "overall_score",
            "foot_traffic",
            "competition",
            "safety",
            "equity",
            "activity",
            "scenario",
        ]
    )

    for rank, ps in enumerate(scores, start=1):
        prop = session.get(Property, ps.property_id)
        if not prop:
            continue
        writer.writerow(
            [
                rank,
                prop.id,
                prop.parcel_id,
                prop.address,
                prop.neighborhood or "",
                ps.overall_score,
                ps.foot_traffic_score,
                ps.competition_score,
                ps.safety_score,
                ps.equity_score,
                ps.activity_index,
                ps.scenario,
            ]
        )

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=urbanpulse_export.csv"},
    )
