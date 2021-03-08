# upy-esp32-lib

Generic micropython tools for the ESP32

## rtc_fifo.py

A simple first in/first out queue for small amounts of data surviving deep sleep.
Uses uctypes to specify the payload transferred from/to the queue.

USAGE:
```
import uctypes
from rtc_fifo import RTCFIFO
import machine

struct_def = {
    "time":             0 | uctypes.UINT32,
    "temperature":      4 | uctypes.INT16,       # 1/10 Celsius
    "pressure":         8 | uctypes.UINT16       # 1/10 hPa
}
samples = (
    [ 100, 20, 10320],
    [ 200, 21, 10321],
    [ 400,  5,  9000], # Storm!
    [ 500,  5, 10000], # Storm!
    )

def create_struct():
    arr = bytearray(uctypes.sizeof(struct_def))
    data = uctypes.struct(uctypes.addressof(arr), struct_def)
    return data

def sleeptest():
    q = RTCFIFO(struct_def)
    for sample in samples:
        data = create_struct()
        data.time = sample[0]
        data.temperature = sample[1]
        data.pressure = sample[2]
        print("enqueue t={}".format(data.time))
        q.enqueue(data)
        machine.deepsleep(500)

def read_one():
    q = RTCFIFO(struct_def)
    data = q.dequeue()
    return data

def read():
    q = RTCFIFO(struct_def)
    data = q.dequeue()
    while data is not None:
        print("data from queue: {} {} {}".format(data.time, data.temperature, data.pressure))
        data = q.dequeue()

``` 

## mem_fifo.py 

Logic behind RTCFIFO. Can use almost any address space to create a FIFO in.

## mem_pool.py 

Small and very dumb memory pool (misses even a free() call!)

