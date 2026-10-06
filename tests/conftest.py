import pytest

from src.datasets import load_datasets
from src.job_matcher import JobMatcher


@pytest.fixture(scope="session")
def dictionary():
    return load_datasets()[0]


@pytest.fixture(scope="session")
def roles():
    return load_datasets()[1]


@pytest.fixture(scope="session")
def matcher(dictionary, roles):
    return JobMatcher(roles, list(dictionary))
