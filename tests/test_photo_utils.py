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
