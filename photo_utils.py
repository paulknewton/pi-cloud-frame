import logging
import random

from PyQt5 import QtGui
from geopy.geocoders import Nominatim
from geopy.point import Point

logger = logging.getLogger(__name__)


def get_sample(photos, n):
    """
    Select a random sample from a list of photos.

    :param photos: list of photos
    :param n: number of photos to sample
    :return: a random list of samples containing n items (or fewer if there are not enough photos)
    """
    n = min(n, len(photos))
    n = max(n, 0)  # avoid -ve numbers
    return random.sample(photos, n)


def crop_image(image, aspect_ratio):
    """Crop an image to match the desired aspect ratio. This is not used because Pillow cannot handle HEIC libraries."""
    print("Cropping with aspect ratio", aspect_ratio)

    width, height = image.size
    left = 0
    right = width
    new_height = width / aspect_ratio
    top = (height - new_height) / 2
    bottom = top + new_height

    box = (left, top, right, bottom)
    print("box = ", box)
    image = image.crop(box)
    # image.show()

    return image


def get_gps_location(lat_d, lat_m, lat_s, lat_ref, long_d, long_m, long_s, long_ref):
    logger.debug("Checking gps location: %s", locals())
    geolocator = Nominatim(user_agent="pi-cloud-frame")
    location_point = Point(
        "%d %d' %f'' %s, %d %d' %f'' %s" % (lat_d, lat_m, lat_s, lat_ref, long_d, long_m, long_s, long_ref))
    location = geolocator.reverse(location_point)

    return location.address


def is_portrait(image_filename):
    """
    Check if an image is in portrait mode.
    :param image_filename: a QImage image
    :return: True if portrait mode, False if landscape mode or unknown
    """
    image = QtGui.QImage(image_filename)
    # TODO: handle EXIF rotation data in images
    width = image.width()
    height = image.height()
    _is_portrait = height > width
    logger.debug("Width = %d, Height = %d. Portrait mode: %s", width, height, _is_portrait)
    return _is_portrait


def is_landscape(image_filename):
    """
    Check if an image is in landscape mode.
    :param image_filename: a QImage image
    :return: True if landscape mode, False if portrait mode or unknown
    """
    return not is_portrait(image_filename)
