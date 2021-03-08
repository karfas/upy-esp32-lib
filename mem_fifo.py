# mem_fifo.py
#
# Create a queue/storage for small amounts of data in the RTC.
#
#


import uctypes
import sys

RTC_MEM_SIZE = 2048 # default

# some space for apps using RTC().memory(), e.g. RTC().memory('blah')
RTC_MEM_RESERVED = 64


FIFO_HEADER = {
    "magic":        0 | uctypes.UINT32,
    "rd_i":         4 | uctypes.UINT8,
    "wr_i":         5 | uctypes.UINT8,
    "elements":     6 | uctypes.UINT8,
    "elem_size":    7 | uctypes.UINT8,
    "full":         8 | uctypes.UINT8,
    }
FIFO_MAGIC = 0x3ffd3e80

class QueueOverrunException(BaseException):
    pass


class MemFifo():
    def __init__(self, pool, struct_def, entries = None):
        hdr_size = uctypes.sizeof(FIFO_HEADER)
        elem_size = uctypes.sizeof(struct_def)
        if entries is None:
            entries = (pool.space() - hdr_size) // elem_size
        addr = pool.alloc(entries * elem_size + hdr_size)
        hdr = uctypes.struct(addr, FIFO_HEADER)
        if hdr.magic != FIFO_MAGIC:
            print("MemFifo: init queue")
            hdr.rd_i = 0
            hdr.wr_i = 0
            hdr.elem_size = elem_size
            hdr.elements = entries
            hdr.magic = FIFO_MAGIC
            hdr.full = False
        self._hdr = hdr
        self._data_addr = addr + uctypes.sizeof(self._hdr)
        self._struct = struct_def

    def _incr_wrap(self, index):
        index = index + 1
        if index == self._hdr.elements:
            index = 0
        return index

    def enqueue(self, data):
        hdr = self._hdr
        if hdr.full:
            raise QueueOverrunException()
        addr = self._data_addr + hdr.elem_size * hdr.wr_i
        src = uctypes.bytearray_at(uctypes.addressof(data), hdr.elem_size)
        dst = uctypes.bytearray_at(addr, hdr.elem_size)
        dst[:] = src[:]
        hdr.wr_i = self._incr_wrap(hdr.wr_i)
        hdr.full = hdr.wr_i == hdr.rd_i

    def dequeue(self):
        hdr = self._hdr
        if (not hdr.full) and (hdr.rd_i == hdr.wr_i):
            return None
        addr = self._data_addr + hdr.elem_size * hdr.rd_i
        hdr.rd_i = self._incr_wrap(hdr.rd_i)
        hdr.full = False
        return uctypes.struct(addr, self._struct)

