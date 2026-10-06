"""Charts communicate measured quantities on labelled, comparable scales."""
from collections import Counter

import plotly.graph_objects as go

from src.models import Match, SkillEvidence

TEAL = "#087F70"
NAVY = "#173A43"


def _style(fig, height=360):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=5, r=25, t=15, b=15), font=dict(family="Arial, sans-serif", size=12, color=NAVY), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    return fig


def ranking_chart(rankings: list[Match], target_name: str):
    ordered = list(reversed(rankings))
    fig = go.Figure(go.Bar(x=[m.score for m in ordered], y=[m.role.name for m in ordered], orientation="h", marker_color=[TEAL if m.role.name == target_name else "#CBDDD7" for m in ordered], text=[f"{m.score:.1f}%" for m in ordered], textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>Documented skill alignment: %{x:.1f}%<extra></extra>"))
    fig.update_xaxes(range=[0, 110], tickvals=[0, 25, 50, 75, 100], ticksuffix="%", title="Documented skill alignment")
    fig.update_yaxes(automargin=True)
    return _style(fig, 460)


def coverage_chart(match: Match):
    fig = go.Figure(go.Pie(labels=["Core detected", "Core not detected"], values=[len(match.matched), len(match.missing)], hole=.73, marker_colors=[TEAL, "#E5ECE8"], sort=False, textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>"))
    fig.update_layout(annotations=[dict(text=f"{len(match.matched)}/{len(match.role.required)}", x=.5, y=.5, font_size=30, showarrow=False)])
    return _style(fig, 210)


def category_chart(skills: list[SkillEvidence]):
    counts = Counter(s.category for s in skills)
    ordered = sorted(counts, key=counts.get)
    fig = go.Figure(go.Bar(x=[counts[c] for c in ordered], y=ordered, orientation="h", marker_color=TEAL, text=[counts[c] for c in ordered], textposition="outside", hovertemplate="%{y}: %{x} skills<extra></extra>"))
    fig.update_xaxes(title="Unique skills detected", dtick=1, rangemode="tozero")
    return _style(fig, max(250, len(ordered) * 34 + 70))
