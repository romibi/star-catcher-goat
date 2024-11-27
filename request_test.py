import time
import threading

import grequests

import random

def get_random_color():
    r = lambda: random.randint(0,255)
    return '%02X%02X%02X' % (r(),r(),r())

def get_random_url(hub, segment):
    color = get_random_color()
    return f"http://10.128.0.10{hub}/win&SM={segment}&SB=255&CL=H{color}&SV=2"

# change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
def update_leds():
    urls = []

    for hub in (1,2,3,4,5,6,7,8,9):
        for segment in (0,1,2,3,4,5):
            urls += [get_random_url(hub, segment)]

    rs = (grequests.get(u, timeout=5) for u in urls)

    def call_map(rs, exception_handler):
        grequests.map(rs, exception_handler=exception_handler, gtimeout=20)

    threading.Thread(target=call_map, args=(rs,None)).start()
    #call_map(rs,None)

def main():
    while True:
        update_leds()
        time.sleep(1)


if __name__ == "__main__":
    main()