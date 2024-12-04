# STAR CATCHER GOAT

Catch Stars as a Goat

## Branches:
- PoC-p5js: First Prof of Concept in Javascript using p5js
- master: Re-Implementation in python to run on a raspberry pi

## Setup RPi

I'm using an Raspberry PI 3

### Install:
- Raspberry Pi OS Lite (32-bit) 12 (bookworm)
- checkout  this repo (e.g. to `~/star-catcher-goat`)
- `sudo apt install libegl-dev python3-pip`
- `python3 -m venv scg-venv`
- `source scg-venv/bin/activate`
- `pip install pygame pyserial httpx`
- Enable autologin using raspi-config
- Add one of the following blocks to .bashrc or .zshenv    
```
if [ "`tty`" = "/dev/tty1" ]; then
    source ~/scg-venv/bin/activate
    python3 ~/star-catcher-goat/star_catcher_goat.py
fi
```
or
```
if [ "`tty`" = "/dev/tty1" ]; then
    #tmux new-session -d -s star_catcher_goat '~/start_star_catcher_goat.sh'
    tmux new-session -d -n 'star_catcher_goat'
    tmux send-keys -t star_catcher_goat '~/start_star_catcher_goat.sh' Enter
    tmux -2 attach0session -d
fi
```
- setup automatic shutoff:
```
sudo su
crontab -e
```
and enter
```
0 22 * * * /bin/pkill "python"
0 22 * * * /sbin/shutdown -P +1 It's 22:00
```


### Setup Splash Screen
- `sudo apt install rpd-plym-splash`
- copy `data/Splash_Screen.png` to `/usr/share/plymouth/themes/pix/splash.png`
- Maybe change theme name in `/usr/share/plymouth/plymouthd.defaults`
- If changed theme name also call: `sudo update-initramfs -c -k $(uname -r)`

## Materials:
- TODO list materials

## Notes:
At some point I also did these steps:
- `pip install rpi-rf`
- `pip uninstall rpi-gpio` (buggy on bookworm)
- `pip install rpi-lgpio` (works instead on bookworm)
But as I switched to a different RF module (the ones included in the feather modules) this should not be needed anymore