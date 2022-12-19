import time
import struct
from enum import IntFlag

__version__ = '0.0.2'

CHIP_ID = 0xEA
I2C_ADDR = 0x68
I2C_ADDR_ALT = 0x69
ICM20948_BANK_SEL = 0x7f

ICM20948_I2C_MST_ODR_CONFIG = 0x00
ICM20948_I2C_MST_CTRL = 0x01
ICM20948_I2C_MST_DELAY_CTRL = 0x02
ICM20948_I2C_SLV0_ADDR = 0x03
ICM20948_I2C_SLV0_REG = 0x04
ICM20948_I2C_SLV0_CTRL = 0x05
ICM20948_I2C_SLV0_DO = 0x06
ICM20948_EXT_SLV_SENS_DATA_00 = 0x3B

ICM20948_GYRO_SMPLRT_DIV = 0x00
ICM20948_GYRO_CONFIG_1 = 0x01
ICM20948_GYRO_CONFIG_2 = 0x02

# Bank 0
ICM20948_WHO_AM_I = 0x00
ICM20948_USER_CTRL = 0x03
ICM20948_PWR_MGMT_1 = 0x06
ICM20948_PWR_MGMT_2 = 0x07
ICM20948_INT_PIN_CFG = 0x0F
ICM20948_FIFO_EN_1 = 0x66
ICM20948_FIFO_EN_2 = 0x67
ICM20948_FIFO_RST = 0x68
ICM20948_FIFO_MODE = 0x69
ICM20948_FIFO_COUNT = 0x70
ICM20948_FIFO_R_W = 0x72
ICM20948_ACCEL_SMPLRT_DIV_1 = 0x10
ICM20948_ACCEL_SMPLRT_DIV_2 = 0x11
ICM20948_ACCEL_INTEL_CTRL = 0x12
ICM20948_ACCEL_WOM_THR = 0x13
ICM20948_ACCEL_CONFIG = 0x14
ICM20948_ACCEL_XOUT_H = 0x2D
ICM20948_GRYO_XOUT_H = 0x33

ICM20948_TEMP_OUT_H = 0x39
ICM20948_TEMP_OUT_L = 0x3A

# Offset and sensitivity - defined in electrical characteristics, and TEMP_OUT_H/L of datasheet
ICM20948_TEMPERATURE_DEGREES_OFFSET = 21
ICM20948_TEMPERATURE_SENSITIVITY = 333.87
ICM20948_ROOM_TEMP_OFFSET = 21

AK09916_I2C_ADDR = 0x0c
AK09916_CHIP_ID = 0x09
AK09916_WIA = 0x01
AK09916_ST1 = 0x10
AK09916_ST1_DOR = 0b00000010   # Data overflow bit
AK09916_ST1_DRDY = 0b00000001  # Data self.ready bit
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

# Register Bits
ICM20948_I2C_SLV0_EN = 0x80
ICM20948_I2C_SLV0_GRP = 0x08
ICM20948_FIFO_EN = 0x40
ICM20948_I2C_MST_EN = 0x20
AK09916_READ = 0x80

ICM20948_FIFO_MODE_STREAM = 0x00    # overwrite old data with new
ICM20948_FIFO_MODE_SNAPSHOT = 0x01  # only write until fifo is full

ICM20948_FIFO_TYPE_ACC = 0x0010
ICM20948_FIFO_TYPE_GYR = 0x000E
ICM20948_FIFO_TYPE_GYR_X = 0x0002
ICM20948_FIFO_TYPE_GYR_Y = 0x0004
ICM20948_FIFO_TYPE_GYR_Z = 0x0008
ICM20948_FIFO_TYPE_TEMP = 0x0001
ICM20948_FIFO_TYPE_MAG = 0x0100
ICM20948_FIFO_TYPE_ACC_GYR = 0x001E
ICM20948_FIFO_TYPE_ACC_GYR_MAG = 0x011E

