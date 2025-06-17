import argparse
from organizer import Organizer

def main():
    # Main Menu
    parser = argparse.ArgumentParser(description="Organize and process audio files with ffmpeg.")
    parser.add_argument("-pa", "--path", default=".", dest="path", help="Path to the directory containing audio files (default: current directory).")
    parser.add_argument("-tr", "--try_run", action="store_true", help="Run in simulation mode without making changes.")
    parser_opt = parser.add_subparsers(dest="operation", title="Operation", help="Select audioediting operation.")
    # Operations for the Main Menu
    parser_opt_norm = parser_opt.add_parser("norm", help="Normalize audio files.")
    parser_opt_org = parser_opt.add_parser("org", help="Organize and normalize audio files.")
    parser_opt_play = parser_opt.add_parser("play", help="Create a playlist file from audio files.")

    # Options for the Normalize operation
    parser_opt_norm.add_argument("-pr", "--prefix", default="", dest="prefix", help="Prefix for file names (default: None).")
    parser_opt_norm.add_argument("-ex", "--exclusions", default="", dest="exclusions", help="Comma-separated list of patterns to exclude from normalization (default: None, e.g., 'foo,bar').")

    # Options for the Organize operation
    parser_opt_org.add_argument("-bz", "--batch_size", type=int, default=100, dest="batch_size", help="Number of files per batch (default: 100).")
    parser_opt_org.add_argument("-rd", "--random_dist", action="store_true", help="Distribute files randomly by artist (default: Off).")
    parser_opt_org.add_argument("-c2", "--convert_2_mp3", action="store_true", help="Convert files to MP3 format (default: Off).")
    # Dynamic range processing options
    parser_opt_org_com = parser_opt_org.add_subparsers(dest="dynamic_range_method", title="Dynamic compression method", help="Select dynamic range processing method (default: None).")
    parser_opt_org_com_dc = parser_opt_org_com.add_parser("dc", help="Dynamic compression (acompressor)")
    parser_opt_org_com_dc.add_argument("-th, --threshold", default="-26", dest="threshold", help="Threshold (default: -26 dB)")
    parser_opt_org_com_dc.add_argument("-rt, --ratio", type=float, default=4.0, dest="ratio", help="Compression ratio (default: 4.0)")
    parser_opt_org_com_dc.add_argument("-at, --attack", type=int, default=30, dest="attack", help="Attack time in milliseconds (default: 30 ms)")
    parser_opt_org_com_dc.add_argument("-re, --release", type=int, default=150, dest="release", help="Release time in milliseconds (default: 150 ms)")
    # Loudness normalization options
    parser_opt_org_com_ln = parser_opt_org_com.add_parser("ln", help="Loudness normalization (loudnorm)")
    parser_opt_org_com_ln.add_argument("-lu, --lufs", type=float, default=-16.0, dest="lufs", help="Loudness in LUFS (default: -16.0)")
    parser_opt_org_com_ln.add_argument("-tp, --true_peak", type=float, default=-1.5, dest="true_peak", help="True Peak in dB (default: -1.5)")
    parser_opt_org_com_ln.add_argument("-lr, --loudness_range", type=float, default=11.0, dest="loudness_range", help="Loudness Range in LU (default: 11.0)")

    args = parser.parse_args()
    print(f"Selected parameters: {args}")

    # Call functions based on the selected operation
    organizer = Organizer(args)
    match args.operation:
        case "norm":
            organizer.norm_files()
        case "org":
            organizer.organize_files()
        case "play":
            organizer.create_play_list_file()
        case _:
            parser.print_help()
            exit(1)

if __name__ == '__main__':
    main()
