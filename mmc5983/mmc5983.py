import smbus2
import spidev
import time

REG_XOUT_L = 0x00
REG_TOUT = 0x07
REG_STATUS = 0x08
REG_CONTROL0 = 0x09
REG_CONTROL1 = 0x0A
REG_CONTROL2 = 0x0B
REG_CONTROL3 = 0x0C
REG_PRODUCT_ID = 0x2F

# bits in REG_CONTROL0
REG_CONTROL0_TMM = (1<<0)
REG_CONTROL0_TMT = (1<<1)
REG_CONTROL0_SET = (1<<3)
REG_CONTROL0_RESET = (1<<4)

# bits in REG_CONTROL1
REG_CONTROL1_BW0 = (1<<0)
REG_CONTROL1_BW1 = (1<<1)
REG_CONTROL1_SW_RST = (1<<7)

MIN_DELAY_SET_RESET = 1e-3
MIN_DELAY_MEASURE = 1.6e-3

MMC5883_ID = 0x0C

# default i2c address
_address = 0x30

class CompassData:
    def __init__(self, rawdata, caldata):
        self.x_raw = int.from_bytes(rawdata[0:2], 'big')
        self.y_raw = int.from_bytes(rawdata[2:4], 'big')
        self.z_raw = int.from_bytes(rawdata[4:6], 'big')

        xyz2 = rawdata[6]
        self.x_raw = (self.x_raw << 2) | (((xyz2 & 0xC0) >> 6) & 0x3)
        self.y_raw = (self.y_raw << 2) | (((xyz2 & 0x30) >> 4) & 0x3)
        self.z_raw = (self.z_raw << 2) | (((xyz2 & 0x03) >> 2) & 0x3)

        self.x_raw -= 0x20000
        self.y_raw -= 0x20000
        self.z_raw -= 0x20000

        # field strength in gauss
        self.x_norm = self.x_raw/16384
        self.y_norm = self.y_raw/16384
        self.z_norm = self.z_raw/16384

        self.x = self.x_norm + caldata[0]
        self.y = self.y_norm + caldata[1]
        self.z = self.z_norm + caldata[2]

        self.t_raw = rawdata[7]
        self.t = self.t_raw*200.0/256 - 75

class MMC5983:

    def __init__(self, bus=1, cs=1, i2cbus=None):
        if i2cbus is None: # spi communication
            self._bus = spidev.SpiDev()
            self._bus.open(bus, cs)
            self._bus.max_speed_hz = 10000000 # 10MHz
        else: # i2c communication
            self._bus = smbus2.SMBus(i2cbus)
            self.read = self.readI2C
            self.write = self.writeI2C

        self.caldata = [0, 0, 0]
        self.reset()
        self._id = self.read_id()
        self.set_BW()
        self.calibrate()

    def software_reset(self):
        self.write(REG_CONTROL1, [REG_CONTROL1_SW_RST])
        time.sleep(0.01)

    def reset(self):
        self.write(REG_CONTROL0, [REG_CONTROL0_RESET])
        time.sleep(MIN_DELAY_SET_RESET)

    def set(self):
        self.write(REG_CONTROL0, [REG_CONTROL0_SET])
        time.sleep(MIN_DELAY_SET_RESET)

    def calibrate(self):
        self.set()
        setdata = self.measure()
        self.reset()
        resetdata = self.measure()
        self.caldata = [
            (setdata.x - resetdata.x)/2,
            (setdata.y - resetdata.y)/2,
            (setdata.y - resetdata.y)/2
        ]


    def set_BW(self, BW=(REG_CONTROL1_BW0 | REG_CONTROL1_BW1)):
        self.write(REG_CONTROL1, [BW])

    def read_id(self):
        id = self.readByte(REG_PRODUCT_ID)
        return id

    def measure(self):
        self.write(REG_CONTROL0, [REG_CONTROL0_TMM])
        time.sleep(MIN_DELAY_MEASURE)
        status = self.readByte(REG_STATUS)
        while not ((status & 1) == 1):
            status = self.readByte(REG_STATUS)
            continue

        rawdata = self.read(REG_XOUT_L, 8)
        return CompassData(rawdata, self.caldata)

    def read(self, reg, nbytes=1):
        xferdata = [0] * (nbytes+1)
        xferdata[0] = reg | 0x80 # read transaction
        return self._bus.xfer(xferdata)[1:]

    def readByte(self, reg):
        return self.read(reg)[0]

    def write(self, reg, data):
        data.insert(0, reg)
        return self._bus.xfer(data)

    def readI2C(self, reg, nbytes=1):
        data = self._bus.read_i2c_block_data(_address, reg, nbytes)
        return data

    def writeI2C(self, reg, data):
        self._bus.write_i2c_block_data(_address, reg, data)
