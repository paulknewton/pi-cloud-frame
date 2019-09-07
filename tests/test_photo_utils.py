import pytest

import photo_utils as pu


def test_sample():
    """
    Test sample function - simple
    """
    photos = [0] * 10
    assert len(pu.get_sample(photos, 3)) == 3


def test_sample_small_data():
    """
    Test sample where requested number exceeds size of data set
    """
    photos = [0] * 2
    assert len(pu.get_sample(photos, 3)) == 2


def test_sample_no_data():
    """
    Test sample where no data
    """
    photos = []
    assert not pu.get_sample(photos, 3)


def test_sample_negative():
    """
    Test sample where requested sample size is -ve
    """
    photos = [0] * 5
    assert not pu.get_sample(photos, -3)


def test_exif_rotation():
    expected = {
        6: 90,
        8: 270,
        1: 0
    }

    for exif in expected:
        assert pu.get_exif_rotation_angle(exif) == expected[exif]


def test_is_portrait_or_landscape():
    # test data with different exif rotation values: all portrait
    portrait_values = [
        (1, 10, 20),
        (3, 10, 20),
        (6, 20, 10),
        (8, 20, 10)
    ]

    # test data with different exif rotation values: all landscape
    landscape_values = [
        (1, 20, 10),
        (3, 20, 10),
        (6, 10, 20),
        (8, 10, 20)
    ]

    for exif, width, height in portrait_values:
        assert pu.is_portrait(width, height, exif)
        assert not pu.is_landscape(width, height, exif)

    for exif, width, height in landscape_values:
        assert pu.is_landscape(width, height, exif)
        assert not pu.is_portrait(width, height, exif)

    # test using default exif rotation (1)
    assert pu.is_landscape(20, 10)
    assert not pu.is_landscape(10, 20)
    assert pu.is_portrait(10, 20)
    assert not pu.is_portrait(20, 10)


def test_invalid_exif_rotation():
    invalid_exif_values = [0, 2, 4, 5, 7]
    for i in invalid_exif_values:
        with pytest.raises(KeyError):
            assert pu.get_exif_rotation_angle(i)


def test_no_exif_orientation():
    portrait_file = "portrait_no_exif.jpg"

    assert pu.get_file_exif_orientation(portrait_file) is None


def test_exif_orientation():
    # TODO unit test for EXIF orientation
    pass
