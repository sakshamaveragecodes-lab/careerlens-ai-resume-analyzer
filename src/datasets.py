"""Validate the curated CSVs before any scoring is possible."""
import csv
from functools import lru_cache
from pathlib import Path

from src.config import DATA_DIR
from src.models import Role, Skill


class DatasetError(ValueError):
    """Dataset installation or consistency error."""


def _parts(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split("|") if part.strip())


def _rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise DatasetError("The role/skill data could not be loaded. Restore the data folder from the project package and restart.") from exc


@lru_cache(maxsize=4)
def load_datasets(directory: Path = DATA_DIR) -> tuple[dict[str, Skill], tuple[Role, ...]]:
    try:
        skills = {}
        for row in _rows(directory / "skill_dictionary.csv"):
            skill = Skill(row["name"], row["category"], _parts(row["aliases"]), _parts(row["prerequisites"]), row["topic"], row["exercise"], row["resource"], int(row["stage"]))
            if skill.name in skills:
                raise ValueError("Duplicate skill")
            skills[skill.name] = skill
        roles = tuple(Role(row["name"], row["category"], row["description"], _parts(row["required"]), _parts(row["preferred"]), row["project"]) for row in _rows(directory / "job_roles.csv"))
        if len(skills) < 30 or len(roles) < 5 or len({r.name for r in roles}) != len(roles):
            raise ValueError("Insufficient or duplicated dataset")
        for role in roles:
            if not role.required or set(role.required) & set(role.preferred):
                raise ValueError("Empty or overlapping requirements")
            if len(set(role.required)) != len(role.required) or len(set(role.preferred)) != len(role.preferred):
                raise ValueError("Duplicate requirements")
            if not set(role.required + role.preferred) <= skills.keys():
                raise ValueError("Unknown skill")
        def visit(name: str, ancestors: frozenset[str]) -> None:
            if name in ancestors or name not in skills:
                raise ValueError("Invalid skill dependency graph")
            for dependency in skills[name].prerequisites:
                visit(dependency, ancestors | {name})
        for name in skills:
            visit(name, frozenset())
        return skills, roles
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, DatasetError):
            raise
        raise DatasetError("The role/skill data is incomplete or inconsistent. Restore the data folder and restart.") from exc
