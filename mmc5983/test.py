#!/usr/bin/python3

def main():
    from llog import LLogWriter
    from mmc5983 import MMC5983
    import time

    device = "mmc5983"
    parser = LLogWriter.create_default_parser(__file__, device)
    parser.add_argument("--bus", type=int, default=None, help="i2c bus")
    parser.add_argument("--cal", type=int, default=None, help="i2c bus")
    args = parser.parse_args()

    with LLogWriter(args.meta, args.output, console=args.console) as log:
        mmc = MMC5983(i2cbus=args.bus)
        lastcal = time.time()

        frequency = args.frequency
        duration = args.duration
        stop_on_error = args.stop_on_error

        start_time = time.time()
        while time.time() < start_time + duration:
            try:
                if time.time() > lastcal + 1:
                    mmc.calibrate()
                    lastcal = time.time()
                data = mmc.read_data()
                logdata = f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x:.6f} {data.y:.6f} {data.z:.6f} {data.t:.3f} {mmc.caldata[0]} {mmc.caldata[1]} {mmc.caldata[2]}"
                log.log_data(logdata)
            except Exception as e:
                log.log_error(f'"{e}"')
                if stop_on_error:
                    return

            if frequency:
                time.sleep(1.0 / frequency)

if __name__ == '__main__':
    main()
