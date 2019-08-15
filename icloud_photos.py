import logging
import os
import sys

from pyicloud import PyiCloudService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IcloudPhotos:

    def __init__(self, user, password):
        self.api = self._connect(user, password)

    def _connect(self, user, password):
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

        self.api = api

    @staticmethod
    def is_image(photo):
        """
        Check if the photo is an image (excludes videos)

        @:param photo: the photo
        @:return: True if the photo is an image, otherwise False
        """

        # root, ext = os.path.splitext(photo.filename)
        # format = ext.upper()
        format = photo._master_record["fields"]["itemType"]["value"]
        if (format not in ["public.jpeg", "public.png", "public.heic", "public.tiff"]):
            logger.debug("[Invalid format %s - skip]", format)
            return False

        logger.debug("[format %s OK]", format)
        return True

    @staticmethod
    def is_correct_format(photo, orientation):
        """
        Check if the photo is the correct orientation.

        :param photo: the photo
        :param orientation: portrait or landscape
        :return: True if the photo orientation matches the specified orientation
        """

        photo_orientation = photo._asset_record["fields"]["orientation"]["value"]
        width, height = photo.dimensions

        # rotate dimensions if needed
        if photo_orientation in (6, 8):
            width = photo.dimensions[1]
            height = photo.dimensions[0]

        if (orientation == "landscape" and width <= height) or (orientation == "portrait" and width >= height):
            logger.debug("[Invalid orientation %s - skip]", orientation)
            return False

        logger.debug("[orientation %s OK]", orientation)
        return True

    def get_all_photos(self, album, orientation):
        """
        Retrieve all photos from the specified icloud album. Only photos that are images and match the requested orientation are returned.

        @:param album: the icloud album to search
        @:param orientation: the orientation of the photos (portrait or landscape)
        @:return: a list of matching photos
        """
        eligible_photos = []
        i = 1
        for i, photo in enumerate(self.api.photos.albums[album]):
            logger.debug("%d - Checking %s" % (i, photo.filename))
            # asset_types.add(photo._master_record["fields"]["itemType"]["value"])
            if IcloudPhotos.is_image(photo) and IcloudPhotos.is_correct_format(photo, orientation):
                logger.debug("Adding photo")
                eligible_photos.append(photo)

        return eligible_photos

    @staticmethod
    def download(photos, folder):
        """
        Download the specific photos from the icloud and store them locally

        :param photos: list of photos to download
        :param folder: the folder to store the photos locally
        """
        for photo in photos:
            with open(os.path.join(folder, photo.filename), 'wb') as opened_file:
                logger.info("[%s %s %s]" % (
                    photo.filename, photo.dimensions, photo._asset_record["fields"]["orientation"]["value"]))
                data = photo.download().raw.read()

                # cannot crop HEIC images with Pillow
                #crop_image(PIL.Image.open(os.io.BytesIO(data)), float(16 / 9))

                opened_file.write(data)

    def get_albums(self):
        return self.api.photos.albums
