[![Build Status](https://travis-ci.org/paulknewton/pi-cloud-frame.svg?branch=master)](https://travis-ci.org/paulknewton/pi-cloud-frame)
# pi cloud frame

An icloud-powered digital frame running on a Raspberry Pi.
Downloads a random sample of photos from your icloud account and displays them. Photos are periodically refreshed.

## What is it?

Like most people, I have a digitial photo frame at home. In my case, a beautiful Nixplay display that includes lots of fancy cloud integration. Photos can be uploaded remotely, synchronised from various sources. It even has its own email address!

I am really happy with this frame. The display quality is excellent and for the most part, I haven't had any issues with it.

But there were a few things that I really missed:
* no icloud support - all of my photos are stored in the Apple icloud, but the only way to sync photos to Nixplay is to copy them to some other supported platform like Dropbox

* no auto-cropping - the frame uses 16:9 aspect ratio while most of my photos are 3:2. I have to manually crop these to get them to fit the frame

* no automatic syncing of new photos - all photos need to be manually pushed to the digital frame. This means more manual effort for adding new photos. And uploading the many 1000s of photos I have accumulated over the years is pretty much out of the question

This python code tries to address all of the limitations above. It downloads a random sample of photos from an icloud account (you can specify which album) and crops these to the correct aspect. The photos are periodically cleared out and refreshed as required.

Everything runs on a Raspberry Pi attached to one of the official displays. But you can run this on any Linux box really.

## Install

The main code to download photos is written in python, using the pyicloud library. Install everything via pip. If you are not using virtualenv then you will probably need to run this as super-user via "sudo":

```
pip install -r requirements.txt
```

The cropping is done using the imagemagick libraries (I tried to do this using in python with PIL/Pillow, but these do not have support for the .HEIC image format).

```
sudo apt install imagemagick
```

And finally, the photos are shown on the screen using the "fbi" image viewer. You could use your favourite image viewer/screensaver here.

```
sudo apt install fbi
```


## Running the code

The code has 2 parts: downloading the photos and displaying the photos

### Downloading the photos

Just run the python code, along with the user/pwd icloud details. The program uses default values for everything else.

```
python3 myuser mypwd
```

The program supports different command line arguments that you can use:
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

Once you are happy with the parameters that you need, just run this via a cron job on a periodic basis so that photos get refreshed.

```
crontab -e
```

then add a line like this:

```
0 0 * * * /usr/bin/python3 /home/pi/pi-cloud-frame/icloud_photos.py myuser mypwd --sample 100 --album myphotos --orientation portrait
```

to kick-off the script each day at midnight.

### Displaying the photos

```
todo
```
