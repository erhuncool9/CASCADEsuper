from DocChecker.utils import inference
import json
import re




def build_signature(method_context, doc=False):
    doc_string = method_context["doc"] if doc else ""
    ctsig = method_context["signature"]

    return doc_string + (" ".join(ctsig["modifier"]) + " " + ('<' + ', '.join(ctsig["generics"]) + '> ' if ctsig["generics"] else '') +
                 ctsig["returns"] + " " + ctsig["name"] + "(" + ", ".join(ctsig["params"]) + ")" +
                         (" throws " + ", ".join(ctsig["exceptions"]) if ctsig.get("exceptions") else ""))





def get_prediction(target):
    try:
        inference(raw_code=target, language="java", output_file_path="./prediction.json")
        with open("./prediction.json") as f:
            result = json.load(f)
            prediction = result[0]["predict"]

    except Exception as e:
        result = e
        prediction = "Error"

    with open("./log.txt", "a") as log:
        log.write(str(target) + "\n")
        log.write(str(result) + "\n")
        log.write(str(prediction) + "\n")
        log.write("--------------\n")

    if prediction == "Inconsistent!":
        prediction = "Positive"
    elif prediction == "Consistent!":
        prediction = "Negative"
    else:
        prediction = "Error"

    return prediction


if __name__ == '__main__':
    # this first reads in the analyzed.json
    with open("./analyzed.json") as f:
        data = json.load(f)

    sample = data[0]
    code = sample["code"]
    doc = sample["doc"]

    # we do three evaluations
    # one is with the code as is
    signature_with_doc = build_signature(sample, doc=True)
    target1 = signature_with_doc + "{\n" + code + "\n}"
    prediction1 = get_prediction(target1)

    # second everything put into one long line in a comment
    signature = build_signature(sample, doc=False)

    pattern = re.sub(r"/\*\*?|\\\*/", "", doc)
    clean_doc = re.sub(r"^\s*\*\s?", "", pattern, flags=re.MULTILINE).strip()

    target2 =  signature + "{\n    // " + clean_doc.replace("\n", " ").strip() + "\n\n" + code + "\n}"
    prediction2 = get_prediction(target2)

    # the third is we prompt the model once for each line that is longer than 3 characters.
    comment_lines = clean_doc.split("\n")
    predictions3_collection3 = []
    for comment in comment_lines:
        if len(comment.strip()) > 3:
            target3 = signature + "{\n    // " + comment.strip() + "\n\n" + code + "\n}"
            tmp = get_prediction(target3)
            predictions3_collection3.append(tmp)


    # verdict as long as there is one positive in there we predict a positive:
    prediction3 = "Positive" if "Positive" in predictions3_collection3 else "Negative"

    result = f"{prediction1}; {prediction2}; {prediction3}; [{','.join(predictions3_collection3)}]"
    print(result)

    with open("./result.txt", "w") as f:
        f.write(result)

