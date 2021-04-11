#
# rtc_mem.py
#
# Memory pool in RTC memory.
#

from sys import platform

from mem_map import MemMap

if platform == "linux":
    # testing only.
    import uctypes
    mem = bytearray(2048)
    ADDR = uctypes.addressof(mem)
if platform == "esp32":
    # from ESP32 data sheet: 8kb from 0x5000_0000 to 0x5000_1fff
    #
    # Unfortunately, we can't obtain this value from micropython v1.14 itself,
    # so we use rtc_user_mem_data from linker map
    ADDR = 0x50000200


RTC_MEM_SIZE = 2048 # default
# some space for apps using RTC().memory(), e.g. RTC().memory('blah')
RTC_MEM_RESERVED = 64


class RTCMemory(MemMap):
    def __init__(self, layout):
        super().__init__(ADDR + RTC_MEM_RESERVED,
                         RTC_MEM_SIZE - RTC_MEM_RESERVED,
                         layout)

