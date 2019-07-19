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
    eligible_photos = []
    #asset_types = set()
    for photo in api.photos.albums[album]:
        #asset_types.add(photo._master_record["fields"]["itemType"]["value"])
        if (is_image(photo) and is_correct_format(photo, orientation)):
            eligible_photos.append(photo)

    #print(asset_types)
    return eligible_photos


def crop_image(image):
    aspect_ratio = float(16 / 9)
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
    for photo in photos:
        with open(os.path.join(folder, photo.filename), 'wb') as opened_file:
            print("[%s %s %s]" % (
                photo.filename, photo.dimensions, photo._asset_record["fields"]["orientation"]["value"]))
            data = photo.download().raw.read()

            # cannot crop HEIC images with Pillow
            # crop_image(Image.open(io.BytesIO(data)))

            opened_file.write(data)


def get_sample(photos, n):
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
    args = parser.parse_args()
    print(args)

    api = connect(args.user, args.password)

    # print("Albums:")
    # for album in api.photos.albums:
    #    print(album)

    # get all photos in the photoframe album
    print("Downloading photo list...")
    photos = get_all_photos(api, args.album, args.orientation)

    # get a random sample to download
    print("Selecting random sample (%d from %d)" % (args.sample, len(photos)))
    photos = get_sample(photos, args.sample)

    print("Downloading photos to %s..." % args.output)
    download(photos, args.folder)
