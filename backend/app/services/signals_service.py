"""Signal refresh and change-tracking utilities."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select

from app.models.property import Property, SignalSnapshot, WebSignal
from app.services.brightdata_client import get_brightdata_client


def _utcnow() -> datetime:
    return datetime.utcnow()


def latest_web_signal(session: Session, property_id: int) -> Optional[WebSignal]:
    """Return the latest cached web signal for a property."""
    signals = session.exec(
        select(WebSignal)
        .where(WebSignal.property_id == property_id)
        .order_by(WebSignal.fetched_at.desc())  # type: ignore[union-attr]
    ).all()
    return signals[0] if signals else None


async def refresh_signal_for_property(
    session: Session,
    property_id: int,
    force_live: bool = False,
) -> Optional[dict]:
    """Refresh and persist one property's activity signals."""
    prop = session.get(Property, property_id)
    if not prop:
        return None

    client = get_brightdata_client()
    # `force_live` is best-effort. If token is missing, client simulates.
    del force_live

    payload = await client.fetch_activity_signals(prop.latitude, prop.longitude)
    fetched_at = _utcnow()
    is_live = bool(payload.get("is_live", client.is_configured))

    current = latest_web_signal(session, property_id)
    if current:
        current.poi_count = int(payload.get("poi_count", 0))
        current.avg_rating = float(payload.get("avg_rating", 0) or 0)
        current.review_count = int(payload.get("review_count", 0))
        current.competitor_count = int(payload.get("competitor_count", 0))
        current.source = str(payload.get("source", "brightdata"))
        current.fetched_at = fetched_at
        session.add(current)
    else:
        current = WebSignal(
            property_id=property_id,
            poi_count=int(payload.get("poi_count", 0)),
            avg_rating=float(payload.get("avg_rating", 0) or 0),
            review_count=int(payload.get("review_count", 0)),
            competitor_count=int(payload.get("competitor_count", 0)),
            source=str(payload.get("source", "brightdata")),
            fetched_at=fetched_at,
        )
        session.add(current)

    snapshot = SignalSnapshot(
        property_id=property_id,
        poi_count=current.poi_count,
        avg_rating=current.avg_rating,
        review_count=current.review_count,
        competitor_count=current.competitor_count,
        activity_index=float(payload.get("activity_index", 0.0)),
        source=current.source,
        is_live=is_live,
        fetched_at=fetched_at,
    )
    session.add(snapshot)
    session.commit()

    return {
        "property_id": property_id,
        "address": prop.address,
        "activity_index": float(payload.get("activity_index", 0.0)),
        "is_live": is_live,
        "source": str(payload.get("source", "brightdata")),
        "fetched_at": fetched_at,
    }


async def refresh_signals(
    session: Session,
    property_ids: Optional[list[int]] = None,
    limit: int = 50,
    force_live: bool = False,
) -> list[dict]:
    """Refresh signals for selected properties (or top-N by id)."""
    if property_ids:
        props = session.exec(
            select(Property).where(Property.id.in_(property_ids))
        ).all()
    else:
        props = session.exec(select(Property).limit(limit)).all()

    results: list[dict] = []
    for prop in props:
        item = await refresh_signal_for_property(
            session=session,
            property_id=prop.id,  # type: ignore[arg-type]
            force_live=force_live,
        )
        if item:
            results.append(item)
    return results


def get_signal_changes(
    session: Session,
    window_hours: int = 24,
    limit: int = 100,
) -> list[dict]:
    """Return per-property activity deltas from the latest two snapshots."""
    cutoff = _utcnow() - timedelta(hours=window_hours)
    snapshots = session.exec(
        select(SignalSnapshot).order_by(
            SignalSnapshot.property_id.asc(),
            SignalSnapshot.fetched_at.desc(),  # type: ignore[union-attr]
        )
    ).all()

    by_property: dict[int, list[SignalSnapshot]] = {}
    for snap in snapshots:
        if snap.property_id not in by_property:
            by_property[snap.property_id] = []
        if len(by_property[snap.property_id]) < 2:
            by_property[snap.property_id].append(snap)

    changes: list[dict] = []
    for property_id, pair in by_property.items():
        if len(pair) < 2:
            continue
        latest, previous = pair[0], pair[1]
        if latest.fetched_at < cutoff:
            continue
        prop = session.get(Property, property_id)
        if not prop:
            continue
        delta = round(latest.activity_index - previous.activity_index, 2)
        changes.append(
            {
                "property_id": property_id,
                "address": prop.address,
                "previous_activity_index": previous.activity_index,
                "current_activity_index": latest.activity_index,
                "delta_activity_index": delta,
                "previous_fetched_at": previous.fetched_at,
                "current_fetched_at": latest.fetched_at,
            }
        )

    changes.sort(key=lambda c: abs(c["delta_activity_index"]), reverse=True)
    return changes[:limit]
