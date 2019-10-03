import logging

import yaml

logger = logging.getLogger(__name__)


class Config:
    default = {
        "frame": None,  # section containing generic frame parameters
        "slideshow_delay": 5000,  # time between photos (ms)
        "root_folder": "tmp",  # location of photos under the 'media' folder
        "font": "12",  # font size for popup menu
        "compass": None,  # if automation detection of frame rotation is support (mpu6050 | fixed)
        "rotation": 0,  # if 'fixed' compass is used, what is the angle of the frame
        "flip_rotation": False,  # rotation values are inverted to handle upside down accelerometer
        "shuffle": False,  # shuffle slideshow
        "players": None  # section containing configuration of media players
    }

    def __init__(self, filename):
        self.root = None

        try:
            with open(filename, 'r') as ymlfile:
                self.root = yaml.load(ymlfile, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            logger.error("Could not load config file %s", filename)
            raise e
        # data = yaml.dump(config, Dumper=yaml.CDumper)
        # print(data)

    @staticmethod
    def get_config_value(key, config_dict):
        # get a default value (if any)
        default_value = Config.default.get(key, None)

        logger.debug("Reading %s (default %s)", key, default_value)
        value = config_dict.get(key, default_value)
        logger.debug("Config value %s = %s", key, value)
        return value


    @staticmethod
    def _get_config_value(key, config_dict, default):
        try:
            value = config_dict[key]
        except KeyError:
            logger.debug("Using default for config value %s = %s", key, default)
            return default

        return value
