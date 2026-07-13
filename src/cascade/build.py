import json
import os
import shutil
import subprocess
import sys

from cascade.utils.Utils import load_json_from_path


def build(args):
    analyzed_path = args.analyzed_file
    in_path = args.input_path
    out_path = args.output_path
    id_ = args.id

    code = args.code_key
    tests = args.tests_key

    data = load_json_from_path(analyzed_path)

    context = next(item for item in data if item["id"] == id_)
    print(context["package"], context["parent"]["name"])
    print(context["signature"])
    if args.code_key + "_response" in context:
        print(context[args.code_key + "_response"])
    if args.tests_key + "_response" in context:
        print(context[args.tests_key + "_response"])

    if context["language"] != "Java":
        sys.stderr.write("Can only build Java projects right now!")
        exit(-1)

    build_project(context, in_path, out_path, code, tests)


def build_project(context, in_path, out_path, code, tests):
    try:
        shutil.copytree(in_path, out_path, dirs_exist_ok=True)

    except Exception as e:
        print("could not copy root path")
        print(e)

    entry = os.path.join(out_path, "entry.json")
    with open(entry, "w") as json_entry:
        json.dump(context, json_entry)

    my_path = os.path.dirname(__file__)
    p = subprocess.run(
        ["java", "-jar", os.path.join(my_path, "resources", "tools", "JavaExtractor.jar"),
         "mod",
         out_path,
         entry,
         code,
         tests],
        capture_output=True,
        text=True
    )

    os.remove(entry)
