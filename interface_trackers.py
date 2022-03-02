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
        file.close()
    return finished


def get_last_done():
    file_name = "last_done.txt"
    last_done = dict()
    with open(file_name, 'r') as file:
        last_done["year"] = file.readline()
        last_done["state"] = file.readline()
        last_done["district"] = file.readline()
    file.close()
    return last_done


def mark_done(year, state, district):
    file_name = "last_done.txt"
    with open(file_name, 'w') as file:
        file.writelines([year, state, district])
    file.close()
