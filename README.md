This fork adds python 2 compatibility and a new close() method. test.py is modified to print sensor values for easy testing.

**CompassData Interface Structure:**
+ \_\_init\_\_(rawdata, caldata) - raw values are extracted from rawdata, and then real values are calculated using information provided in the [datasheet](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf).

**MMC5983 Interface Structure:**
+ \_\_init\_\_(bus=1, cs=1, i2cbus=None) - open port at some bus and chip select number or use i2c, run (software_reset(), read_id(), config1(), config2(), calibrate())
+ config1() - write harcoded parameters to REG_CONTROL1
+ config2() - write harcoded parameters to REG_CONTROL2
+ software_reset() - write soft reset command to a control register, and sleep
+ reset() - write reset command to a control register, and sleep
+ set() - Write SET bit to MMC
+ calibrate() - get data after set(), get data after reset(), calculate mean
+ set_BW(BW=(REG_CONTROL1_BW0 | REG_CONTROL1_BW1)) - set BW0 or BW1 bits to set bandwidth
+ read_id() - read device id register
+ measure() - run read_data() - **no real use**
+ read_data() - get 8 bytes of data and use CompassData for calculation - **can put CompassData into measure() to make read_data() more generic and give measure() a purpose**
+ read(reg, nbytes=1) - read a number of bytes from the select register and successive registers
+ readByte(reg) - run read() with nbytes=0to get single byte
+ write(reg, data) - write data to select register
+ readI2C(reg, nbytes=1) - launched from \_\_init\_\_() if using i2c bus - **todo check if i2c can be used and if library runs correctly, otherwise can be removed**
+ writeI2C(reg, data) - **same case as readI2C()**
+ close() - close MMC port

If you only need the Magnetic North direction then units can be ignored, but according to the library file they should be in gauss.
