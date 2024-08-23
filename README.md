# STAR CATCHER GOAT

Catch Stars as a Goat

## Branches:
- PoC-p5js: First Prof of Concept in Javascript using p5js
- master: Re-Implementation in python to run on a raspberry pi

## Setup RPi

I'm using an old Raspberry PI 2 (unless it shows that it is not powerful enough)

### Install:
- Raspberry Pi OS Lite (32-bit) 12 (bookworm)
- checkout  this repo (e.g. to `~/star-catcher-goat`)
- `sudo apt install libegl-dev python3-pip`
- `python3 -m venv scg-venv`
- `source scg-venv/bin/activate`
- `pip install pygame grequests rpi-rf`
- `pip uninstall rpi-gpio` (buggy on bookworm)
- `pip install rpi-lgpio` (works instead on bookworm)
- Enable autologin using raspi-config
- Add the following lines to .bashrc or .zshenv    
```
if [ "`tty`" = "/dev/tty1" ]; then
    source ~/scg-venv/bin/activate
    python3 ~/star-catcher-goat/star_catcher_goat.py
fi
```

### Setup Splash Screen
- `sudo apt install rpd-plym-splash`
- copy `data/Splash_Screen.png` to `/usr/share/plymouth/themes/pix/splash.png`
- Maybe change theme name in `/usr/share/plymouth/plymouthd.defaults`
- If changed theme name also call: `sudo update-initramfs -c -k $(uname -r)`

## Materials:
- TODO list materials
