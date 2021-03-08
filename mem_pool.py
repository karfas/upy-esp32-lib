#
# mem_pool.py
#
# very primitive memory handling.
# For use with pre-allocated bytearray or with uctype
#
class MemPoolAllocException(BaseException):
    pass

class MemPool():
    def __init__(self, addr, size):
        self._base = addr
        self._top = addr + size
        self._addr = addr

    def addr(self):
        return self._addr

    def space(self):
        return self._top - self._addr

    def alloc(self, size):
        addr = self._addr
        new_addr = addr + size
        if new_addr >= self._top:
            raise MemPoolAllocException()
        self._addr = new_addr
        return addr
