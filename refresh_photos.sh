#! /bin/sh

# Download a set of random photos from icloud and crop to the correct aspect ratio
# usage: refresh_photos.sh icloud_id icloud_pwd download_folder crop_folder sample_size

DOWNLOAD=$3			# folder to store raw downloaded photos
CROPPED=$4			# folder to store re-cropped photos (with correct aspect ratio)
SAMPLE_SIZE=$5	# number of photos to download

# empty the current set of raw images (normally already done)
rm -f "$DOWNLOAD"/*

# download photos from icloud
python3 download_icloud_photos.py "$1" "$2" "$DOWNLOAD" $SAMPLE_SIZE

# empty the current set of cropped images (currently in use)
rm -f "$CROPPED"/*

# crop the new photos
echo "Cropping photos from $DOWNLOAD to $CROPPED..."
cd "$CROPPED"
for i in "../$DOWNLOAD"/*; do echo `basename $i`; aspectcrop -a 16:9 "$i" `basename $i`; done
cd ..

# tidy up the raw photos
rm -f "$DOWNLOAD"/*
