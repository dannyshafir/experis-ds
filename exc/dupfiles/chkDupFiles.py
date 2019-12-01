import os
import hashlib
import csv


def create_functions():
    functions = {
        'scan': {"name" : "Scan sub-directories and search for duplicate files",
             "func": scan_directories
        },
        'dup': {"name": "Output duplicate files to a new csv file",
            "func": dup_csv
        },
        'dirsize': {"name": "Tree-view of sub directories sizes",
            "func": dir_size,
            "default" : '3'
        }
    }
    return functions


def dup_csv(dirs, dups, csv_file):
    '''
    generating a csv file with all the duplicated files (name, size & copies)
    '''
    csv_columns = ['name', 'size', 'copies']
    with open(csv_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for dup_file in dups:
            if dups[dup_file]['copies'] > 1:
                writer.writerow(dups[dup_file])

    print("Finished generating {} file".format(csv_file))


def dir_treeview(dirs, depth, max_depth):
    print('{depth_line} {name} [{size}]'.format(depth_line='==' * depth,
                                                name=dirs['name'],
                                                size=dirs['size']))
    for sub_dir in dirs['dirs']:
        if depth <= max_depth:
            dir_treeview(dirs['dirs'][sub_dir], depth+1, max_depth)
        else:
            return


def dir_size(dirs, dups, depth=3):
    '''
    printing a tree-view of the scanned directory (and sub-directories) sizes
    '''
    print("Directory Tree View")
    print("===================\n")
    dir_treeview(dirs, 0, int(depth))
    print('')


def get_file_hash_value(file_name, chunk_size=1024):
    # takes a file name and returns md5 checksum of the file
    m = hashlib.md5()
    with open(file_name, "rb") as f:
        # Read the 1st block of the file
        chunk = f.read(chunk_size)
        # Keep reading the file until the end and update hash
        while chunk:
            m.update(chunk)
            chunk = f.read(chunk_size)

    # Return the hex checksum
    return m.hexdigest()


def check_file_duplicate(entry_path, entry, file_size, dups):
    print("Analyzing {}".format(entry_path))
    file_hash_content = get_file_hash_value(entry_path)
    if file_hash_content in dups:
        shortest_name = dups[file_hash_content]['name']
        if len(entry) < len(shortest_name):
            dups[file_hash_content]['name'] = entry
        dups[file_hash_content]['copies'] += 1
    else:
        dups[file_hash_content] = { 'name': entry, 'size': file_size, 'copies': 1}


def scan_directories(upper_dir, dups, dir_path):
    '''
    scan the directory and its sub-directories (calling this function
    recursively). check for each directory its size (sum of all its
    files' and sub-directories' sizes, and also check for duplicated files
    using hash function on the files' content
    '''
    upper_dir['files'] = []
    upper_dir['size'] = 0
    upper_dir['dirs'] = dict()
    if 'name' not in upper_dir:
        upper_dir['name'] = dir_path.split('\\')[-1]
    files_list = os.listdir(dir_path)
    # entries are the file and directories in this path
    for entry in files_list:
        # Create full path
        entry_path = os.path.join(dir_path, entry)
        if os.path.isdir(entry_path):
            # if entry is a directory:
            lower_dir = dict()
            lower_dir['name'] = entry
            scan_directories(lower_dir, dups, entry_path)
            upper_dir['dirs'][entry] = lower_dir
            upper_dir['size'] += lower_dir['size']
        else:
            # if entry is a file
            file_size = os.path.getsize(entry_path)
            upper_dir['size'] += file_size
            upper_dir['files'].append(entry)
            check_file_duplicate(entry_path, entry, file_size, dups)


def chk_command(functions, cmd_line):
    params = cmd_line.split()
    if len(params) == 0:
        return False
    elif params[0] not in functions:
        print("Unrecognised command: ", params[0])
        return False
    elif len(params) == 1:
        if functions[params[0]].get("default") is None:
            print(cmd_line, "what?")
            return False
    return True


def run_commands(dirs, functions, dups):
    keep_run = True
    while keep_run:
        for func in functions:
            print("[{num}] - {func_name}".format(num=func, func_name=functions[func]["name"]))
        cmd_line = input("Select function (Q to exit) >> ").lower()
        if cmd_line == 'q':
            print("Bye...")
            keep_run = False
        elif chk_command(functions, cmd_line):
            cmd = cmd_line.split()[0]
            arg = functions[cmd].get("default")
            if len(cmd_line.split()) > 1:
                arg = cmd_line.split()[1]
            functions[cmd]["func"](dirs, dups, arg)


def main_prog():
    directories = dict()
    duplicates = dict()
    # path = r'C:\Users\user\PycharmProjects\ClassDemo'
    functions = create_functions()
    run_commands(directories, functions, duplicates)


if __name__== "__main__":
    main_prog()

