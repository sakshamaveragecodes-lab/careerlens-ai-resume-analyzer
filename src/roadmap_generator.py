"""Topologically ordered learning steps derived from actual documented gaps."""
from src.models import Match, RoadmapStep, Skill


def generate_roadmap(match: Match, detected: set[str], skills: dict[str, Skill], include_preferred: bool = False) -> list[RoadmapStep]:
    targets = list(match.missing)
    if include_preferred:
        targets.extend(match.preferred_missing)
    ordered: list[str] = []
    visited = set(detected)

    def add(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        for prerequisite in skills[name].prerequisites:
            add(prerequisite)
        ordered.append(name)

    for target in sorted(targets, key=lambda name: (skills[name].stage, targets.index(name))):
        add(target)
    steps = []
    for week, name in enumerate(ordered, 1):
        skill = skills[name]
        purpose = "Core requirement" if name in match.missing else "Preferred requirement" if name in match.preferred_missing else "Foundation for a later topic"
        steps.append(RoadmapStep(week, name, purpose, skill.topic, skill.exercise, skill.resource))
    steps.append(RoadmapStep(len(steps) + 1, "Applied project", "Put the target role into practice", f"Build a portfolio artifact for {match.role.name}.", match.role.project))
    return steps
