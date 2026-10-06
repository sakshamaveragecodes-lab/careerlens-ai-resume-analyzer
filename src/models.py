"""Small immutable domain objects shared by the pipeline and interface."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple[str, ...]
    prerequisites: tuple[str, ...]
    topic: str
    exercise: str
    resource: str
    stage: int


@dataclass(frozen=True)
class Role:
    name: str
    category: str
    description: str
    required: tuple[str, ...]
    preferred: tuple[str, ...]
    project: str
    custom: bool = False


@dataclass(frozen=True)
class ParsedDocument:
    filename: str
    text: str
    size_bytes: int
    pages: int | None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillEvidence:
    name: str
    category: str
    mentions: int
    sections: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class Match:
    role: Role
    score: float
    required_coverage: float
    preferred_coverage: float
    similarity: float
    required_points: float
    preferred_points: float
    similarity_points: float
    matched: tuple[str, ...]
    missing: tuple[str, ...]
    preferred_matched: tuple[str, ...]
    preferred_missing: tuple[str, ...]


@dataclass(frozen=True)
class RoadmapStep:
    week: int
    skill: str
    purpose: str
    topic: str
    exercise: str
    resource: str = ""


@dataclass(frozen=True)
class Feedback:
    title: str
    detail: str
    kind: str = "suggestion"


@dataclass
class Analysis:
    document: ParsedDocument
    cleaned_text: str
    sections: dict[str, str]
    skills: list[SkillEvidence]
    rankings: list[Match]
    analyzed_at: str
    notices: list[str] = field(default_factory=list)
