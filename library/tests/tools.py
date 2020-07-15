import struct


class MockSMBus():
    def __init__(self, bus):
        self.regs = [[0 for x in range(255)] for x in range(4)]
        self.bank = 0

    def read_byte_data(self, addr, reg):
        if reg == 0x00:
            return 0xEA  # ICM20948 CHIP ID
        if reg == 0x3B:
            return 0x09  # AK09916 CHIP ID
        return self.regs[self.bank][reg]

    def write_byte_data(self, addr, reg, value):
        if reg == 0x7f:  # BANK SELECT
            self.bank = value >> 4
        self.regs[self.bank][reg] = value

    def read_i2c_block_data(self, addr, reg, length):
        if length == 6:
            return struct.pack("<hhh", *(
                111,
                222,
                333
            ))
        if length == 12:
            return struct.pack(">hhhhhh", *(
                111,
                222,
                333,
                444,
                555,
                666
            ))
        # temperature data
        if length == 2:
            return struct.pack(">h", 0x400)
