import threading
import time

def count1(n):
    for i in range(1, n+1):
        print(f"\t\t{i}")
        time.sleep(.01)

def count2(n):
    for i in range(1, n+1):
        print(f"\t{i}")
        time.sleep(.01)

if __name__ == '__main__':
    print("Hello Threading!")

    # x = threading.Thread(target=count, args=(10,))
    # x.start()
    x = threading.Thread(target=count1, args=(10,))
    y = threading.Thread(target=count2, args=(10,))
    x.start()
    y.start()
    print("done")

    # print(threading.active_count())