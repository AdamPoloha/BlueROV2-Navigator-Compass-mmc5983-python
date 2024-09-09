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
+ measure() - write TMM bit to REG_CONTROL0 (take magnetic measurement) and wait for staus flag, then run read_data()
+ read_data() - get 8 bytes of data and use CompassData for calculation
+ read(reg, nbytes=1) - read a number of bytes from the select register and successive registers
+ readByte(reg) - run read() with nbytes=0to get single byte
+ write(reg, data) - write data to select register
+ readI2C(reg, nbytes=1) - launched from \_\_init\_\_() if using i2c bus - **i2c cannot be used on the selected pins, can be removed**
+ writeI2C(reg, data) - **same case as readI2C()**
+ close() - close MMC port

If only the Magnetic North direction is needed then units can be ignored, but according to the library file they should be in gauss.

The library has an i2c option, but according to the [navigator schematic](https://bluerobotics.com/wp-content/uploads/2022/06/NAVIGATOR-PCB-SCHEMATIC.pdf), the pins used on the Raspberry Pi are for SPI1, SPI6, and GPIO. Therefore, there was no reason to attempt the option's use. The chip seems to have all i2c pins connected and so using it should be possible with jumper wires, but not with the navigator as a HAT.
