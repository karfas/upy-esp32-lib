# test_rtc_mem.py

import sys
import machine
import uctypes

sys.path.append(".")    # include current directory
sys.path.append("..")   # assume we are in tests/

from rtc_mem import RTCMemory
from mem_fifo import MemFifo

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

rtc_mem = RTCMemory([
    'fifo',     50,             # space for ~3 entries + fifo header
    'something_else', 256
    ])
q = MemFifo(rtc_mem.fifo, struct_def)

def create_struct():
    arr = bytearray(uctypes.sizeof(struct_def))
    data = uctypes.struct(uctypes.addressof(arr), struct_def)
    return data


def overrun():
    for sample in samples:
        data = create_struct()
        data.time = sample[0]
        data.temperature = sample[1]
        data.pressure = sample[2]
        print("enqueue t={}".format(data.time))
        q.put_nowait(data)

def sleeptest():
    for sample in samples:
        data = create_struct()
        data.time = sample[0]
        data.temperature = sample[1]
        data.pressure = sample[2]
        print("enqueue t={}".format(data.time))
        q.put_nowait(data)
        machine.deepsleep(500)

def read_one():
    data = q.get_nowait()
    return data

def read():
    data = q.dequeue()
    while data is not None:
        print("data from queue: {} {} {}".format(data.time, data.temperature, data.pressure))
        data = q.get_nowait()
