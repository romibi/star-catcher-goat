import time
import threading
import random
import httpx
from httpx import Timeout


def get_random_color():
    r = lambda: random.randint(0,255)
    return '%02X%02X%02X' % (r(),r(),r())

def get_random_url(hub, segment):
    color = get_random_color()
    # todo use json api to use 1 request per hub
    return f"http://10.128.0.10{hub}/win&SM={segment}&SB=255&CL=H{color}&SV=2"

GET_TIMEOUT = Timeout(timeout=5)

# change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
def update_leds():
    urls = []

    for hub in (1,2,3,4,5,6,7,8,9):
        for segment in (0,1,2,3,4,5):
            urls += [get_random_url(hub, segment)]

    def request_url(url, exception_handler):
        try:
            resp = httpx.get(url, timeout=GET_TIMEOUT)
            resp.close()
        except:
            if exception_handler:
                exception_handler()

    for url in urls:
        # todo: use task groups
        threading.Thread(target=request_url, args=(url,None)).start()

def main():
    while True:
        update_leds()
        time.sleep(1)


if __name__ == "__main__":
    main()