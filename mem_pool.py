#
# mem_pool.py
#
# very primitive memory handling.
# For use with pre-allocated bytearray or with uctype
#
import uctypes


class MemPoolAllocException(BaseException):
    pass
class MemPoolInvalidException(BaseException):
    pass

POOL_DEF = {
    "magic":    0 | uctypes.UINT32,
    "addr":     4 | uctypes.UINT32,
    "top":      8 | uctypes.UINT32,
    }
POOL_MAGIC = 0x389ac54f

class MemPool():
    #
    # creates a memory pool or attaches to an existing one
    #
    def __init__(self, addr, size):
        self._head = uctypes.struct(addr, POOL_DEF)
        if self._head.magic != POOL_MAGIC:
            print("create new pool, addr={:x}, size={}".format(addr, size))
            self._head.magic = POOL_MAGIC
            self._head.top = addr + size
            self._head.addr = addr + uctypes.sizeof(POOL_DEF)

    def _magic(self):
        if self._head.magic != POOL_MAGIC:
            raise MemPoolInvalidException

    def addr(self):
        self._magic()
        return self._head.addr

    def space(self):
        self._magic()
        return self._head.top - self._head.addr

    def alloc(self, size):
        self._magic()
        new_addr = self._head.addr + size
        if new_addr >= self._head.top:
            raise MemPoolAllocException()
        self._head.addr = new_addr
        return self._head.addr

