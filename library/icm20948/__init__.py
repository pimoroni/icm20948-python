import time
import struct
from smbus import SMBus

CHIP_ID = 0xEA
I2C_ADDR = 0x68

AK09916_I2C_ADDR = 0x0c
AK09916_CHIP_ID = 0x09
AK09916_WIA = 0x01
AK09916_ST1 = 0x10
AK09916_ST1_DOR = 0b00000010   # Data overflow bit
AK09916_ST1_DRDY = 0b00000001  # Data ready bit
AK09916_HXL = 0x11
AK09916_ST2 = 0x18
AK09916_ST2_HOFL = 0b00001000  # Magnetic sensor overflow bit
AK09916_CNTL2 = 0x31
AK09916_CNTL2_MODE = 0b00001111
AK09916_CNTL2_MODE_OFF = 0
AK09916_CNTL2_MODE_SINGLE = 1
AK09916_CNTL2_MODE_CONT1 = 2
AK09916_CNTL2_MODE_CONT2 = 4
AK09916_CNTL2_MODE_CONT3 = 6
AK09916_CNTL2_MODE_CONT4 = 8
AK09916_CNTL2_MODE_TEST = 16
AK09916_CNTL3 = 0x32



bus = SMBus(1)

def write(reg, value):
    bus.write_byte_data(I2C_ADDR, reg, value)
    time.sleep(0.0001)

def read(reg):
    return bus.read_byte_data(I2C_ADDR, reg)
    time.sleep(0.0001)

def read_bytes(reg, length=1):
    return bus.read_i2c_block_data(I2C_ADDR, reg, length)

def bank(value):
    write(0x7f, value << 4)

def mag_write(reg, value):
    bank(3)
    write(0x03, AK09916_I2C_ADDR)  # Write one byte
    write(0x04, reg)
    write(0x06, value)
    bank(0)

def mag_read(reg):
    bank(3)
    write(0x03, AK09916_I2C_ADDR | 0x80)
    write(0x04, reg)
    write(0x06, 0xff)
    bank(0)
    return read(0x3b)

def mag_read_bytes(reg, length=1):
    value = []
    for offset in range(length):
        value.append(mag_read(reg + offset))
    return value

def magnetometer_ready():
    return mag_read(0x10) & 0x01 > 0

def read_magnetometer_data():
    mag_write(0x31, 0x01)  # Trigger single measurement
    while not magnetometer_ready():
        time.sleep(0.00001)

    data = mag_read_bytes(0x11, 6)

    #mag_read(0x18)  # Read ST2 to confirm read finished, needed for continuous modes

    x, y, z = struct.unpack("<hhh", bytearray(data))

    # Scale for magnetic flux density "uT" from section 3.3 of the datasheet
    x *= 0.15
    y *= 0.15
    z *= 0.15

    return x, y, z

def read_accelerometer_gyro_data():
    bank(0)
    data = read_bytes(0x2D, 12)

    ax, ay, az, gx, gy, gz = struct.unpack(">hhhhhh", bytearray(data))


    bank(2)

    # Read accelerometer full scale range and
    # use it to compensate the reading to gs
    scale = (read(0x14) & 0x06) >> 1

    # scale ranges from section 3.2 of the datasheet
    gs = [16384.0, 8192.0, 4096.0, 2048.0][scale]

    ax /= gs
    ay /= gs
    az /= gs

    # Read back the degrees per second rate and 
    # use it to compensate the reading to dps
    scale = (read(0x01) & 0x06) >> 1

    # scale ranges from section 3.1 of the datasheet
    dps = [131, 65.5, 32.8, 16.4][scale]

    gx /= dps
    gy /= dps
    gz /= dps

    return ax, ay, az, gx, gy, gz

bank(0)
if read(0x00) == CHIP_ID:
    print("ICM20948 Found!")
else:
    print("Unable to find ICM20940")

write(0x06, 0x01)
# write(0x03, 0x78)  # Don't do this
write(0x07, 0x00)

bank(2)
write(0x00, 0x0A)  # 100Hz sample rate - 1.1 kHz / (1 + rate)
write(0x01, 0b00101001)  # 250 dps

# Accel sensitivity
write(0x14, 0b00101111)  # +-16g

# Accel sample rate divider MSB and LSB
write(0x10, 0x00) # 125Hz - 1.125 kHz / (1 + rate)
write(0x11, 0x08)


bank(0)
write(0x0f, 0x30)
write(0x03, 0x20)

bank(3)
write(0x01, 0x4D) # I2C_MST_ODR_CONFIG
write(0x02, 0x01) 
write(0x05, 0x81)

if mag_read(0x01) == AK09916_CHIP_ID:
    print("Found AK09916")
else:
    print("Unable to find AK09916")

mag_write(0x32, 0x01)
while mag_read(0x32) == 0x01:
    time.sleep(0.0001)

while True:
    x, y, z = read_magnetometer_data()
    print(x, y, z)
    ax, ay, az, gx, gy, gz = read_accelerometer_gyro_data()
    print(ax, ay, az, gx, gy, gz)
    time.sleep(0.25)
