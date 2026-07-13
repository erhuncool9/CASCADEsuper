import os
import json

def repairJunitVersion(d: dict) -> dict:
        if "test_file_path" not in d:
                d["test_file_path"] = d["code_file_path"].replace(".java", "Test.java")

        if "test_package" not in d:
            d["test_package"] = d["package"]

        d["test_imports"] = d.get("test_imports", [])

        junit_found = False
        for imp in d["test_imports"]:
            if "junit" in imp:
                junit_found = True
                break

        if not junit_found:
            if d["junit_version"].startswith("3"):
                d["test_imports"].append("import junit.framework.*;\n")
            elif d["junit_version"].startswith("4."):
                d["test_imports"].append("import org.junit.*;\n")
                d["test_imports"].append("import static org.junit.Assert.*;\n")
            else:
                d["test_imports"].append("import org.junit.jupiter.api.*;\n")
        
        return d


def process_analyzed_json_files(root_folder: str):
    """
    Recursively walks through root_folder, finds all files named 'analyzed.json',
    loads them (expects a JSON list with exactly one dict element),
    applies "repairJunitVersion" to that dict, and writes the updated content back.
    """

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == "analyzed.json":
                file_path = os.path.join(dirpath, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        print("workingwith" , file_path)
                        content = json.load(f)

                    # Validate expected structure
                    if not isinstance(content, list) or len(content) != 1 or not isinstance(content[0], dict):
                        print(f"Skipping {file_path}: unexpected JSON structure")
                        continue

                    data_dict = content[0]

                    # Apply transformation
                    updated_dict = repairJunitVersion(data_dict)

                    # Save back as list with one element
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump([updated_dict], f, indent=2, ensure_ascii=False)

                    print(f"Processed: {file_path}")

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    root_directory = "./java"  # <-- change this
    process_analyzed_json_files(root_directory)

