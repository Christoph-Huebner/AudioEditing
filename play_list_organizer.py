import argparse
import ffmpeg
import math
import os
import random
import shutil

def organize_files(args):
    '''
    Organizes music files into numbered subfolders with even, random distribution by artist.
    '''

    # ---------------------------------------------------------------------------------------------------
    # Preparations / Definitions
    # ---------------------------------------------------------------------------------------------------
    main_sub_path = os.path.join(args.path, 'tmp2')
    sub_dir_path = os.path.join(main_sub_path, 'Liste_')
    console_len = max(len(f) for f in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, f)))
    width_Prefix_num = 4  # 4: 0001 for example

    # Read all files (exclude dirs and playlist (m3u file))
    files = [f for f in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, f)) and not f.endswith('.m3u')]
    cnt_files = len(files)
    cnt_batches = math.ceil(cnt_files / args.batch_size)
    batches = [[] for _ in range(cnt_batches)]

    # Output texts
    prefix_try_run = 'Simulation: ' if args.try_run else ''
    short_prefix_try_run = 'Sim: ' if args.try_run else ''
    txt_header = f"{prefix_try_run}Organize {cnt_files} files in the folder \"{args.path}\" into {cnt_batches} folders (each: {args.batch_size} files)\n\n"
    txt_main_sub_dir = f"{prefix_try_run}Create main subfolder \"{main_sub_path}\"\n"
    txt_sub_dir = f"{prefix_try_run}Create subfolder \"<tag>\"\n"
    txt_file = f"{short_prefix_try_run} Copy file... "
    txt_footer = f"\n\n{prefix_try_run}Finished all and copy {cnt_files} files in {cnt_batches} folders."
    # ---------------------------------------------------------------------------------------------------
    # Group songs by artist and randomly pick a songs from artists (uniform distribution)
    # ---------------------------------------------------------------------------------------------------

    # Initialize the dict witch holds the songs, the key is the artist
    artist_map = {}
    for file in files:
        name = os.path.splitext(file)[0]
        artist = name.split('_', 1)[0] if '_' in name else '<Unknown>'
        artist_map.setdefault(artist, []).append(file)

    # Create if is wished a randomly order dict: artist and there songs a randomly ordered
    if args.random_dist:
        mod_artist_map = dict(zip(random.sample(list(artist_map.keys()), len(artist_map.keys())), [[] for _ in artist_map.keys()]))

        for artist, song in artist_map.items():
            mod_artist_map[artist] = song.copy()
            random.shuffle(mod_artist_map[artist])
    else:
        mod_artist_map = dict(artist_map)

    # Iterate over all artists and take the next song, add this to the batch list
    # Remove this item from the dictionary
    # Take care that the songs in a batch list is lower or equal to the batchSize
    # Otherwise take the next batch list
    batch_idx = 0
    while any(mod_artist_map.values()):
        for artist, songs in mod_artist_map.items():
            if not songs:
                continue
            if len(batches[batch_idx]) < args.batch_size:
                batches[batch_idx].append(songs.pop())
            if len(batches[batch_idx]) >= args.batch_size and batch_idx < cnt_batches - 1:
                batch_idx += 1
    # ---------------------------------------------------------------------------------------------------
    # Actions (copy files, create dirs => not in simulation mode) + print itend
    # ---------------------------------------------------------------------------------------------------

    # Header information for the action, create main sub dir
    actions = []
    print(txt_header.ljust(console_len))
    if not os.path.exists(main_sub_path):
        print(txt_main_sub_dir.ljust(console_len))
        if not args.try_run:
            os.makedirs(main_sub_path, exist_ok=True)

    # Iterate over all batches and files => print new file location and copy item is tryRun is set to true
    file_num = 1
    for idx, batch in enumerate(batches, start=1):
        folder = sub_dir_path + str(idx)
        if not os.path.exists(folder):
            print((txt_sub_dir.replace("<tag>", folder)).ljust(console_len))
            if not args.try_run:
                os.makedirs(folder, exist_ok=True)
        if (idx == cnt_batches):
            print("\n")

        for file in batch:
            prefix_nr = str(file_num).zfill(width_Prefix_num)
            new_file_name = f"{prefix_nr}_{file}"
            new_path = os.path.join(folder, new_file_name)
            new_path_conv = new_path

            if args.convert_2_mp3:
                new_path_conv = os.path.splitext(new_path)[0] + ".mp3"
            actions.append((file.lower(), f"{txt_file}{file.ljust(console_len)} -> {new_path_conv}"))

            if not args.try_run:
                shutil.copy2(os.path.join(args.path, file), new_path)
                if args.convert_2_mp3:
                    convert_audio_2_mp3(new_path, args=args)
            file_num += 1

    for _, action in sorted(actions, key=lambda x: x[0]):
        print(action.ljust(console_len))

    print(txt_footer.ljust(console_len))

