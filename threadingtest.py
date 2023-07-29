from threading import Thread
import time


updateMe = 0

def updateFunc():
    global updateMe
    time.sleep(5)
    updateMe += 1
    print(updateMe)

count = 0

def main():
    global count
    while True:
        print("This loop always needs to run!")
        count += 1
        print("Count: " + str(count))
        if count == 100:
            thread = Thread(target=updateFunc, daemon=True)
            thread.start()
        time.sleep(0.1)

main()

