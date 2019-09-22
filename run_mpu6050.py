from utils import mpu6050

if __name__ == "__main__":

    accelerometer = mpu6050.Mpu6050Compass()
    for i in range(10):
        print(accelerometer.get_rotation(), accelerometer.get_rotation_simple())
