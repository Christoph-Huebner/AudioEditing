import os
import re
import sys

def add_text(path, text, simulation = False, exclusions=[]):
    try:
        cnt = 0
        max_len = max(len(f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        out_arr = []

        for file_name in os.listdir(path):
            full_path_current = os.path.join(path, file_name)

            if os.path.isfile(full_path_current):
                name, ext = os.path.splitext(file_name)

                name_cleaned = name
                name_cleaned = name_cleaned.replace("_", " ").replace("-", " ")
                name_cleaned = re.sub(re.escape(text), "", name_cleaned, flags=re.IGNORECASE)
                for ex in exclusions:
                    name_cleaned = re.sub(re.escape(ex), "", name_cleaned, flags=re.IGNORECASE)
                #nameCleaned = nameCleaned.replace(f"_{text}", "").replace(text, "").strip("_ ")

                name_cleaned = re.sub(r'\d+', '', name_cleaned)
                name_cleaned = re.sub(r'[^A-Za-zÄÖÜäöüß0-9 ]+', '', name_cleaned)
                name_cleaned = re.sub(r'\s+', ' ', name_cleaned).strip()
                name_cleaned = name_cleaned[0].upper() + name_cleaned[1:]

                file_name_new = f"{text}_{name_cleaned}{ext}"
                full_path_new = os.path.join(path, file_name_new)

                if full_path_current != full_path_new:
                    if simulation == False:
                        os.rename(full_path_current, full_path_new)
                    out_arr.append((file_name.lower(), f"Rename: {file_name.ljust(max_len)} -> {file_name_new}"))
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

if __name__ == "__main__":
    args = sys.argv[1] if len(sys.argv) > 1 else "false"
    simulation = args.lower() == "true"
    add_text(path="Z:\\Musik\\_Playlist\\tmp",
            text="Sonstiges",
            simulation=simulation,
            exclusions=[""])
