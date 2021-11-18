#!/usr/bin/python3

def main():
    from mmc5983 import MMC5983
    from llog import LLogWriter

    device = "mmc5983"
    parser = LLogWriter.create_default_parser(__file__, device)
    parser.add_argument("--bus", type=int, default=None, help="i2c bus")
    args = parser.parse_args()


    with LLogWriter(args.meta, args.output, console=args.console) as log:
        mmc = MMC5983(i2cbus=args.bus)

        def data_getter():
            data = mmc.measure()
            return f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x:.6f} {data.y:.6f} {data.z:.6f} {data.t:.3f}"

        log.log_data_loop(data_getter, parser_args=args)

if __name__ == '__main__':
    main()
