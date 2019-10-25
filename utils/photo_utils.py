import logging
import random

import exifread
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim
from geopy.point import Point

logger = logging.getLogger(__name__)


def get_sample(photos, n):
    """
    Select a random sample from a list of network.

    :param photos: list of network
    :param n: number of network to sample
    :return: a random list of samples containing n items (or fewer if there are not enough network)
    """
    n = min(n, len(photos))
    n = max(n, 0)  # avoid -ve numbers
    return random.sample(photos, n)


def get_gps_dms_location(lat_d, lat_m, lat_s, lat_ref, long_d, long_m, long_s, long_ref):
    """
    Lookup address for a set of GPD co-ordinates in DMS form
    :param lat_d: latitude (degrees)
    :param lat_m: latitude (minutes)
    :param lat_s: latitude (seconds)
    :param lat_ref: latitude reference (N/S)
    :param long_d: longitude (degrees)
    :param long_m: longitude (minutes)
    :param long_s: longitude (seconds)
    :param long_ref: longitude reference (E/W)
    :return: address as a string or "" if not found/lookup error
    """
    logger.debug("Checking gps location: %s", locals())
    geolocator = Nominatim(user_agent="pi-cloud-frame")
    location_point = Point(
        "%d %d' %f'' %s, %d %d' %f'' %s" % (lat_d, lat_m, lat_s, lat_ref, long_d, long_m, long_s, long_ref))

    try:
        return geolocator.reverse(location_point).address
    except GeocoderServiceError as e:
        logger.error("Error downloading map from Google Maps API - %s", e)
        return ""


def gps_dms_to_dd(lat_d, lat_m, lat_s, lat_ref, long_d, long_m, long_s, long_ref):
    """
    Lookup address for a set of GPD co-ordinates in DMS form
    :param lat_d: latitude (degrees)
    :param lat_m: latitude (minutes)
    :param lat_s: latitude (seconds)
    :param lat_ref: latitude reference (N/S)
    :param long_d: longitude (degrees)
    :param long_m: longitude (minutes)
    :param long_s: longitude (seconds)
    :param long_ref: longitude reference (E/W)
    :return: latitude, longitude, altitude
    """
    location_point = Point(
        "%d %d' %f'' %s, %d %d' %f'' %s" % (lat_d, lat_m, lat_s, lat_ref, long_d, long_m, long_s, long_ref))

    return location_point.latitude, location_point.longitude, location_point.altitude


def get_file_exif_orientation(image_filename):
    """
    Get the EXIF orientation from a photo file
    :param image_filename: the location of the image
    :return: the value corresponding to the EXIF orientation tag (None if missing)
    """
    with open(image_filename, 'rb') as f:
        exif_tags = exifread.process_file(f, details=False)
        logger.debug("EXIF data: %s", list(exif_tags.keys()))

        try:
            # TODO: use correct EXIF tag to determine orientation
            return exif_tags["EXIF Orientation"]
        except KeyError:
            return None


def get_exif_rotation_angle(exif_orientation):
    """
    Check if EXIF rotiation angle signifies portrait or lansdscape.
    :param exif_orientation: numeric EXIF rotation value
    :return: angle of rotation (0-270)
    :except KeyError: if invalid exif_orientation
    """
    rotation_values = {
        1: 0,
        6: 90,
        3: 180,
        8: 270
    }
    return rotation_values[exif_orientation]


def is_portrait(width, height, exif_orientation=1):
    """
    Check if an image is in portrait mode, taking into account the EXIF rotation setting.
    :param width: the width of the image
    :param height: the height of the image
    :param exif_orientation: the rotation flag
    :return: True if portrait mode, False if landscape mode or unknown
    :except KeyError: if invalid exif_orientation
    """
    logger.debug("EXIF orientation = %s; width = %d; height = %d", exif_orientation, width, height)

    # swap width/height based on EXIF rotation tags
    angle = get_exif_rotation_angle(exif_orientation)
    logger.debug("angle=%s", angle)

    exif_width, exif_height = width, height

    # rotate dimensions based on EXIF data
    if angle not in (0, 180):  # camera was rotated
        exif_width, exif_height = exif_height, exif_width

    # is photo portrait or landscape?
    return exif_width <= exif_height


def is_landscape(width, height, exif_orientation=1):
    """
    Check if an image is in landscape mode, taking into account the EXIF rotation setting.
    :param width: the width of the image
    :param height: the height of the image
    :param exif_orientation: the rotation flag
    :return: True if landscape mode, False if portrait mode or unknown
    :except KeyError: if invalid exif_orientation
    """
    return not is_portrait(width, height, exif_orientation)
