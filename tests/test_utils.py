import pytest

from src.detector import estimate_proximity, get_spatial_position
from src.navigation import extract_destination, haversine


@pytest.mark.parametrize(
    "x,expected", [(100, "à gauche"), (320, "devant"), (600, "à droite")]
)
def test_spatial_position(x, expected):
    assert get_spatial_position(x, 640) == expected


def test_proximity():
    assert estimate_proximity(0.5) == "très proche"
    assert estimate_proximity(0.1) == "proche"
    assert estimate_proximity(0.01) == "loin"


def test_haversine_zero():
    assert haversine(33.97, -6.87, 33.97, -6.87) == pytest.approx(0, abs=1e-6)


def test_haversine_known_distance():
    assert haversine(0, 0, 1, 0) == pytest.approx(111_195, rel=0.01)


def test_extract_destination():
    assert extract_destination("bghit nmchi l ensias") == "ensias"
    assert extract_destination("emmène moi à marjane hay riad") == "marjane hay riad"
    assert extract_destination("n'importe quoi") is None
