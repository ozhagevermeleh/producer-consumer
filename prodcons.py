from win32event import *
import mmap
from time import sleep
from random import randint
import sys


def produce():
    while True:
        yield 1


FILENAME = "buffer.txt"
BUFFER_SIZE = 8

with open(FILENAME, "r+b") as file:
    buffer = mmap.mmap(file.fileno(), BUFFER_SIZE + 2)
    buffer[:] = (0).to_bytes(BUFFER_SIZE + 2, "big")

space_s = CreateSemaphore(None, BUFFER_SIZE, BUFFER_SIZE, "space")
item_s = CreateSemaphore(None, 0, BUFFER_SIZE, "item")
mutex = CreateMutex(None, False, "mutex")

# producer
if sys.argv[1] == "p":
    gen = produce()
    while True:
        WaitForSingleObject(space_s, INFINITE)
        WaitForSingleObject(mutex, INFINITE)
        start = buffer[-2]
        buffer[start] = next(gen)
        buffer[-2] = (buffer[-2] + 1) % BUFFER_SIZE
        print(buffer[:])
        ReleaseMutex(mutex)
        ReleaseSemaphore(item_s, 1)
        sleep(randint(0, 3))


# consumer
else:
    while True:
        WaitForSingleObject(item_s, INFINITE)
        WaitForSingleObject(mutex, INFINITE)
        start = buffer[-1]
        buffer[start] = 0
        buffer[-1] = (buffer[-1] + 1) % BUFFER_SIZE
        print(buffer[:])
        ReleaseMutex(mutex)
        ReleaseSemaphore(space_s, 1) 
        sleep(randint(0, 3))

