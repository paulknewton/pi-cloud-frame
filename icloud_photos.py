import logging
import os
import sys

from pyicloud import PyiCloudService

logger = logging.getLogger(__name__)


class IcloudPhotos:

    def __init__(self, user, password):
        self.api = self._connect(user, password)

    @staticmethod
    def _connect(user, password):
        """
        Connect to the icloud

        :param user: the icloud user id
        :param password: the icloud password
        :return a reference to the icloud
        """
        api = PyiCloudService(user, password)

        if api.requires_2sa:  # this attribute is added by the patched pyicloud at https://github.com/picklepete/pyicloud.git
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

    @staticmethod
    def is_image(photo):
        """
        Check if the photo is an image (excludes videos)

        @:param photo: the photo
        @:return: True if the photo is an image, otherwise False
        """

        if not photo:
            return False

        # root, ext = os.path.splitext(photo.filename)
        # media_type = ext.upper()
        media_type = photo._master_record["fields"]["itemType"]["value"]
        if (media_type not in ["public.jpeg", "public.png", "public.heic", "public.tiff"]):
            logger.debug("[Invalid media_type %s - skip]", media_type)
            return False

        logger.info("[media_type %s OK]", media_type)
        return True

    @staticmethod
    def is_correct_format(photo, requested_orientation):
        """
        Check if the photo is the correct orientation.

        :type photo: pyicloud.services.photos.PhotoAsset
        :param photo: the photo
        :param requested_orientation: portrait, landscape or None
        :return: True if the photo orientation matches the specified orientation or orientation is undefined
        """

        if not photo:
            raise ValueError("Photo is not defined")

        if not requested_orientation:
            return True

        if requested_orientation not in ("portrait", "landscape"):
            raise ValueError("requested_orientation must be one of portrait or landscape")

        # exif_orientation = photo._asset_record["fields"]["orientation"]["value"]
        exif_orientation = photo._master_record["fields"]["originalOrientation"]["value"]
        width, height = photo.dimensions

        # rotate dimensions if needed
        logger.debug("EXIF orientation = %s", exif_orientation)
        if exif_orientation in (6, 8):
            width = photo.dimensions[1]
            height = photo.dimensions[0]
        logger.debug("dimensions = %d x %d", width, height)

        # is photo portrait or landscape?
        if width <= height:
            photo_orientation = "portrait"
        else:
            photo_orientation = "landscape"

        if requested_orientation != photo_orientation:
            logger.debug("[Invalid photo orientation (%s) - skip]", photo_orientation)
            return False

        logger.info("[requested_orientation %s OK]", photo_orientation)
        return True

    def get_all_photos(self, album, requested_orientation):
        """
        Retrieve all photos from the specified icloud album. Only photos that are images and match the requested requested_orientation are returned.

        @:param album: the icloud album to search
        @:param requested_orientation: the requested_orientation of the photos (portrait, landscape or None)
        @:return: a list of matching photos
        """
        logger.info("requested_orientation = %s", requested_orientation)
        eligible_photos = []
        for i, photo in enumerate(self.api.photos.albums[album]):
            logger.debug("%d - Checking %s", i, photo.filename)
            # asset_types.add(photo._master_record["fields"]["itemType"]["value"])
            if IcloudPhotos.is_image(photo) and IcloudPhotos.is_correct_format(photo, requested_orientation):
                logger.debug("Adding photo")
                eligible_photos.append(photo)
            else:
                logger.debug("Skipping %s", photo.filename)

        return eligible_photos

    @staticmethod
    def download(photos, folder):
        """
        Download the specific photos from the icloud and store them locally

        :param photos: list of photos to download
        :param folder: the folder to store the photos locally
        """
        for i, photo in enumerate(photos):
            with open(os.path.join(folder, photo.filename), 'wb') as opened_file:
                logger.info("%d - [%s %s %s]", i, photo.filename, photo.dimensions,
                            photo._master_record["fields"]["originalOrientation"]["value"])
                data = photo.download().raw.read()
                # cannot crop HEIC images with Pillow
                # crop_image(PIL.Image.open(os.io.BytesIO(data)), float(16 / 9))
                opened_file.write(data)

    def get_albums(self):
        return self.api.photos.albums
