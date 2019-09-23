import yaml
import logging
import sys

logger = logging.getLogger(__name__)


class Config:
    default = {
        "frame": None,              # section containing generic frame parameters
        "slideshow_delay": 5000,    # time between photos (ms)
        "media_folder": "tmp",      # location of photos under the 'media' folder
        "font": "12",               # font size for popup menu
        "compass": None,            # if automation detection of frame rotation is support (mpu6050 | fixed)
        "rotation": 0,              # if 'fixed' compass is used, what is the angle of the frame
        "flip_rotation": False,     # rotation values are inverted to handle upside down accelerometer
        "players": None             # section containing configuration of media players
    }

    def __init__(self, filename):
        self.root = None

        try:
            with open(filename, 'r') as ymlfile:
                self.root = yaml.load(ymlfile, Loader=yaml.FullLoader)
        except FileNotFoundError:
            logger.error("Could not load config file %s. Exiting.", filename)
            sys.exit(1)
        # data = yaml.dump(config, Dumper=yaml.CDumper)
        # print(data)

    def get_config_value(self, key, dict):
        return Config._get_config_value(key, dict, Config.default[key])

    @staticmethod
    def _get_config_value(key, dict, default):
        logger.debug("Reading %s (default %s)", key, default)

        try:
            value = dict[key]
        except KeyError:
            logger.debug("Using default for config value %s = %s", key, default)
            return default

        logger.debug("Config value %s = %s", key, value)
        return value
