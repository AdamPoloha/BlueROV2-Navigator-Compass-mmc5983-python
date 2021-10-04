#!/usr/bin/python3

def main():
    from mmc5983 import MMC5983
    from llog import LLogWriter

    device = "mmc5983"
    parser = LLogWriter.create_default_parser(__file__, device)
    args = parser.parse_args()


    with LLogWriter(args.meta, args.output, console=args.console) as log:
        mmc = MMC5983()

        def data_getter():
            data = mmc.measure()
            return f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x:.6f} {data.y:.6f} {data.z:.6f} {data.t:.3f}"
            # return f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {bin(data.x_raw)} {bin(data.y_raw)} {bin(data.z_raw)} {bin(data.xtra)}"
            return f"{data.x_raw:9} {bin(data.x_raw):25} {bin(data.xtra):12}"

        log.log_data_loop(data_getter, parser_args=args)

if __name__ == '__main__':
    main()
