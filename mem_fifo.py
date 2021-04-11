"""
mem_fifo.py
============================================================================
Create a queue/storage for small amounts of data inside a given memory pool.
"""
import uctypes
import sys

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
    """ Class managing a simple FIFO queue"""
    def __init__(self, addr, size, struct):
        """
        Attach to an existing queue or create a new one at the location defined by
        the pool parameter.

        Parameters
        ----------
        pool
            A memory pool
        struct_def
            Definition of an uctype structure.
            This describes the messages we will manage in the queue.
        entries
            An integer limiting the number of messages in the queue.
            Default: use entire memory allocated in pool for messages.

        """
        hdr_size = uctypes.sizeof(FIFO_HEADER)
        elem_size = uctypes.sizeof(struct)
        hdr = uctypes.struct(addr, FIFO_HEADER)
        entries = size // elem_size
        if hdr.magic != FIFO_MAGIC or hdr.elem_size != elem_size or hdr.elements != entries:
            print("MemFifo: init queue")
            hdr.rd_i = 0
            hdr.wr_i = 0
            hdr.elem_size = elem_size
            hdr.elements = entries
            hdr.magic = FIFO_MAGIC
            hdr.full = False
        self._hdr = hdr
        self._data_addr = addr + uctypes.sizeof(self._hdr)
        self._struct = struct

    def _incr_wrap(self, index):
        index = index + 1
        if index == self._hdr.elements:
            index = 0
        return index

    def enqueue(self, data):
        """
        Adds a data record to the queue.

        Raises a QueueOverrunException when there are no more slots available in
        in the queue.

        Parameters
        ----------
        data
            An uctype stucture holding the message to add to the queue.
            The structure SHOULD conform to the definition given when creating
            the MemFifo object or should at least have the same size.
            Longer structures get silently truncated when addded to the queue.
        """
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
        """
        Removes the first message from the queue and returns either the data as
        uctype struct or None when the queue is empty.

        The returned value references memory directly in the queue slot, so it might
        change when enqueue() is called!
        """
        hdr = self._hdr
        if (not hdr.full) and (hdr.rd_i == hdr.wr_i):
            return None
        addr = self._data_addr + hdr.elem_size * hdr.rd_i
        hdr.rd_i = self._incr_wrap(hdr.rd_i)
        hdr.full = False
        return uctypes.struct(addr, self._struct)

