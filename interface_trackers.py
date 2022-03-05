import os
import csv


# returns giant set of all (year, state, district, tehsil, crop) tuples that have been done
def get_finished_set():
    directory = "trackers"
    finished = set()

    for file_name in os.listdir(directory):
        full_path = os.path.join(directory, file_name)
        with open(full_path, 'r') as file:
            reader = csv.reader(file)
            _ = next(reader)
            for row in reader:
                finished.add((row[0], row[1], row[2], row[3], row[4]))
    for file_name in os.listdir("state_trackers"):
        full_path = os.path.join("state_trackers", file_name)
        with open(full_path, 'r') as file:
            line = file.readline().split("_")
            if len(line) < 5:
                break
            finished.add((line[0], line[1], line[2], line[3], line[4].strip()))
    return finished


def get_last_done():
    file_name = "last_done.txt"
    last_done = dict()
    if os.stat(file_name).st_size == 0:
        return -1
    with open(file_name, 'r') as file:
        last_done["year"] = file.readline().strip()
        last_done["state"] = file.readline().strip()
        last_done["district"] = file.readline().strip()
        last_done["tehsil"] = file.readline().strip()
    return last_done


# expects all string parameters
def mark_done(year, state, district, tehsil):
    file_name = "last_done.txt"
    with open(file_name, 'w') as file:
        file.write(str(year))
        file.write("\n")
        file.write(state)
        file.write("\n")
        file.write(district)
        file.write("\n")
        file.write(tehsil)