def convert_audio_2_mp3(input_file, args, bitrate="320k"):
    '''
    Converts an audio file to MP3 format using ffmpeg.
    '''
    # INSTALL:
    # 1.) Download "ffmpeg-release-essentials.zip" from https://www.gyan.dev/ffmpeg/builds/
    # 2.) Extract the zip file to C:\Program Files x86\ for example
    # 3.) Set the PATH environment system variable "path" to include the ffmpeg bin directory
    # 4.) After a reboot the cmd ffmpeg.exe -version should work
    # 5.) run pip install ffmpeg-python
    output_file, ext = os.path.splitext(input_file)
    output_file = output_file + ".mp3"
    if ext.lower() !=".mp3":
        try:
            if args.dynamic_range_method == "dc":
                (
                    ffmpeg
                    .input(input_file)
                    .filter('acompressor',
                            threshold=args.threshold + 'dB',
                            ratio=args.ratio,
                            attack=args.attack,
                            release=args.release)
                    .output(output_file, audio_bitrate=bitrate, format='mp3', acodec='libmp3lame')
                    .run(overwrite_output=True, quiet=True)
                )
            elif args.dynamic_range_method == "ln":
                (
                    ffmpeg
                    .input(input_file)
                    .output(output_file,
                            af=f"loudnorm=I={args.lufs}:TP={args.true_peak}:LRA={args.loudness_range}:print_format=summary",
                            ar='48k',
                            audio_bitrate=bitrate,
                            format='mp3',
                            acodec='libmp3lame')
                    .run(overwrite_output=True, quiet=True)
                )
            else:
                (
                    ffmpeg
                    .input(input_file)
                    .output(output_file, audio_bitrate=bitrate, format='mp3', acodec='libmp3lame')
                    .run(overwrite_output=True, quiet=True)
                )
            os.remove(input_file)
            #print(f"✅ Konvertiert: {output_file}")
        except ffmpeg.Error as e:
            print("❌ FFmpeg error:")
            print(e.stderr.decode())
            pass
    return output_file

def create_play_list_file(path):
    '''
    Create a m3u file: that plays the tracks in the correct order in vlc or windows media player
    '''
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    with open(os.path.join(path, '_PlayListe.m3u'), 'w') as playlist:
        playlist.write("#EXTM3U\n")

        for file in sorted(files):
            playlist.write(f"{file}\n")

def main():
    #create_play_list_file(path=r"C:\Users\Christoph\Music\_Playlist\tmp2\Liste_1")

    parser = argparse.ArgumentParser(description="Organize and process audio files with ffmpeg.")
    parser.add_argument("-pa", "--path", default=".", help="Path to the directory containing audio files (default: current directory).")
    parser.add_argument("-tr", "--try_run", action="store_true", help="Run in simulation mode without making changes.")
    parser.add_argument("-bz", "--batch_size", type=int, default=100, help="Number of files per batch (default: 100).")
    parser.add_argument("-rd", "--random_dist", action="store_true", help="Distribute files randomly by artist (default: Off).")
    parser.add_argument("-c2", "--convert_2_mp3", action="store_true", help="Convert files to MP3 format (default: Off).")
    subparsers = parser.add_subparsers(dest="dynamic_range_method", title="Processing method", help="Select dynamic range processing method (default: None).")

    dc_parser = subparsers.add_parser("dc", help="Dynamic compression (acompressor)")
    dc_parser.add_argument("-th, --threshold", default="-26", dest="threshold", help="Threshold (default: -26 dB)")
    dc_parser.add_argument("-rt, --ratio", type=float, default=4.0, dest="ratio", help="Compression ratio (default: 4.0)")
    dc_parser.add_argument("-at, --attack", type=int, default=30, dest="attack", help="Attack time in milliseconds (default: 30 ms)")
    dc_parser.add_argument("-re, --release", type=int, default=150, dest="release", help="Release time in milliseconds (default: 150 ms)")

    ln_parser = subparsers.add_parser("ln", help="Loudness normalization (loudnorm)")
    ln_parser.add_argument("-lu, --lufs", type=float, default=-16.0, dest="lufs", help="Loudness in LUFS (default: -16.0)")
    ln_parser.add_argument("-tp, --true_peak", type=float, default=-1.5, dest="true_peak", help="True Peak in dB (default: -1.5)")
    ln_parser.add_argument("-lr, --loudness_range", type=float, default=11.0, dest="loudness_range", help="Loudness Range in LU (default: 11.0)")

    args = parser.parse_args()
    print(f"Arguments: {args}")
    organize_files(args)

if __name__ == '__main__':
    main()
