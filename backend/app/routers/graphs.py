from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.db.mongodb import get_database
from app.dependencies import verify_jwt_or_api_key
from app.utils.graph import (
    build_efficiency_scatter,
    build_expiration_timeline,
    build_last_used_timeline,
    build_tokens_per_call_bar,
    build_total_tokens_pie,
)

router = APIRouter(prefix="/api/v1/graphs", tags=["graphs"])


class GraphResponse(BaseModel):
    chart_id: str
    title: str
    description: str
    figure: Dict[str, Any]
    meta: Dict[str, Any]


@router.get("/total-tokens", response_model=GraphResponse)
async def total_tokens_chart(
    project_id: Optional[str] = Query(
        None,
        description="Filter by project identifier if provided.",
    ),
    _: str = Depends(verify_jwt_or_api_key),
) -> GraphResponse:
    records = await _fetch_usage_documents(project_id)
    return GraphResponse(
        chart_id="total_tokens_pie",
        title="Total token consumption",
        description="Share of total project tokens attributed to each teammate.",
        figure=_ensure_dict(build_total_tokens_pie(records)),
        meta=_build_meta(records, project_id),
    )


@router.get("/tokens-per-call", response_model=GraphResponse)
async def tokens_per_call_chart(
    project_id: Optional[str] = Query(None),
    _: str = Depends(verify_jwt_or_api_key),
) -> GraphResponse:
    records = await _fetch_usage_documents(project_id)
    return GraphResponse(
        chart_id="tokens_per_call_bar",
        title="Tokens per call",
        description="Average request cost per teammate (lower is more efficient).",
        figure=_ensure_dict(build_tokens_per_call_bar(records)),
        meta=_build_meta(records, project_id),
    )


@router.get("/efficiency", response_model=GraphResponse)
async def efficiency_chart(
    project_id: Optional[str] = Query(None),
    _: str = Depends(verify_jwt_or_api_key),
) -> GraphResponse:
    records = await _fetch_usage_documents(project_id)
    return GraphResponse(
        chart_id="efficiency_scatter",
        title="API efficiency",
        description="Relate average tokens per call with calls per token for each teammate.",
        figure=_ensure_dict(build_efficiency_scatter(records)),
        meta=_build_meta(records, project_id),
    )


@router.get("/recent-usage", response_model=GraphResponse)
async def recent_usage_chart(
    project_id: Optional[str] = Query(None),
    _: str = Depends(verify_jwt_or_api_key),
) -> GraphResponse:
    records = await _fetch_usage_documents(project_id)
    return GraphResponse(
        chart_id="recent_usage_timeline",
        title="Recent usage",
        description="Timeline of the latest API activity per teammate.",
        figure=_ensure_dict(build_last_used_timeline(records)),
        meta=_build_meta(records, project_id),
    )


@router.get("/expirations", response_model=GraphResponse)
async def expiration_chart(
    project_id: Optional[str] = Query(None),
    _: str = Depends(verify_jwt_or_api_key),
) -> GraphResponse:
    records = await _fetch_usage_documents(project_id)
    return GraphResponse(
        chart_id="expiration_timeline",
        title="API key expirations",
        description="Number line highlighting upcoming credential expirations.",
        figure=_ensure_dict(build_expiration_timeline(records)),
        meta=_build_meta(records, project_id),
    )


@router.get("/overview", response_model=List[GraphResponse])
async def overview(
    project_id: Optional[str] = Query(None),
    _: str = Depends(verify_jwt_or_api_key),
) -> List[GraphResponse]:
    records = await _fetch_usage_documents(project_id)
    figure_builders = [
        (
            "total_tokens_pie",
            "Total token consumption",
            "Share of total project tokens attributed to each teammate.",
            build_total_tokens_pie,
        ),
        (
            "tokens_per_call_bar",
            "Tokens per call",
            "Average request cost per teammate (lower is more efficient).",
            build_tokens_per_call_bar,
        ),
        (
            "efficiency_scatter",
            "API efficiency",
            "Relate average tokens per call with calls per token for each teammate.",
            build_efficiency_scatter,
        ),
        (
            "recent_usage_timeline",
            "Recent usage",
            "Timeline of the latest API activity per teammate.",
            build_last_used_timeline,
        ),
        (
            "expiration_timeline",
            "API key expirations",
            "Number line highlighting upcoming credential expirations.",
            build_expiration_timeline,
        ),
    ]

    meta_template = _build_meta(records, project_id)
    return [
        GraphResponse(
            chart_id=chart_id,
            title=title,
            description=description,
            figure=_ensure_dict(builder(records)),
            meta=dict(meta_template),
        )
        for chart_id, title, description, builder in figure_builders
    ]


async def _fetch_usage_documents(project_id: Optional[str]) -> List[Dict[str, Any]]:
    database = get_database()
    projection = {
        "_id": 1,
        "email": 1,
        "name": 1,
        "project_id": 1,
        "tokens_per_call": 1,
        "total_tokens": 1,
        "api_calls_per_token": 1,
        "last_used": 1,
        "expiration": 1,
        "usage": 1,
        "metrics": 1,
        "stats": 1,
        "projects": 1,
    }

    cursor = database.users.find({}, projection)
    documents = await cursor.to_list(length=None)

    filtered: List[Dict[str, Any]] = []
    for doc in documents:
        prepared = _flatten_usage_document(doc)
        if _matches_project(prepared, project_id):
            filtered.append(prepared)

    return filtered


def _flatten_usage_document(document: Mapping[str, Any]) -> Dict[str, Any]:
    flattened: Dict[str, Any] = {}
    for key, value in document.items():
        if key == "_id":
            flattened["id"] = str(value)
            continue

        flattened[key] = value
        if key in {"usage", "metrics", "stats"} and isinstance(value, Mapping):
            for inner_key, inner_value in value.items():
                flattened.setdefault(inner_key, inner_value)

    if "project_id" in flattened and flattened["project_id"] is not None:
        flattened["project_id"] = str(flattened["project_id"])

    return flattened


def _matches_project(record: Mapping[str, Any], target: Optional[str]) -> bool:
    if not target:
        return True

    target_str = str(target)
    candidate_keys = (
        "project_id",
        "PROJECT_ID",
        "project",
        "projects",
        "team_id",
    )

    for key in candidate_keys:
        if key not in record:
            continue
        value = record[key]
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            for entry in value:
                if entry is not None and str(entry) == target_str:
                    return True
            continue
        if str(value) == target_str:
            return True

    return False


def _ensure_dict(figure: Any) -> Dict[str, Any]:
    if isinstance(figure, dict):
        return figure
    if hasattr(figure, "to_dict"):
        return figure.to_dict()  # type: ignore[return-value]
    return dict(figure)


def _build_meta(records: List[Dict[str, Any]], project_id: Optional[str]) -> Dict[str, Any]:
    meta: Dict[str, Any] = {"records": len(records)}
    if project_id:
        meta["project_id"] = project_id
    return meta

