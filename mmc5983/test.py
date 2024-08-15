#!/usr/bin/python3

def main():
    from mmc5983 import MMC5983
    
    mmc = MMC5983()
    
    mmc.calibrate()
    while True:
        data = mmc.read_data()
        #print(f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x:.6f} {data.y:.6f} {data.z:.6f} {data.t:.3f} {mmc.caldata[0]} {mmc.caldata[1]} {mmc.caldata[2]}")
        print(data.x, data.y, data.z)
        #mmc.close()

if __name__ == '__main__':
    main()
