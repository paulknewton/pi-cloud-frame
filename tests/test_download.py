import pytest
import icloud_photos as ip


@pytest.fixture
def setup():
    return "hello"


def test_sample():
    photos = [0] * 10
    assert len(ip.get_sample(photos, 3)) == 3


def test_sample_small_data():
    photos = [0] * 2
    assert len(ip.get_sample(photos, 3)) == 2


def test_sample_no_data():
    photos = []
    assert len(ip.get_sample(photos, 3)) == 0

