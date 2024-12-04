import time
import threading
import random
import httpx
from httpx import Timeout


def get_random_color():
    r = lambda: random.randint(0,255)
    return '%02X%02X%02X' % (r(),r(),r())

def get_post(hub):
    color = get_random_color()
    url = f"http://10.128.0.10{hub}/json"
    data = "{'seg':["
    for segment in (0,1,2,3,4,5):
        if segment != 0:
            data += ","
        color = get_random_color()
        data += f"{{'id':{segment},'on':true, 'bri': 255, 'col': ['{color}']}}"
    data += "]}"
    return url, data


GET_TIMEOUT = Timeout(timeout=5)

# change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
def update_leds():
    posts = []

    for hub in (1,2,3,4,5,6,7,8,9):
        posts += [get_post(hub)]

    def do_post(post, exception_handler):
        try:
            print(f"posting to {post[0]}: {post[1]}")
            resp = httpx.post(post[0], data=post[1], timeout=GET_TIMEOUT)
            resp.close()
        except Exception as e:
            print(e)
            if exception_handler:
                exception_handler()

    for post in posts:
        threading.Thread(target=do_post, args=(post,None)).start()

def main():
    while True:
        update_leds()
        time.sleep(1)


if __name__ == "__main__":
    main()