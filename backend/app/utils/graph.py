"""High-level helpers to turn usage metrics into polished Plotly figures."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Iterable, List, Mapping, Optional, Sequence

import plotly.graph_objects as go
from plotly.colors import qualitative


COLOR_SEQUENCE: Sequence[str] = qualitative.Prism


@dataclass
class UserUsage:
    """Normalized representation of usage metrics for a single teammate."""

    id: str
    email: str
    name: str
    project_id: Optional[str]
    tokens_per_call: float
    total_tokens: float
    api_calls_per_token: float
    last_used: Optional[datetime]
    expiration: Optional[date]


def normalize_usage_records(records: Iterable[Mapping[str, Any]]) -> List[UserUsage]:
    """Convert raw database rows/documents into :class:`UserUsage` objects."""

    normalized: List[UserUsage] = []

    for raw in records:
        if raw is None:
            continue

        record = dict(raw)
        lower_map = {
            str(key).lower(): value
            for key, value in record.items()
            if isinstance(key, str)
        }

        def pick(*names: str, default: Any = None) -> Any:
            for name in names:
                if not isinstance(name, str):
                    continue
                candidates = {name, name.lower(), name.upper()}
                for candidate in candidates:
                    if candidate in record:
                        value = record[candidate]
                        if value not in (None, ""):
                            return value
                lowered = name.lower()
                if lowered in lower_map:
                    value = lower_map[lowered]
                    if value not in (None, ""):
                        return value
            return default

        user_id = _to_str(pick("id", "user_id", "uid", "record_id"))
        email = _to_str(pick("email", "user_email"))
        name = _to_str(pick("name", "full_name", "display_name"))
        if not name:
            name = email.split("@")[0] if email else "Unknown"

        project_id = _to_optional_str(pick("project_id", "project", "team_id"))

        usage = UserUsage(
            id=user_id or "",
            email=email or "unknown@example.com",
            name=name,
            project_id=project_id,
            tokens_per_call=_to_number(pick("tokens_per_call", "tokensPerCall")),
            total_tokens=_to_number(pick("total_tokens", "tokens_total", "token_total")),
            api_calls_per_token=_to_number(pick("api_calls_per_token", "apiCallsPerToken")),
            last_used=_to_datetime(pick("last_used", "lastUsed", "last_activity")),
            expiration=_to_date(pick("expiration", "expires_at", "expiry")),
        )
        normalized.append(usage)

    return normalized


def build_total_tokens_pie(records: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Highlight each teammate's share of the overall token consumption."""

    users = sorted(
        (u for u in normalize_usage_records(records) if u.total_tokens > 0),
        key=lambda item: item.total_tokens,
        reverse=True,
    )

    if not users:
        return _build_empty_figure(
            "Total token consumption",
            "Once teammates start using tokens, their share will appear here.",
        )

    labels = [u.name for u in users]
    values = [u.total_tokens for u in users]
    colors = _repeat_palette(len(users))
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.35,
                sort=False,
                marker=dict(colors=colors, line=dict(color="#ffffff", width=1.5)),
                pull=[0.08 if idx == 0 else 0 for idx in range(len(users))],
                hovertemplate="<b>%{label}</b><br>Total tokens: %{value:,.0f}<br>%{percent}<extra></extra>",
                textinfo="label+percent",
                insidetextorientation="radial",
            )
        ]
    )

    _apply_layout(
        fig,
        "Total token consumption",
        "Proportional usage across teammates",
    )
    fig.update_layout(legend=dict(orientation="v", yanchor="top", y=0.95, x=1.05))

    return fig.to_dict()


