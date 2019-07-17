import argparse
from pyicloud import PyiCloudService
import logging
import random
import os
from PIL import Image
import io

logging.basicConfig(level=logging.ERROR)


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


def is_eligible(photo):
    print(photo.filename, end=" ")

    root, ext = os.path.splitext(photo.filename)
    if (ext.upper() not in [".JPG", ".HEIC", ".PNG", ".TIF", ".GIF"]):
        print("[Invalid format - skip]", ext)
        return False

    orientation = photo._asset_record["fields"]["orientation"]["value"]
    width, height = photo.dimensions

    # rotate dimensions if needed
    if orientation == 6 or orientation == 8:
        width = photo.dimensions[1]
        height = photo.dimensions[0]

    if width <= height:
        print("Invalid orientation - skip")
        return False

    print("[OK]")
    return True


def get_all_photos(api, album):
    eligible_photos = []
    for photo in api.photos.albums[album]:
        if (is_eligible(photo)):
            eligible_photos.append(photo)

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


def download(photos):
    for photo in photos:
        with open(os.path.join('raw', photo.filename), 'wb') as opened_file:
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
    parser.add_argument("folder", help="folder to store downloaded photos")
    args = parser.parse_args()
    print(args)

    api = connect(args.user, args.password)

    # print("Albums:")
    # for album in api.photos.albums:
    #    print(album)

    # get all photos in the photoframe album
    print("Downloading  photo list...")
    photos = get_all_photos(api, "photoframe")

    # get a random sample to download
    n = 10
    print("Selecting random sample (%d from %d)" % (n, len(photos)))
    photos = get_sample(photos, n)

    download(photos)
