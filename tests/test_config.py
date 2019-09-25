import pytest

from utils.config import Config


@pytest.fixture
def config():
    return Config("tests/test_config.yml")


def test_simple_lookup(config):
    frame_dict = config.get_config_value("frame", config.root)
    assert frame_dict

    assert config.get_config_value("media_folder", frame_dict) == "tests/test_media"

def test_missing_values(config):
    with pytest.raises(KeyError):
        assert config.get_config_value("unknown_value", config.root)

def test_default_value(config):
    frame_dict = config.get_config_value("frame", config.root)

    # this valuse is missing from the config file, but has a default value
    assert config.get_config_value("flip_rotation", frame_dict) == False

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        config = Config("file_does_not_exist")