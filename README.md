[![Build Status](https://travis-ci.org/paulknewton/pi-cloud-frame.svg?branch=master)](https://travis-ci.org/paulknewton/pi-cloud-frame)
[![codecov](https://codecov.io/gh/paulknewton/pi-cloud-frame/branch/master/graph/badge.svg)](https://codecov.io/gh/paulknewton/pi-cloud-frame)

[![DeepSource](https://static.deepsource.io/deepsource-badge-light.svg)](https://deepsource.io/gh/paulknewton/pi-cloud-frame/?ref=repository-badge)
# pi cloud frame
![logo_medium](logo_medium.png)

An icloud-powered digital frame running on a Raspberry Pi.
Downloads a random sample of photos from your icloud account, crops them to the correct aspect ratio and displays them. Supports parallel slideshows, interactive menus, GPS/EXIF lookup and auto rotation via a MPU-6050 accelerometer.

## What is it?

Like most people, I have a digitial photo frame at home.
In my case, a beautiful Nixplay display that includes lots of fancy cloud integration.
Photos can be uploaded remotely and synchronised from various sources. It even has its own email address!

I am really happy with this frame. The display quality is excellent and for the most part, I haven't had any issues with it.

But there were a few things that I really miss:
* no icloud support - all of my photos are stored in the Apple icloud, but the only way to sync photos to Nixplay is to copy them to some other supported platform like Dropbox.

* no auto-cropping - the frame uses 16:9 aspect ratio while most of my photos are 3:2. I have to manually crop these to get them to fit the frame.

* no automatic syncing of new photos - all photos need to be manually pushed to the digital frame. This means more manual effort for adding new photos. And uploading the many 1000s of photos I have accumulated over the years is pretty much out of the question. (UDPATE: Nixplay now support [Dynamic Playlists](https://blog.nixplay.com/2018/10/nixplays-dynamic-playlists-explained) from Google Photos and Dropbox)

All of this means that it becomes a bit of a pain to add photos to my photo frame.
I end up leaving the same set of photos on endless rotation like some old MTV playlist, and all my other photos sit on a remote disk somewhere, gathering digital dust.

This python code tries to solve all of these problems and help to unlock my 1000s of digital photos.
It downloads a random sample of photos from an icloud account (you can specify which album) and automatically crops these to the correct aspect ratio (based on the target photo frame).
The photos are automatically transferred to a Nixplay frame (via Dropbox) or stored in a folder for access by a pi-cloud-frame (running on a Raspberry Pi).

The photo display software runs on a Raspberry Pi connected to an official Pi display (although it could run on anything). The software supports simple photo slideshows, random shuffle but also lots of extras like:
* 'Stacked' photo viewers to allow multiple slideshows to be setup in parallel. The user can jump between slideshows at any time by touching the screen.
* Embedded custom widgets (currently a system dashboard, but others are in the pipeline such as a video player)
* Auto-detect frame orientation and skip non-matching photos (landscape/portrait)
* Interactively delete unwanted photos
* Show meta-information about each photo (date, filename, location of GPS location)

Everything runs on a Raspberry Pi attached to one of the official displays. But you can run this on any Linux box really. The download part can be used without the front-end application (e.g. to download icloud photos for other photos frames).

## Install

The main code to download photos is written in python, using the ```pyicloud``` library, and Qtv5 for the user interface. Install everything via pip. If you are not using virtualenv then you will probably need to run this as super-user via "sudo":

```
pip install -r requirements.txt
```

The cropping is done using the ```imagemagick``` libraries. I tried to do this using in python with ```PIL/Pillow```, but these do not have support for the .HEIC image format.

```
sudo apt install imagemagick
```

## Running the code

The code has 2 parts: downloading the photos and displaying the photos

### Downloading the photos

Just run the script ```refresh_photos``` with the relevant parameters from the root directory:

```
./bin/refresh_photos icloud_id icloud_pwd profile album num_photos
```
where:
* icloud_id - your apple ID
* icloud_pwd - your apple password
* profile - the type of photo frame device. Currently supports ```pi``` or ```nixplay```
* photoalbum - the icloud album to use as the source of the photos
* num_photos - the number of photos to download (or less if the album does not have enough photos)

The script retrieves the list of photos in the specified album. Any portrait photos are ignored, and a random sample is taken from the remaining photos. The script then downloads the photos and crops them to the appropriate aspect ration using the "convert" tool from the imagemagick suite. The cropped photos are saved in the output photo, and any temporary photos are cleaned up.

For reference, the main python script is ```icloud_photos.py``` which takes a series of arguments as follows:
```
usage: icloud_photos.py [-h] [--output OUTPUT] [--sample SAMPLE]
                        [--album ALBUM] [--orientation {portrait,landscape}]
                        user password

icloud photo frame

positional arguments:
  user                  icloud user
  password              password

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       folder to store downloaded photos
  --sample SAMPLE       number of photos to download
  --album ALBUM         icloud album to find photos
  --orientation {portrait,landscape}
                        orientation of photos
```


### Displaying the photos

The photo frame display is written as a Qt5 application. It scans the specified folder for any photos and displays them one at a time before jumping to the next. The folder is scanned after each photo for any updates. The application also supports a 'stack' of media players, allowing the user to switch between multiple slideshows at any time.

The program needs to be configured in ```config.yml``` to specify the folders to search. A sample file is included in ```config_sample.yml```. The configuration consists of 2 parts:

```
frame:
    slideshow_delay: 30000
    media_folder: media
    font: 14
    frame_rotation: true

players:
    Holiday Photo Player:
        type: photo_player
        folder: italy
        
    Family Photo Player:
        type: photo_player
        folder: personal
        
    Video Player:
        type: video_player
        folder: myvideo
```
* frame
    General config parameters for the display frame:
    * slideshow_delay: the delay (in ms) between photo transitions
    * media_folder: the main root of the media files (each player has a sub-folder under this directory)
    * font: size of font to use for popup menus
    * frame_rotation: if frame knows which way it is rotated (using an accelerometer)
* players
    A list of media players.
    * type: the type of media player. The current implementation only support photo_player (video_player is allowed, but is not yet implemented)
    * folder: the sub-folder under ```media_folder``` where the photos/videos are found

Once the photo frame has been configured, run it by typing:
```
./frame.py
```

The application opens and runs the first media player (in the above example photo player). At any time, the user can jump to the next photo by clicking on the right-hand side of the screen, or jump back to the previous photo by clicking on the left-hand side.

If the user clicks on the top or bottom parts of the screen, it jumps to the previous/next media player (if any are configured). In the example above, it would switch to the video player. This allows multiple slide shows to be running in parallel.
