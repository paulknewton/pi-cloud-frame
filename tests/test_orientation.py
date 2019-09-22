from utils import mpu6050, orientation


def test_portrait_check():
    """
    Test portrait mode check
    """
    compass = orientation.Compass()

    portrait_angles = [90, 270, -90]
    landscape_angles = [0, 180, -180, 360]

    for angle in portrait_angles:
        compass._compass_angle = angle
        assert compass.is_portrait_frame()
        assert not compass.is_landscape_frame()

    for angle in landscape_angles:
        compass._compass_angle = angle
        assert compass.is_landscape_frame()
        assert not compass.is_portrait_frame()


def test_compass_rounded():
    """
    Test rotation rounding logic
    """
    compass = orientation.Compass()

    compass._compass_angle = 10
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 40
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 44
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 45
    assert compass.get_rotation_simple() == 90

    compass._compass_angle = 46
    assert compass.get_rotation_simple() == 90

    compass._compass_angle = 89
    assert compass.get_rotation_simple() == 90

    compass._compass_angle = 90
    assert compass.get_rotation_simple() == 90

    compass._compass_angle = 91
    assert compass.get_rotation_simple() == 90

    compass._compass_angle = 134
    assert compass.get_rotation_simple() == 90

    compass._compass_angle = 135
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = 136
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = 179
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = 180
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = 181
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = 224
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = 225
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = 226
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = 269
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = 270
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = 271
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = 314
    assert compass.get_rotation_simple() == 270

    # all angles are modulo 360
    compass._compass_angle = 315
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 316
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 359
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 360
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 361
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = 0
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = -1
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = -44
    assert compass.get_rotation_simple() == 0

    compass._compass_angle = -45
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = -46
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = -89
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = -90
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = -91
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = -134
    assert compass.get_rotation_simple() == 270

    compass._compass_angle = -135
    assert compass.get_rotation_simple() == 180

    compass._compass_angle = -136
    assert compass.get_rotation_simple() == 180
