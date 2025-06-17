import math
import os
import random
import re
import shutil

from converter import Converter

class Organizer:
    def __init__(self, args):
        self.__path = args.path
        self.__try_run = args.try_run
        # Normalization parameters
        self.__prefix = getattr(args, 'prefix', '')
        self.__exclusions = getattr(args, 'exclusions', "").split(',')
        # Organizer specific parameters
        self.__batch_size = getattr(args, 'batch_size', 0)
        self.__random_dist = getattr(args, 'random_dist', False)
        self.__convert_2_mp3 = getattr(args, 'convert_2_mp3', False)
        self.__converter = Converter(args)

    def organize_files(self):
        '''
        Organizes music files into numbered subfolders with even, random distribution by artist.
        '''

        # ---------------------------------------------------------------------------------------------------
        # Preparations / Definitions
        # ---------------------------------------------------------------------------------------------------
        main_sub_path = os.path.join(self.__path, 'tmp')
        sub_dir_path = os.path.join(main_sub_path, 'list_')
        console_len = max(len(f) for f in os.listdir(self.__path) if os.path.isfile(os.path.join(self.__path, f)))
        width_Prefix_num = 4  # 4: 0001 for example

        # Read all files (exclude dirs and playlist (m3u file))
        files = [f for f in os.listdir(self.__path) if os.path.isfile(os.path.join(self.__path, f)) and not f.endswith('.m3u')]
        cnt_files = len(files)
        cnt_batches = math.ceil(cnt_files / self.__batch_size)
        batches = [[] for _ in range(cnt_batches)]

        # Output texts
        prefix_try_run = 'Simulation: ' if self.__try_run else ''
        short_prefix_try_run = 'Sim: ' if self.__try_run else ''
        txt_header = f"{prefix_try_run}Organize {cnt_files} files in the folder \"{self.__path}\" into {cnt_batches} folders (each: {self.__batch_size} files)\n\n"
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
        if self.__random_dist:
            mod_artist_map = dict(zip(random.sample(list(artist_map.keys()), len(artist_map.keys())), [[] for _ in artist_map.keys()]))

            for artist, song in artist_map.items():
                mod_artist_map[artist] = song.copy()
                random.shuffle(mod_artist_map[artist])
        else:
            mod_artist_map = dict(artist_map)

        # For each artist, add the next song to the current batch and remove it from the dictionary.
        # Start a new batch if the batch size limit is reached.
        batch_idx = 0
        while any(mod_artist_map.values()):
            for artist, songs in mod_artist_map.items():
                if not songs:
                    continue
                if len(batches[batch_idx]) < self.__batch_size:
                    batches[batch_idx].append(songs.pop())
                if len(batches[batch_idx]) >= self.__batch_size and batch_idx < cnt_batches - 1:
                    batch_idx += 1
        # ---------------------------------------------------------------------------------------------------
        # Actions (copy files, create dirs => not in simulation mode) + print itend
        # ---------------------------------------------------------------------------------------------------

        # Header information for the action, create main sub dir
        actions = []
        print(txt_header.ljust(console_len))
        if not os.path.exists(main_sub_path):
            print(txt_main_sub_dir.ljust(console_len))
            if not self.__try_run:
                os.makedirs(main_sub_path, exist_ok=True)

        # Iterate over all batches and files => print new file location and copy item is tryRun is set to true
        file_num = 1
        for idx, batch in enumerate(batches, start=1):
            folder = sub_dir_path + str(idx)
            if not os.path.exists(folder):
                print((txt_sub_dir.replace("<tag>", folder)).ljust(console_len))
                if not self.__try_run:
                    os.makedirs(folder, exist_ok=True)
            if (idx == cnt_batches):
                print("\n")

            for file in batch:
                prefix_nr = str(file_num).zfill(width_Prefix_num)
                new_file_name = f"{prefix_nr}_{file}"
                new_path = os.path.join(folder, new_file_name)
                new_path_conv = new_path

                if self.__convert_2_mp3:
                    new_path_conv = os.path.splitext(new_path)[0] + ".mp3"
                actions.append((file.lower(), f"{txt_file}{file.ljust(console_len)} -> {new_path_conv}"))

                if not self.__try_run:
                    shutil.copy2(os.path.join(self.__path, file), new_path)
                    self.__converter.convert_audio(new_path)
                file_num += 1

        for _, action in sorted(actions, key=lambda x: x[0]):
            print(action.ljust(console_len))

        print(txt_footer.ljust(console_len))

    def create_play_list_file(self):
        '''
        Create a m3u file: that plays the tracks in the correct order in vlc or windows media player
        '''
        files = [f for f in os.listdir(self.__path) if os.path.isfile(os.path.join(self.__path, f))]
        playlist_lines = ["#EXTM3U"] + sorted(files)
        playlist_path = os.path.join(self.__path, '_PlayListe.m3u')

        if (self.__try_run):
            print(f"Simulation: Create playlist file '{playlist_path}' with the following files:")
            for file in playlist_lines:
                print(file)
        else:
            with open(playlist_path, 'w') as playlist:
                for file in playlist_lines:
                    playlist.write(f"{file}\n")
            print(f"Created playlist file '{playlist_path}' with {len(files) -1} files.")

    def norm_files(self):
        '''
        Adds a prefix to the beginning of each file name in the specified directory, excluding certain patterns.
        Normalizes the file names by removing numbers and special characters, and capitalizing the first letter.
        '''
        try:
            cnt = 0
            max_len = max(len(f) for f in os.listdir(self.__path) if os.path.isfile(os.path.join(self.__path, f)))
            out_arr = []
            txt_prefix_rename = "Rename: " if not self.__try_run else "[Simulation] Rename: "

            for file_name in os.listdir(self.__path):
                full_path_current = os.path.join(self.__path, file_name)

                if os.path.isfile(full_path_current):
                    name, ext = os.path.splitext(file_name)

                    name_cleaned = name
                    name_cleaned = name_cleaned.replace("_", " ").replace("-", " ")
                    if not self.__prefix:
                        name_cleaned = re.sub(re.escape(self.__prefix), "", name_cleaned, flags=re.IGNORECASE)
                    for ex in self.__exclusions:
                        name_cleaned = re.sub(re.escape(ex), "", name_cleaned, flags=re.IGNORECASE)
                    #nameCleaned = nameCleaned.replace(f"_{text}", "").replace(text, "").strip("_ ")

                    name_cleaned = re.sub(r'\d+', '', name_cleaned)
                    name_cleaned = re.sub(r'[^A-Za-zÄÖÜäöüß0-9 ]+', '', name_cleaned)
                    name_cleaned = re.sub(r'\s+', ' ', name_cleaned).strip()
                    name_cleaned = name_cleaned[0].upper() + name_cleaned[1:]

                    if self.__prefix:
                        file_name_new = f"{self.__prefix}_{name_cleaned}{ext}"
                    else:
                        file_name_new = f"{name_cleaned}{ext}"
                    full_path_new = os.path.join(self.__path, file_name_new)

                    if full_path_current != full_path_new:
                        if self.__try_run == False:
                            os.rename(full_path_current, full_path_new)
                        out_arr.append((file_name.lower(), f"{txt_prefix_rename} {file_name.ljust(max_len)} -> {file_name_new}"))
                    else:
                        out_arr.append((file_name.lower(), f"Skip: {file_name} already correct."))
                    cnt = cnt + 1
        except Exception as e:
            print(f"Error: {e}")
        finally:
            out_arr.sort(key=lambda x: x[0])
            for _, item in out_arr:
                print(item)
            print(f"Number of files: {cnt}")
