import os
import json
import shutil

"""
The extraction and filtering will lead to an overlap of functions with same name. With this script we can clean that.  press n to dicsrd and enter to keep the fucntion.
"""


def process_file(path):
    with open(path, 'r') as f:
        data = json.load(f)

    new_data = []
    print("---------------------")
    print("file:" , path)
    if len(data) == 1:
        new_data.append(data[0])
    else:
        print("elements:", len(data))
        for d in data:
            print("-----")
            print(d["code_file_path"])
            for k,v in d['signature'].items():
                print(k,v)

            choice = input("discard? press n: ").strip().lower()
            # if n enter was pressed this speciufic instance is deleted 
            if choice != 'n':
                new_data.append(d)
                break
    
    with open(path, 'w') as f:
        json.dump(new_data, f)
    
    if new_data == []:
        print("file now empty")
        return False

    return True

failures = []

for dirpath, _, filenames in os.walk("./java/"):
    for filename in filenames:
        if filename == 'analyzed.json':
            if not process_file(os.path.join(dirpath, filename)):
                failures.append(dirpath)
                
with open("./failed.txt", "w") as f:
    for l in failures:
        f.write(l + "\n")

