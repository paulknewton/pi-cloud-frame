#! /usr/bin/env python3

import argparse
import logging.config
import sys

import yaml

from network.icloud_photos import IcloudPhotos
from utils import photo_utils

LOG_CONFIG = "logging.yml"
with open(LOG_CONFIG, 'rt') as f:
    logging.config.dictConfig(yaml.safe_load(f.read()))

logger = logging.getLogger(__name__)


def main():
    """
    Read command-line args and start the download
    """
    parser = argparse.ArgumentParser(
        description="icloud photo frame")
    parser.add_argument("user", help="icloud user")
    parser.add_argument("password", help="password")
    parser.add_argument("--output", help="folder to store downloaded network", default="tmp/raw")
    parser.add_argument("--sample", help="number of network to download", type=int, default=5)
    parser.add_argument("--album", help="icloud album to find network", default="All Photos")
    parser.add_argument("--orientation", help="orientation of network", choices=["portrait", "landscape"],
                        default=None)
    parser.add_argument("--list", help="list albums (no photo downloading)", action='store_true', default=False)
    args = parser.parse_args()
    print(args)

    api = IcloudPhotos(args.user, args.password)

    if args.list:
        print("Albums:")
        albums = api.get_albums()
        for album in albums:
            print(album)
        sys.exit(1)

    try:
        # get all network in the photo frame album
        logger.info("Downloading photo list...")
        photos = api.get_all_photos(args.album, args.orientation)
    except KeyError as exception:
        print("Could not find album: ", exception)
        sys.exit(1)

    # get a random sample to download
    logger.info("Selecting random sample (%d from %d)", args.sample, len(photos))
    photos_sample = photo_utils.get_sample(photos, args.sample)

    logger.info("Downloading photos to %s...", args.output)
    IcloudPhotos.download(photos_sample, args.output)


if __name__ == '__main__':
    main()
