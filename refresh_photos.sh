#! /bin/sh

# Download a set of random photos from icloud and crop to the correct aspect ratio

USAGE="refresh_photos.sh icloud_id icloud_pwd download_folder crop_folder sample_size"

if [ $# -ne 3 ]; then
  echo $USAGE
  exit 1
fi

MEDIA_FOLDER=media
DOWNLOAD=$MEDIA/raw		# folder to store raw downloaded photos
CROPPED=MEDIA/cropped		# folder to store re-cropped photos (with correct aspect ratio)
OUT=$MEDIA/photos
SAMPLE_SIZE=$3		# number of photos to download
ALBUM=photoframe

ROOT=`pwd`

# empty the current set of raw images (normally already done)
rm -f "$DOWNLOAD"/*

# download photos from icloud
echo "Downloading photos to $DOWNLOAD..."
python3 downloader.py "$1" "$2" --output "$DOWNLOAD" --album $ALBUM --sample $SAMPLE_SIZE

# empty the current set of cropped images
rm -f "$CROPPED"/*

# crop the new photos
echo "Cropping photos from $DOWNLOAD to $CROPPED..."
cd "$CROPPED"
for i in "$ROOT/$DOWNLOAD"/*; do echo `basename "$i"`; aspectcrop -a 800:480 "$i" `basename "$i"`; done
cd "$ROOT" 

# clean out the raw photos
rm -f "$DOWNLOAD"/*

# empty the current set of final images (currently in use)
rm -f "$OUT"/*

# convert the new photos
echo "Converting photos from $CROPPED to $OUT..."
cd "$OUT"
for i in "$ROOT/$CROPPED"/*; do echo `basename "$i"`; convert "$i" `basename "$i"`.jpg; done
#for i in "$ROOT/$CROPPED"/*; do echo `basename $i`; mv "$i" .; done
cd $ROOT

# empty the current set of cropped images
rm -f "$CROPPED"/*
