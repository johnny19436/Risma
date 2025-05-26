import os
import argparse

def normalize_path(path):
    return os.path.normpath(path).replace("\\", "/")  # make Windows paths consistent too

def should_exclude(rel_path, exclude_list):
    rel_path = normalize_path(rel_path)
    for pattern in exclude_list:
        pattern = normalize_path(pattern)
        if rel_path == pattern or rel_path.startswith(pattern + "/"):
            return True
    return False

def pack_folder_to_txt(folder_path, output_file="packed_output.txt", exclude_list=None):
    exclude_list = exclude_list or ['pack.py', 'packed_output.txt']
    folder_path = os.path.abspath(folder_path)

    with open(output_file, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(folder_path):
            rel_root = os.path.relpath(root, folder_path)
            rel_root = "" if rel_root == "." else normalize_path(rel_root)

            # Modify dirs in-place to skip excluded subdirectories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(rel_root, d), exclude_list)]

            for file in files:
                rel_file_path = normalize_path(os.path.join(rel_root, file))
                if should_exclude(rel_file_path, exclude_list):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    out.write(f"\n==== {rel_file_path} ====\n")
                    out.write(content)
                    out.write("\n")
                except Exception as e:
                    print(f"[!] Skipping {file_path}: {e}")

    print(f"\n✅ Packed folder into {output_file}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack folder contents into a .txt file")
    parser.add_argument("folder", help="Folder path to pack")
    parser.add_argument("--output", default="packed_output.txt", help="Output .txt file")
    parser.add_argument("--exclude", nargs='*', default=[], help="List of file/folder names to exclude")

    args = parser.parse_args()
    pack_folder_to_txt(args.folder, output_file=args.output, exclude_list=args.exclude)
