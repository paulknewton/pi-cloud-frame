from utils import orientation


def test_portrait_check():
    """
    Test portrait mode check
    """
    portrait_angles = [90, 270, -90]
    landscape_angles = [0, 180, -180, 360]

    for angle in portrait_angles:
        compass = orientation.Compass(angle)
        assert compass.is_portrait_frame()
        assert not compass.is_landscape_frame()

    for angle in landscape_angles:
        compass = orientation.Compass(angle)
        assert compass.is_landscape_frame()
        assert not compass.is_portrait_frame()


def test_compass_rounded():
    """
    Test rotation rounding logic
    """
    compass = orientation.Compass(10)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(40)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(44)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(45)
    assert compass.get_rotation_simple() == 90

    compass = orientation.Compass(46)
    assert compass.get_rotation_simple() == 90

    compass = orientation.Compass(89)
    assert compass.get_rotation_simple() == 90

    compass = orientation.Compass(90)
    assert compass.get_rotation_simple() == 90

    compass = orientation.Compass(91)
    assert compass.get_rotation_simple() == 90

    compass = orientation.Compass(134)
    assert compass.get_rotation_simple() == 90

    compass = orientation.Compass(135)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(136)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(179)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(180)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(181)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(224)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(225)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(226)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(269)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(270)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(271)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(314)
    assert compass.get_rotation_simple() == 270

    # all angles are modulo 360
    compass = orientation.Compass(315)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(316)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(359)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(360)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(361)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(0)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(-1)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(-44)
    assert compass.get_rotation_simple() == 0

    compass = orientation.Compass(-45)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(-46)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(-89)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(-90)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(-91)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(-134)
    assert compass.get_rotation_simple() == 270

    compass = orientation.Compass(-135)
    assert compass.get_rotation_simple() == 180

    compass = orientation.Compass(-136)
    assert compass.get_rotation_simple() == 180
