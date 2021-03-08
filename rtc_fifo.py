import uctypes
from mem_pool import MemPool
from mem_fifo import MemFifo


from sys import platform
print("platform: {}".format(platform))
if platform == "linux":
    glob_addr = uctypes.addressof(bytearray(2048))
if platform == "esp32":
    # from ESP32 data sheet: 8kb from 0x5000_0000 to 0x5000_1fff
    glob_addr = 0x50000200 # rtc_user_mem_data from linker map


RTC_MEM_SIZE = 2048 # default
# some space for apps using RTC().memory(), e.g. RTC().memory('blah')
RTC_MEM_RESERVED = 64

class RTCFIFO(MemFifo):
    def __init__(self, struct, entries = None):
        pool = MemPool(glob_addr + RTC_MEM_RESERVED,
                    RTC_MEM_SIZE - RTC_MEM_RESERVED)
        super(RTCFIFO, self).__init__(pool, struct, entries)