class ICM20948:
    def write(self, reg, value):
        """Write byte to the sensor."""
        self._bus.write_byte_data(self._addr, reg, value)
        time.sleep(0.0001)

    def read(self, reg):
        """Read byte from the sensor."""
        return self._bus.read_byte_data(self._addr, reg)

    def trigger_mag_io(self):
        user = self.read(ICM20948_USER_CTRL)
        self.write(ICM20948_USER_CTRL, user | ICM20948_I2C_MST_EN)
        time.sleep(0.005)
        self.write(ICM20948_USER_CTRL, user)

    def read_bytes(self, reg, length=1):
        """Read byte(s) from the sensor."""
        return self._bus.read_i2c_block_data(self._addr, reg, length)

    def read_bytes_fifo(self, length=1):
        """Read byte(s) from the fifo queue."""
        self.bank(0)
        data = []
        # read data in 32 bytes chunks due to i2c limit
        for i in range(length//32):
            data += self.read_bytes(ICM20948_FIFO_R_W, 32)
        data += self.read_bytes(ICM20948_FIFO_R_W, length % 32)
        return data

    def bank(self, value):
        """Switch register self.bank."""
        if not self._bank == value:
            self.write(ICM20948_BANK_SEL, value << 4)
            self._bank = value

    def enable_fifo(self, value=True, mode=ICM20948_FIFO_MODE_SNAPSHOT):
        self.bank(0)
        user = self.read(ICM20948_USER_CTRL)
        if (value):
            user |= ICM20948_FIFO_EN
        else:
            user &= ~ICM20948_FIFO_EN
        self.write(ICM20948_USER_CTRL, user)
        self.set_fifo_mode(mode)

    def set_fifo_mode(self, mode):
        self.bank(0)
        self.write(ICM20948_FIFO_MODE, mode)

    def start_fifo(self, type=ICM20948_FIFO_TYPE_ACC_GYR):
        self._fifotype = type
        if type >> 8 and (type & 0xff):
            raise Exception("Magnetometer output currently cannot be discerned from other data in fifo queue")
        self.bank(0)
        self.write(ICM20948_FIFO_EN_1, type >> 8)
        self.write(ICM20948_FIFO_EN_2, type & 0xff)

    def stop_fifo(self):
        self.bank(0)
        self.write(ICM20948_FIFO_EN_1, 0x00)
        self.write(ICM20948_FIFO_EN_2, 0x00)

    def reset_fifo(self):
        self.bank(0)
        self.write(ICM20948_FIFO_RST, 0x01)
        self.write(ICM20948_FIFO_RST, 0x00)

    def get_fifo_count(self):
        self.bank(0)
        data = self.read_bytes(ICM20948_FIFO_COUNT, 2)
        count, = struct.unpack(">h", bytearray(data))
        return count

    def get_fifo_dataset_count(self):
        def check_type(type):
            return self._fifotype & type == type
        count = self.get_fifo_count()
        divider = 0
        if check_type(ICM20948_FIFO_TYPE_ACC):
            divider += 6
        if check_type(ICM20948_FIFO_TYPE_GYR_X):
            divider += 2
        if check_type(ICM20948_FIFO_TYPE_GYR_Y):
            divider += 2
        if check_type(ICM20948_FIFO_TYPE_GYR_Z):
            divider += 2
        if check_type(ICM20948_FIFO_TYPE_TEMP):
            divider += 2
        if check_type(ICM20948_FIFO_TYPE_MAG):
            divider += 6
        return count // divider

    def seek_fifo_begin(self):
        """Advance FIFO Queue to start with first complete set of data.
           Needs to be used when operating in continuous mode."""
        count = self.get_fifo_count()
        set_length = 0
        if self._fifotype & ICM20948_FIFO_TYPE_ACC:
            set_length += 6
        if self._fifotype & ICM20948_FIFO_TYPE_GYR_X:
            set_length += 2
        if self._fifotype & ICM20948_FIFO_TYPE_GYR_Y:
            set_length += 2
        if self._fifotype & ICM20948_FIFO_TYPE_GYR_Z:
            set_length += 2
        if self._fifotype & ICM20948_FIFO_TYPE_TEMP:
            set_length += 2
        offset = count % set_length
        self.read_bytes_fifo(offset)

    def mag_write(self, reg, value):
        """Write a byte to the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR)  # Write one byte
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, value)
        self.bank(0)
        self.trigger_mag_io()

    def mag_read(self, reg):
        """Read a byte from the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | AK09916_READ)
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, 0xff)
        self.write(ICM20948_I2C_SLV0_CTRL, ICM20948_I2C_SLV0_EN | 1)  # Read 1 byte

        self.bank(0)
        self.trigger_mag_io()

        return self.read(ICM20948_EXT_SLV_SENS_DATA_00)

    def mag_read_bytes(self, reg, length=1):
        """Read up to 24 bytes from the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_CTRL, ICM20948_I2C_SLV0_EN | ICM20948_I2C_SLV0_GRP | length)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | AK09916_READ)
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, 0xff)
        self.bank(0)
        self.trigger_mag_io()

        return self.read_bytes(ICM20948_EXT_SLV_SENS_DATA_00, length)

    def magnetometer_ready(self):
        """Check the magnetometer status self.ready bit."""
        return self.mag_read(AK09916_ST1) & 0x01 > 0

    def read_magnetometer_data(self, timeout=1.0):
        self.mag_write(AK09916_CNTL2, 0x01)  # Trigger single measurement
        t_start = time.time()
        while not self.magnetometer_ready():
            if time.time() - t_start > timeout:
                raise RuntimeError("Timeout waiting for Magnetometer Ready")
            time.sleep(0.00001)

        data = self.mag_read_bytes(AK09916_HXL, 6)

        # Read ST2 to confirm self.read finished,
        # needed for continuous modes
        # self.mag_read(AK09916_ST2)

        x, y, z = struct.unpack("<hhh", bytearray(data))

        # Scale for magnetic flux density "uT"
        # from section 3.3 of the datasheet
        # This value is constant
        x *= 0.15
        y *= 0.15
        z *= 0.15

        return x, y, z

    def read_magnetometer_data_fifo(self, length=1):
        data = self.read_bytes_fifo(6*length)

        values = []

        for i in range(length):
            x, y, z = struct.unpack("<hhh", bytearray(data[6*i:6*(i+1)]))

            # Scale for magnetic flux density "uT"
            # from section 3.3 of the datasheet
            # This value is constant
            x *= 0.15
            y *= 0.15
            z *= 0.15

            values.append([x, y, z])

        return values

    def read_accelerometer_gyro_data(self):
        self.bank(0)
        data = self.read_bytes(ICM20948_ACCEL_XOUT_H, 12)

        ax, ay, az, gx, gy, gz = struct.unpack(">hhhhhh", bytearray(data))

        self.bank(2)

        # Read accelerometer full scale range and
        # use it to compensate the self.reading to gs
        scale = (self.read(ICM20948_ACCEL_CONFIG) & 0x06) >> 1

        # scale ranges from section 3.2 of the datasheet
        gs = [16384.0, 8192.0, 4096.0, 2048.0][scale]

        ax /= gs
        ay /= gs
        az /= gs

        # Read back the degrees per second rate and
        # use it to compensate the self.reading to dps
        scale = (self.read(ICM20948_GYRO_CONFIG_1) & 0x06) >> 1

        # scale ranges from section 3.1 of the datasheet
        dps = [131, 65.5, 32.8, 16.4][scale]

        gx /= dps
        gy /= dps
        gz /= dps

        return ax, ay, az, gx, gy, gz

    def read_accelerometer_gyro_data_fifo(self, length=1):
        data = self.read_bytes_fifo(length * 12)

        # scale ranges from section 3.2 of the datasheet
        gs = [16384.0, 8192.0, 4096.0, 2048.0][self._acc_scale]

        # scale ranges from section 3.1 of the datasheet
        dps = [131, 65.5, 32.8, 16.4][self._gyr_scale]

        values = []

        for i in range(length):
            ax, ay, az, gx, gy, gz = struct.unpack(">hhhhhh", bytearray(data[12*i:12*(i+1)]))

            ax /= gs
            ay /= gs
            az /= gs

            gx /= dps
            gy /= dps
            gz /= dps

            values.append([ax, ay, az, gx, gy, gz])

        return values

    def set_accelerometer_sample_rate(self, rate=125):
        """Set the accelerometer sample rate in Hz."""
        self.bank(2)
        # 125Hz - 1.125 kHz / (1 + rate)
        rate = int((1125.0 / rate) - 1)
        # TODO maybe use struct to pack and then write_bytes
        self.write(ICM20948_ACCEL_SMPLRT_DIV_1, (rate >> 8) & 0xff)
        self.write(ICM20948_ACCEL_SMPLRT_DIV_2, rate & 0xff)
        return 1125 / (1 + rate)

    def set_accelerometer_full_scale(self, scale=16):
        """Set the accelerometer fulls cale range to +- the supplied value."""
        self.bank(2)
        value = self.read(ICM20948_ACCEL_CONFIG) & 0b11111001
        self._acc_scale = {2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11}[scale]
        value |= self._acc_scale << 1
        self.write(ICM20948_ACCEL_CONFIG, value)

    def set_accelerometer_low_pass(self, enabled=True, mode=5):
        """Configure the accelerometer low pass filter."""
        self.bank(2)
        value = self.read(ICM20948_ACCEL_CONFIG) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(ICM20948_ACCEL_CONFIG, value)

    def set_gyro_sample_rate(self, rate=125):
        """Set the gyro sample rate in Hz."""
        self.bank(2)
        # 125Hz sample rate - 1.125 kHz / (1 + rate)
        rate = int((1125.0 / rate) - 1)
        self.write(ICM20948_GYRO_SMPLRT_DIV, rate)
        # return the actual sample rate
        return 1125 / (1 + rate)

    def set_gyro_full_scale(self, scale=250):
        """Set the gyro full scale range to +- supplied value."""
        self.bank(2)
        value = self.read(ICM20948_GYRO_CONFIG_1) & 0b11111001
        self._gyr_scale = {250: 0b00, 500: 0b01, 1000: 0b10, 2000: 0b11}[scale]
        value |= self._gyr_scale << 1
        self.write(ICM20948_GYRO_CONFIG_1, value)

    def set_gyro_low_pass(self, enabled=True, mode=5):
        """Configure the gyro low pass filter."""
        self.bank(2)
        value = self.read(ICM20948_GYRO_CONFIG_1) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(ICM20948_GYRO_CONFIG_1, value)

    def read_temperature(self):
        """Property to read the current IMU temperature"""
        # PWR_MGMT_1 defaults to leave temperature enabled
        self.bank(0)
        temp_raw_bytes = self.read_bytes(ICM20948_TEMP_OUT_H, 2)
        temp_raw = struct.unpack('>h', bytearray(temp_raw_bytes))[0]
        temperature_deg_c = ((temp_raw - ICM20948_ROOM_TEMP_OFFSET) / ICM20948_TEMPERATURE_SENSITIVITY) + ICM20948_TEMPERATURE_DEGREES_OFFSET
        return temperature_deg_c

    def __init__(self, i2c_addr=I2C_ADDR, i2c_bus=None):
        self._bank = -1
        self._addr = i2c_addr
        self._fifotype = ICM20948_FIFO_TYPE_ACC

        if i2c_bus is None:
            from smbus import SMBus
            self._bus = SMBus(1)
        else:
            self._bus = i2c_bus

        self.bank(0)

        self._acc_scale = (self.read(ICM20948_ACCEL_CONFIG) & 0x06) >> 1
        self._gyr_scale = (self.read(ICM20948_GYRO_CONFIG_1) & 0x06) >> 1

        if not self.read(ICM20948_WHO_AM_I) == CHIP_ID:
            raise RuntimeError("Unable to find ICM20948")

        self.write(ICM20948_PWR_MGMT_1, 0x80)
        time.sleep(0.01)
        self.write(ICM20948_PWR_MGMT_1, 0x01)
        self.write(ICM20948_PWR_MGMT_2, 0x00)

        self.bank(2)

        self.set_gyro_sample_rate(100)
        self.set_gyro_low_pass(enabled=True, mode=5)
        self.set_gyro_full_scale(250)

        self.set_accelerometer_sample_rate(125)
        self.set_accelerometer_low_pass(enabled=True, mode=5)
        self.set_accelerometer_full_scale(16)

        self.bank(0)
        self.write(ICM20948_INT_PIN_CFG, 0x30)

        self.bank(3)
        self.write(ICM20948_I2C_MST_CTRL, 0x4D)
        self.write(ICM20948_I2C_MST_DELAY_CTRL, 0x01)

        if not self.mag_read(AK09916_WIA) == AK09916_CHIP_ID:
            raise RuntimeError("Unable to find AK09916")

        # Reset the magnetometer
        self.mag_write(AK09916_CNTL3, 0x01)
        while self.mag_read(AK09916_CNTL3) == 0x01:
            time.sleep(0.0001)


if __name__ == "__main__":
    imu = ICM20948()

    while True:
        x, y, z = imu.read_magnetometer_data()
        ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()

        print("""
Accel: {:05.2f} {:05.2f} {:05.2f}
Gyro:  {:05.2f} {:05.2f} {:05.2f}
Mag:   {:05.2f} {:05.2f} {:05.2f}""".format(
            ax, ay, az, gx, gy, gz, x, y, z
        ))

        time.sleep(0.25)
