"""Signal refresh and change-feed endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.schemas import (
    ProvenanceSource,
    SignalChangesResponse,
    SignalsRefreshRequest,
    SignalsRefreshResponse,
)
from app.services.brightdata_client import get_brightdata_client
from app.services.signals_service import get_signal_changes, refresh_signals

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.post("/refresh", response_model=SignalsRefreshResponse)
async def refresh_activity_signals(
    body: SignalsRefreshRequest,
    session: Session = Depends(get_session),
) -> SignalsRefreshResponse:
    """Refresh activity signals in live-or-cached mode."""
    items = await refresh_signals(
        session=session,
        property_ids=body.property_ids,
        limit=body.limit,
        force_live=body.force_live,
    )
    client = get_brightdata_client()
    mode = "live" if client.is_configured else "cached_simulated"
    source = ProvenanceSource(
        id="brightdata-refresh",
        label="Bright Data refresh pipeline",
        source_type="bright_data",
        is_live=client.is_configured,
        observed_at=datetime.now(timezone.utc),
        confidence=0.86 if client.is_configured else 0.62,
        url="https://docs.brightdata.com/scraping-automation/crawl-api/quick-start",
        note="Hybrid mode enabled. Simulated fallback is used when credentials are missing.",
    )
    return SignalsRefreshResponse(
        refreshed_count=len(items),
        mode=mode,
        items=items,
        sources=[source],
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/changes", response_model=SignalChangesResponse)
def signal_change_feed(
    window_hours: int = Query(24, ge=1, le=168),
    session: Session = Depends(get_session),
) -> SignalChangesResponse:
    """Get recent changes in activity signals over a time window."""
    changes = get_signal_changes(session=session, window_hours=window_hours)
    source = ProvenanceSource(
        id="signal-delta",
        label="Signal delta engine",
        source_type="derived_analytics",
        is_live=True,
        observed_at=datetime.now(timezone.utc),
        confidence=0.74,
        note="Compares latest two snapshots per property.",
    )
    return SignalChangesResponse(
        window_hours=window_hours,
        changes=changes,
        generated_at=datetime.now(timezone.utc),
        sources=[source],
    )