def build_tokens_per_call_bar(records: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Visualize how costly each teammate's average API call is."""

    users = sorted(
        normalize_usage_records(records),
        key=lambda item: item.tokens_per_call,
        reverse=True,
    )

    if not any(u.tokens_per_call for u in users):
        return _build_empty_figure(
            "Tokens per call",
            "No call data yet. Run a few API calls to populate this chart.",
        )

    x_values = [u.tokens_per_call for u in users]
    y_values = [u.name for u in users]
    colors = _repeat_palette(len(users))

    fig = go.Figure(
        data=[
            go.Bar(
                x=x_values,
                y=y_values,
                orientation="h",
                text=[f"{value:,.0f}" for value in x_values],
                marker=dict(color=colors, line=dict(color="#e2e8f0", width=1)),
                hovertemplate="<b>%{y}</b><br>Tokens per call: %{x:,.2f}<extra></extra>",
            )
        ]
    )

    _apply_layout(fig, "Tokens per call", "Average request cost by teammate")
    fig.update_layout(
        xaxis_title="Tokens per request",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
    )

    return fig.to_dict()


def build_efficiency_scatter(records: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Plot API efficiency: tokens per call vs. calls per token."""

    users = [
        user
        for user in normalize_usage_records(records)
        if user.tokens_per_call > 0 and user.api_calls_per_token > 0
    ]

    if not users:
        return _build_empty_figure(
            "API efficiency",
            "We need both token and call metrics to plot efficiency.",
        )

    colors = _repeat_palette(len(users))
    sizes = _bubble_sizes([u.total_tokens for u in users])
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[u.tokens_per_call for u in users],
                y=[u.api_calls_per_token for u in users],
                mode="markers+text",
                text=[u.name for u in users],
                textposition="top center",
                marker=dict(size=sizes, color=colors, opacity=0.85, line=dict(color="#0f172a", width=1)),
                customdata=[[u.total_tokens] for u in users],
                hovertemplate=(
                    "<b>%{text}</b><br>Tokens per call: %{x:,.2f}"
                    "<br>API calls per token: %{y:,.2f}"
                    "<br>Total tokens: %{customdata[0]:,.0f}<extra></extra>"
                ),
            )
        ]
    )

    _apply_layout(
        fig,
        "API efficiency",
        "Lower left is thrifty - upper right means heavy usage",
    )
    fig.update_layout(
        xaxis_title="Tokens per call",
        yaxis_title="API calls per token",
    )

    return fig.to_dict()


def build_last_used_timeline(records: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Show the recency of each teammate's activity on a timeline."""

    entries = sorted(
        [u for u in normalize_usage_records(records) if u.last_used],
        key=lambda item: item.last_used,
    )

    if not entries:
        return _build_empty_figure(
            "Recent usage",
            "As soon as someone makes a call, we will plot it on the timeline.",
        )

    def _ensure_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    now_marker = datetime.now(timezone.utc)
    x_values = [_ensure_utc(u.last_used) for u in entries]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x_values,
                y=[u.name for u in entries],
                mode="markers",
                marker=dict(
                    size=16,
                    color=_repeat_palette(len(entries)),
                    line=dict(color="#0f172a", width=1),
                    symbol="diamond",
                ),
                hovertemplate="<b>%{y}</b><br>Last used: %{x|%b %d, %Y %H:%M UTC}<extra></extra>",
            )
        ]
    )

    fig.add_vline(
        x=now_marker,
        line=dict(color="#6366f1", dash="dash", width=2),
    )
    fig.add_annotation(
        x=now_marker,
        xref="x",
        y=1,
        yref="paper",
        text="Now",
        showarrow=False,
        align="center",
        yanchor="bottom",
        font=dict(color="#6366f1"),
    )

    _apply_layout(
        fig,
        "Recent usage",
        "Latest API interactions by teammate",
    )

    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="",
        yaxis=dict(type="category"),
    )

    fig.update_xaxes(rangeslider_visible=False, showgrid=True, gridcolor="#e2e8f0")

    return fig.to_dict()


