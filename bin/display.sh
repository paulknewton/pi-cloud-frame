#!/usr/bin/env bash


USAGE="usage: display {on|off}"

if [ $# -ne 1 ]; then
  echo $USAGE
  exit 1
fi

case $1 in
    on)
        echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power > /dev/null
        ;;
    off)
        echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power > /dev/null
        ;;
    *)
        echo "unknown argument $1"
        echo $USAGE
        exit 1
esac
