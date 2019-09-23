import yaml
import logging
import sys

logger = logging.getLogger(__name__)


class Config:
    default = {
        "frame": None,
        "slideshow_delay": 5000,
        "media_folder": "tmp",
        "font": "12",
        "frame_rotation": None,
        "players": None
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
