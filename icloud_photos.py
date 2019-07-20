import argparse
from pyicloud import PyiCloudService
import logging
import random
import os
#from PIL import Image
import sys

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def connect(user, password):
    """
    Connect to the icloud

    @:param user: the icloud user id
    @:param password: the icloud password
    """
    api = PyiCloudService(user, password)

    if api.requires_2sa:
        import click
        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print("  %s: %s" % (i, device.get('deviceName',
                                              "SMS to %s" % device.get('phoneNumber'))))

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)

    return api


def is_image(photo):
    """
    Check if the photo is an image (excludes videos)

    @:param photo: the photo
    @:return: True if the photo is an image, otherwise False
    """
    logger.debug(photo.filename)

    #root, ext = os.path.splitext(photo.filename)
    #format = ext.upper()
    format = photo._master_record["fields"]["itemType"]["value"]

    if (format not in ["public.jpeg", "public.png", "public.heic", "public.tiff"]):
        logger.debug("[Invalid format %s - skip]" % format)
        return False

    logger.debug("[OK]")
    return True
    return photo._asset_record["imageType"] == "image"


def is_correct_format(photo, orientation):
    """
    Check if the photo is the correct orientation.

    :param photo: the photo
    :param orientation: portrait or landscape
    :return: True if the photo orientation matches the specified orientation
    """
    logger.debug(photo.filename)

    photo_orientation = photo._asset_record["fields"]["orientation"]["value"]
    width, height = photo.dimensions

    # rotate dimensions if needed
    if photo_orientation == 6 or photo_orientation == 8:
        width = photo.dimensions[1]
        height = photo.dimensions[0]

    if (orientation == "landscape" and width <= height) or (orientation == "portrait" and width >= height):
        logger.debug("[Invalid orientation - skip]")
        return False

    logger.debug("[OK]")
    return True


def get_all_photos(api, album, orientation):
    """
    Retrieve all photos from the specified icloud album. Only photos that are images and match the requested orientation are returned.

    @:param album: the icloud album to search
    @:param orientation: the orientation of the photos (portrait or landscape)
    @:return: a list of matching photos
    """
    eligible_photos = []
    #asset_types = set()
    i = 1
    for photo in api.photos.albums[album]:
        print("%d - Checking %s" % (i, photo.filename))
        i += 1
        #asset_types.add(photo._master_record["fields"]["itemType"]["value"])
        if (is_image(photo) and is_correct_format(photo, orientation)):
            eligible_photos.append(photo)

    #print(asset_types)
    return eligible_photos


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
    image.show()


def download(photos, folder):
    """
    Download the specific photos from the icloud and store them locally

    :param photos: list of photos to download
    :param folder: the folder to store the photos locally
    """
    for photo in photos:
        with open(os.path.join(folder, photo.filename), 'wb') as opened_file:
            print("[%s %s %s]" % (
                photo.filename, photo.dimensions, photo._asset_record["fields"]["orientation"]["value"]))
            data = photo.download().raw.read()

            # cannot crop HEIC images with Pillow
            # crop_image(Image.open(io.BytesIO(data)), float(16 / 9))

            opened_file.write(data)


def get_sample(photos, n):
    """
    Select a random sample from a list of photos.

    :param photos: list of photos
    :param n: number of photos to sample
    :return: a random list of samples containing n items (or fewer if there are not enough photos)
    """
    n = min(n, len(photos))
    return random.sample(photos, n)


if __name__ == '__main__':

    # read command-line args
    parser = argparse.ArgumentParser(
        description="icloud photo frame")
    parser.add_argument("user", help="icloud user")
    parser.add_argument("password", help="password")
    parser.add_argument("--output", help="folder to store downloaded photos", default="raw")
    parser.add_argument("--sample", help="number of photos to download", type=int, default=5)
    parser.add_argument("--album", help="icloud album to find photos", default="All Photos")
    parser.add_argument("--orientation", help="orientation of photos", choices=["portrait", "landscape"],
                        default="landscape")
    parser.add_argument("--list", help="list albums (no photo downloading)", action='store_true', default=False)
    args = parser.parse_args()
    print(args)

    api = connect(args.user, args.password)

    if args.list:
        print("Albums:")
        for album in api.photos.albums:
            print(album)
        sys.exit(1)

    # get all photos in the photoframe album
    print("Downloading photo list...")
    photos = get_all_photos(api, args.album, args.orientation)

    # get a random sample to download
    print("Selecting random sample (%d from %d)" % (args.sample, len(photos)))
    photos = get_sample(photos, args.sample)

    print("Downloading photos to %s..." % args.output)
    download(photos, args.output)
