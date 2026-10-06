"""Monotone hybrid score over a fixed TF-IDF skill vocabulary.

Only role-relevant, canonical skill tokens enter either vector. For a target
role the resume vector is its intersection with the role's requirements. This
avoids free-text demographic leakage and irrelevant-skill dilution.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models import Match, Role


class JobMatcher:
    def __init__(self, roles: tuple[Role, ...], skill_names: list[str]):
        self.roles = roles
        self.tokens = {name: f"skill_{i:03d}" for i, name in enumerate(sorted(skill_names))}
        self.vectorizer = TfidfVectorizer(vocabulary=list(self.tokens.values()), lowercase=False, binary=True)
        self.vectorizer.fit([self._text(r.required + r.preferred) for r in roles])

    def _text(self, skills) -> str:
        return " ".join(self.tokens[s] for s in sorted(set(skills)) if s in self.tokens)

    def match(self, detected: set[str], role: Role) -> Match:
        matched = tuple(s for s in role.required if s in detected)
        missing = tuple(s for s in role.required if s not in detected)
        preferred_matched = tuple(s for s in role.preferred if s in detected)
        preferred_missing = tuple(s for s in role.preferred if s not in detected)
        required_coverage = len(matched) / len(role.required) if role.required else 0.0
        preferred_coverage = len(preferred_matched) / len(role.preferred) if role.preferred else 0.0
        vectors = self.vectorizer.transform([self._text(matched + preferred_matched), self._text(role.required + role.preferred)])
        similarity = float(cosine_similarity(vectors[0], vectors[1])[0, 0])
        required_weight, preferred_weight = (75, 15) if role.preferred else (90, 0)
        rp = required_weight * required_coverage
        pp = preferred_weight * preferred_coverage
        sp = 10 * similarity
        return Match(role, round(min(100.0, max(0.0, rp + pp + sp)), 1), required_coverage, preferred_coverage, similarity, rp, pp, sp, matched, missing, preferred_matched, preferred_missing)

    def rank(self, detected: set[str]) -> list[Match]:
        return sorted((self.match(detected, role) for role in self.roles), key=lambda m: (-m.score, -m.required_coverage, m.role.name))
