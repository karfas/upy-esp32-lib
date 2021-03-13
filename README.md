# upy-esp32-lib

Generic micropython tools for the ESP32

## FIFO queue in RTC memory

A simple first in/first out queue for small amounts of data surviving deep sleep.
Uses uctypes to specify the payload transferred from/to the queue.

USAGE:
```python
import uctypes
from rtc_mem import rtc_pool
from mem_fifo import MemFifo
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
    q = MemFifo(rtc_pool, struct_def)
    for sample in samples:
        data = create_struct()
        data.time = sample[0]
        data.temperature = sample[1]
        data.pressure = sample[2]
        print("enqueue t={}".format(data.time))
        q.enqueue(data)
        machine.deepsleep(500)

def read_one():
    q = MemFifo(rtc_pool, struct_def)
    data = q.dequeue()
    return data

def read():
    q = MemFifo(rtc_pool, struct_def)
    data = q.dequeue()
    while data is not None:
        print("data from queue: {} {} {}".format(data.time, data.temperature, data.pressure) )
        data = q.dequeue()

```

## mem_fifo.py

Usage:
```python

import uctypes
from mem_pool import MemPool
from mem_fifo import MemFifo

QUEUE_ENTRY = {
    "time":             0 | uctypes.UINT32,
    "temperature":      4 | uctypes.INT16,       # 1/10 Celsius
    }

QUEUE_SLOTS = 20

SIZE=2048
my_memory = bytearray(SIZE)
my_address = uctypes.addressof(my_memory)
pool = MemPool(my_address, SIZE)
queue = MemFifo(pool, QUEUE_ENTRY, QUEUE_SLOTS)

buf = bytearray(uctypes.sizeof(QUEUE_ENTRY))
entry = uctypes.struct(uctypes.addressof(buf))
entry.time = 12345
entry.temperature = 221

queue.enqueue(entry)    # put something in the queue

e = queue.dequeue() # get an entry from the queue
print("time {}, temp {}".format(e.time, e.temperature / 10))

```

## mem_pool.py

Small and very dumb memory pool (misses even a free() call!)

Usage:
```python

import uctypes
from mem_pool import MemPool

SIZE=2048
my_memory = bytearray(SIZE)
my_address = uctypes.addressof(my_memory)
pool = MemPool(my_address, SIZE)

address1 = pool.alloc(4)
address2 = pool.alloc(100)

four = uctypes.bytearray_at(address1, 4)
hundred = uctypes.bytearray_at(address1, 100)

```
