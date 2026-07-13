import json
import os
from typing import List, Dict, Any

from tqdm import tqdm


def load_json_from_path(file_path):
    """
    :return:
    """

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

    except Exception as e:
        print(e)
        return []

    return data


def get_value_from_context(key, context, error_case_callback):
    """
    A function which extracts the value of a key from the context dictionary put in.

    Keys are evaluated hierarchically, so to check "name" in {"signature": {"name": "test"}}, the key would be
    "signature.name".

    :param key: The dictionary key in question
    :param context: The context dictionary to extract from
    :param error_case_callback: The function to execute if anything goes wrong

    :return: The value associated to the key
    """
    components = key.split(".")
    value = context
    for component in components:
        try:
            if component in value:
                value = value[component]
            else:
                return error_case_callback(key)
        except:
            return error_case_callback(key)
    return value


def save_dicts_list_to_json(data: List[Dict[str, Any]], file_path: str, create_folder=True, override=True):
    """
    this saves a list of dictionaries to a json file in the json list format [{},{},{},...]
    :param data: the list of dictionaries that should be saved
    :param file_path: needs to be a path ending with a file name.
    :param create_folder:  if this is True than the specified folder is created if it does not already exist.
    :param override:  a boolean determining whether the specified file can be overridden if it already exists
    """
    # check if file exists
    if os.path.exists(file_path) and os.path.isfile(file_path):
        if override:
            #print("override specified file")
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

        else:
            raise ValueError("file already exists and 'override' is set to False")

    # if file does not exist ...
    else:
        # ... check if the specified directory exists
        if os.path.exists(os.path.dirname(file_path)):
            #print("create file in specified folder")
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

        # if not, create it if allowed
        else:
            if create_folder:
                # print(f"create specified file {file_path} and folder {os.path.dirname(file_path)}")
                os.makedirs( os.path.dirname(file_path))
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=4)

            else:
                raise ValueError(f"specified folder {os.path.dirname(file_path)} does not exist and 'create_folder' is set to False")


def log(content, logger="print"):
    if logger == "print":
        print(content)
    if logger == "tqdm":
        tqdm.write(str(content))
