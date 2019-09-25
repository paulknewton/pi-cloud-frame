from utils import orientation


def test_portrait_check():
    """
    Test portrait mode check
    """
    portrait_angles = [90, 270, -90]
    landscape_angles = [0, 180, -180, 360]

    for angle in portrait_angles:
        compass = orientation.Compass()
        compass.set_angle(angle)
        assert compass.is_portrait_frame()
        assert not compass.is_landscape_frame()

    for angle in landscape_angles:
        compass = orientation.Compass()
        compass.set_angle(angle)
        assert compass.is_landscape_frame()
        assert not compass.is_portrait_frame()


def test_compass_rounded():
    """
    Test rotation rounding logic
    """
    expected = {
        10: 0,
        40: 0,
        44: 0,
        45: 90,
        46: 90,
        89: 90,
        90: 90,
        91: 90,
        134: 90,
        135: 180,
        136: 180,
        179: 180,
        180: 180,
        181: 180,
        224: 180,
        225: 270,
        226: 270,
        269: 270,
        270: 270,
        271: 270,
        314: 270,
        315: 0,  # all angles are modulo 360
        316: 0,
        359: 0,
        360: 0,
        361: 0,
        0: 0,
        -1: 0,
        -44: 0,
        -45: 270,
        -46: 270,
        -89: 270,
        -90: 270,
        -91: 270,
        -134: 270,
        -135: 180,
        -136: 180
    }

    for angle, rounded in expected.items():
        compass = orientation.Compass()
        compass.set_angle(angle)
        assert compass.get_rotation_simple() == rounded


def test_flip():
    compass = orientation.Compass()
    compass.set_angle(-90)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(True)
    compass.set_angle(-90)
    assert compass.get_rotation_simple() == 90
