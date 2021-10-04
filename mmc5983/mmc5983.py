import spidev
import time

REG_PRODUCT_ID = 0x2F
REG_XOUT_L = 0x00
REG_TOUT = 0x07
REG_STATUS = 0x08
REG_CONTROL0 = 0x09
REG_CONTROL1 = 0x0A
REG_CONTROL2 = 0x0B
REG_CONTROL3 = 0x0C

# bits in REG_CONTROL0
REG_CONTROL0_RESET = 0x10
REG_CONTROL0_SET = 0x08
REG_CONTROL0_TMM = 0x01
REG_CONTROL0_TMT = 0x02

# bits in REG_CONTROL1
REG_CONTROL1_SW_RST = 0x80
REG_CONTROL1_BW0 = 0x01
REG_CONTROL1_BW1 = 0x02

MIN_DELAY_SET_SET = 1e-3
MIN_DELAY_MEASURE = 1.6e-3

MMC5883_ID = 0x0C

class CompassData:
    def __init__(self, rawdata):
        # self.x_raw = int.from_bytes(rawdata[0:2], 'big') - 0x8000
        # self.y_raw = int.from_bytes(rawdata[2:4], 'big') - 0x8000
        # self.z_raw = int.from_bytes(rawdata[4:6], 'big') - 0x8000
        self.x_raw = int.from_bytes(rawdata[0:2], 'big')
        self.y_raw = int.from_bytes(rawdata[2:4], 'big')
        self.z_raw = int.from_bytes(rawdata[4:6], 'big')

        # self.x_raw = ((rawdata[1] << 8) | rawdata[0]) - 0x8000
        # self.y_raw = ((rawdata[3] << 8) | rawdata[2]) - 0x8000
        # self.z_raw = ((rawdata[5] << 8) | rawdata[4]) - 0x8000
        # self.x_raw = ((rawdata[1] << 10) | (rawdata[0] << 2) | ((rawdata[6] & 0xC0) >> 6)) - 0x20000
        # self.y_raw = ((rawdata[3] << 10) | (rawdata[2] << 2) | ((rawdata[6] & 0x30) >> 4)) - 0x20000
        # self.z_raw = ((rawdata[5] << 10) | (rawdata[4] << 2) | ((rawdata[6] & 0x0C) >> 2)) - 0x20000
        xyz2 = rawdata[6]
        self.x_raw = (self.x_raw << 2) | (((xyz2 & 0xC0) >> 6) & 0x3)
        self.y_raw = (self.y_raw << 2) | (((xyz2 & 0x30) >> 4) & 0x3)
        self.z_raw = (self.z_raw << 2) | (((xyz2 & 0x03) >> 2) & 0x3)

        self.x_raw -= 0x20000
        self.y_raw -= 0x20000
        self.z_raw -= 0x20000

        self.t_raw = rawdata[7]

        # field strength in gauss
        self.x = self.x_raw/16384
        self.y = self.y_raw/16384
        self.z = self.z_raw/16384
        # self.x = self.x_raw/4096
        # self.y = self.y_raw/4096
        # self.z = self.z_raw/4096
        self.t = self.t_raw*200.0/256 - 75

class MMC5983:

    def __init__(self, bus=1, cs=1):
        self._bus = spidev.SpiDev()
        self._bus.open(bus, cs)
        self._bus.max_speed_hz = 10000000
        self.reset()
        self._id = self.read_id()
        self.set_BW()
        self.write(REG_CONTROL3, [0])

    def reset(self):
        self.write(REG_CONTROL2, [REG_CONTROL1_SW_RST])
        time.sleep(0.01)

    def set_BW(self, BW=3):
        self.write(REG_CONTROL1, [BW])

    def read_id(self):
        id = self.readByte(REG_PRODUCT_ID)
        return id

    def measure(self):
        # self.write(REG_CONTROL0, [REG_CONTROL0_TMM])
        self.write(REG_CONTROL0, [REG_CONTROL0_TMM])
        time.sleep(MIN_DELAY_MEASURE)
        status = self.readByte(REG_STATUS)
        while not ((status & 1) == 1):
            status = self.readByte(REG_STATUS)
            continue

        rawdata = self.read(REG_XOUT_L, 8)
        return CompassData(rawdata)

    def read(self, reg, nbytes=1):
        xferdata = [0] * (nbytes+1)
        xferdata[0] = reg | 0x80 # read transaction
        return self._bus.xfer(xferdata)[1:]

    def readByte(self, reg):
        return self.read(reg)[0]

    # todo write and verify
    def write(self, reg, data):
        data.insert(0, reg)
        return self._bus.xfer(data)
