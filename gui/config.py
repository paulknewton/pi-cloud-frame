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
        "frame_rotation": False,
        "players": None
    }

    def __init__(self, filename):
        self.config = None

        try:
            with open(filename, 'r') as ymlfile:
                self.config = yaml.load(ymlfile, Loader=yaml.FullLoader)
        except FileNotFoundError:
            logger.error("Could not load config file %s. Exiting.", filename)
            sys.exit(1)
        # data = yaml.dump(config, Dumper=yaml.CDumper)
        # print(data)

    def get_config_value(self, key, dict=None):
        if dict:
            return Config._get_config_value(dict, key, Config.default[key])
            config_to_read = dict

        return Config._get_config_value(self.config, key, Config.default[key])

    @staticmethod
    def _get_config_value(config, key, default):
        logger.debug("Reading %s (default %s)", key, default)
        if not (config and key):
            logger.debug("Using default for config value %s = %s", key, default)
            return default

        try:
            value = config[key]
        except KeyError:
            logger.debug("Using default for config value %s = %s", key, default)
            return default
        logger.debug("Config value %s = %s", key, value)
        return value
