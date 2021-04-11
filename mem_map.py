#
# mem_map.py
#

import uctypes
import urandom

AREA_HEAD = {
    "magic":    0 | uctypes.UINT32,
    }
RANDOM_SEED = 686889545



class MemMap():

    class MemDesc():

        def __init__(self, addr, size, magic):
            self.addr = addr
            self.size = size
            self.magic = magic

    def __init__(self, base, size, name_list):
        """
        creates in-object object list of addresses + sizes.
        """

        # remember random generator state (missing in uPy)
        try:
            rand_stat = urandom.getstate()
        except AttributeError:
            rand_stat = None

        urandom.seed(RANDOM_SEED)

        try:
            self._base = base
            self._name_map = {}
            addr = self._base
            print("len name_list", len(name_list))
            for i in range(0, len(name_list), 2):
                name = name_list[i]
                size = name_list[i+1]
                print(i, name, size)
                if not isinstance(size, int):
                    raise ValueError # ("expected int address, not " + str(type(size)))
                self._name_map[name] = MemMap.MemDesc(addr, size, urandom.getrandbits(32))
                addr += size
        finally:
            if not rand_stat is None:
                urandom.setstate(rand_stat)
            pass

    def __getattr__(self, attr):
        print("__getattr__ ", attr)
        entry = self._name_map.get(attr)
        if entry is None:
            raise AttributeError("missing attribute: " + attr)
        return entry

def test():
    layout = [
        'reserved',     64,
        'fifo',       1024,
        'something',     8,
        ]
    mem = bytearray(2048)
    m = MemMap(uctypes.addressof(mem), 2048, layout)
    fifo_mem = m.fifo
    print("fifo: addr={}".format(fifo_mem.addr))