def build_expiration_timeline(records: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Display API key expiration dates along a single number line."""

    entries = sorted(
        [u for u in normalize_usage_records(records) if u.expiration],
        key=lambda item: item.expiration,
    )

    if not entries:
        return _build_empty_figure(
            "API key expirations",
            "No expiration dates recorded. Configure rotations to populate this.",
        )

    xs = [datetime.combine(u.expiration, datetime.min.time()) for u in entries]
    colors = _repeat_palette(len(entries))

    fig = go.Figure(
        data=[
            go.Scatter(
                x=xs,
                y=[0] * len(entries),
                mode="markers+text",
                text=[u.name for u in entries],
                textposition="top center",
                marker=dict(size=18, color=colors, line=dict(color="#1e293b", width=1)),
                hovertemplate="<b>%{text}</b><br>Expires: %{x|%b %d, %Y}<extra></extra>",
            )
        ]
    )

    if xs:
        start = min(xs)
        end = max(xs)
        fig.add_shape(
            type="line",
            x0=start,
            y0=0,
            x1=end,
            y1=0,
            line=dict(color="#94a3b8", width=2),
        )

    _apply_layout(
        fig,
        "API key expirations",
        "Even spacing highlights which keys are nearing rotation",
    )

    fig.update_layout(
        xaxis_title="Expiration date",
        yaxis=dict(visible=False, showticklabels=False),
    )

    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")

    return fig.to_dict()


def _apply_layout(fig: go.Figure, title: str, subtitle: Optional[str] = None) -> None:
    """Apply a consistent styling across charts."""

    if subtitle:
        title_text = (
            f"{title}<br><span style='font-size:0.8em;color:#64748b;'>{subtitle}</span>"
        )
    else:
        title_text = title

    fig.update_layout(
        template="plotly_white",
        title=dict(text=title_text, x=0.02, xanchor="left"),
        margin=dict(l=70, r=40, t=95, b=60),
        font=dict(family="Inter, 'Segoe UI', Tahoma, sans-serif", color="#0f172a"),
        hoverlabel=dict(bgcolor="#0f172a", font=dict(color="#f8fafc"), bordercolor="#1f2937"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        colorway=_repeat_palette(12),
    )


def _build_empty_figure(title: str, message: str) -> Mapping[str, Any]:
    fig = go.Figure()
    _apply_layout(fig, title, message)
    fig.add_annotation(
        text=message,
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        font=dict(size=14, color="#64748b"),
        align="center",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig.to_dict()


def _repeat_palette(length: int) -> List[str]:
    palette = list(COLOR_SEQUENCE) if COLOR_SEQUENCE else ["#2563eb"]
    if length <= 0:
        return palette
    return [palette[idx % len(palette)] for idx in range(max(1, length))]


def _bubble_sizes(values: Sequence[float]) -> List[float]:
    base = 18
    scaled: List[float] = []
    for value in values:
        if value is None or value <= 0:
            scaled.append(base)
            continue
        scaled.append(min(60, base + (value ** 0.5)))
    return scaled


def _to_number(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return default


def _to_datetime(value: Any) -> Optional[datetime]:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        cleaned = cleaned.replace("Z", "+00:00")
        date_formats = (None, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
        for fmt in date_formats:
            try:
                return (
                    datetime.fromisoformat(cleaned)
                    if fmt is None
                    else datetime.strptime(cleaned, fmt)
                )
            except ValueError:
                continue
    return None


def _to_date(value: Any) -> Optional[date]:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return date.fromisoformat(cleaned)
        except ValueError:
            dt_value = _to_datetime(cleaned)
            if dt_value:
                return dt_value.date()
    return None


def _to_str(value: Any) -> str:
    if value in (None, ""):
        return ""
    return str(value)


def _to_optional_str(value: Any) -> Optional[str]:
    text = _to_str(value)
    return text or None


__all__ = [
    "UserUsage",
    "normalize_usage_records",
    "build_total_tokens_pie",
    "build_tokens_per_call_bar",
    "build_efficiency_scatter",
    "build_last_used_timeline",
    "build_expiration_timeline",
]

