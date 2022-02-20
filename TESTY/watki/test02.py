import threading
import time
import math
from typing import Match

fibo_p = (1 + math.sqrt(5)) / 2
fibo_y = -1 * (1/fibo_p)

def fibo(n):
    print(f"({n}) - {threading.active_count()} - [S]")
    st = time.time()
    tmp_f = (fibo_p**n - (-1 * fibo_p)**(-n)) / (2 * fibo_p - 1)
    tmp_f = round(tmp_f)
    print(f"({n}) - {threading.active_count()} -     - {tmp_f}")
    print(f"({n}) - {threading.active_count()} - [F] - {(time.time() - st):.4}s")
    return tmp_f

def is_prim(x):
    print(f"({x})\t- T:{threading.active_count()}\t- S -")
    st = time.time()

    numberIsPrime = True
    for i in range(2, round(x / 2)+1):
        # print(f"{x} % {i} = {x % i}\t-{numberIsPrime}")
        if x % i == 0:
            numberIsPrime = False
            break

    if numberIsPrime == True:
        sts = "P:"
    else:
        sts = "  "

    print(f"({x})\t- T:{threading.active_count()}\t-   - {sts}{x}")
    print(f"({x})\t- T:{threading.active_count()}\t- E - \t\t\t({(time.time() - st):.4}s)")

if __name__ == '__main__':
    print("Hello Threading!")

    # for n in range(10**3):
    #     x = threading.Thread(target=fibo, args=(n,))
    #     x.start()
    print(threading.active_count())
    time.sleep(2)

    st = time.time()
    for n in range(3, 10**3):
        x = threading.Thread(target=is_prim, args=(n,))
        x.start()
        # x.join()

    x.join()
    print(f"{(time.time() - st):.4}s - {threading.active_count()}")