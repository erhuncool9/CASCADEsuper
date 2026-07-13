import os
import sys

from cascade.generation.executor.LLMCallerFactory import create_llm_caller
from cascade.utils.Utils import load_json_from_path, save_dicts_list_to_json


def makeModelRequest(promptList, caller, max_tokens=1200, temperature=0, freq_penalty=0.0):
    response = caller.execute(promptList).model_dump()
    answer = str(response["choices"][0]["message"]["content"])

    return answer


def build_context(context, doc=False, no_fields=False, no_other_method_docs=False, no_other_methods=False, no_constructors=False):
    generics = context["parent"]["generics"]
    implements = context["parent"]["implements"]
    extends = context["parent"]["extends"]
    constructors = context["parent"]["constructors"] if not no_constructors else []
    fields = context["parent"]["variables"] if not no_fields else []
    class_ = f"public class {context['parent']['name']}{('<' + ', '.join(generics) + '>' + ' ' if generics else '')} {('extends ' + ', '.join(extends) + ' ' if extends else '')}{('implements ' + ', '.join(implements) + ' ' if implements else '')}{{\n"

    field_string = "\n".join(fields) + "\n"

    constructor_string = "\n".join(constructors) + "\n"

    other_methods = ""
    for other in (context["parent"]["other_methods"] if not no_other_methods else []):
        other_methods += build_signature(other, doc=(not no_other_method_docs)) + ";\n"

    signature = build_signature(context, doc)

    sig = class_ + field_string + constructor_string + other_methods + signature

    return sig


def build_signature(method_context, doc=False):
    doc_string = method_context["doc"] if doc else ""
    ctsig = method_context["signature"]
    return doc_string + (" ".join(ctsig["modifier"]) + " " + (
        '<' + ', '.join(ctsig["generics"]) + '>' if ctsig["generics"] else '') +
                         ctsig["returns"] + " " + ctsig["name"] + "(" + ", ".join(ctsig["params"]) + ")")


if __name__ == '__main__':
    """
    This script executes the baseline. 
    Calls to a GPT model in a chat style to determine whether code and doc are consistent to each other.
    There are 4 phases to this. 
    First a simple call just asking (1) if code and doc are consistent or not. Yes or No question
    then a simple call asking (2) there is an inconsitency between doc and code

    For the second and third run we provide a lot more information regarding the surrounding class similar 
    to what we provide to CASCADE. :

    Then we ask (3) are code and doc consistent.
    and (4) is there an inconsistency between them
 """

    provider = os.environ.get("CASCADE_LLM_PROVIDER", "openai")
    model = os.environ.get("CASCADE_LLM_MODEL", "gpt-4.1-mini")
    caller = create_llm_caller(
        provider=provider,
        model=model,
        max_tokens=int(os.environ.get("CASCADE_LLM_MAX_TOKENS", "1200")),
        temperature=float(os.environ.get("CASCADE_LLM_TEMPERATURE", "0")),
        freq_penalty=float(os.environ.get("CASCADE_LLM_FREQ_PENALTY", "0.0")),
        base_url=os.environ.get("CASCADE_LLM_BASE_URL"),
        api_key=os.environ.get("CASCADE_LLM_API_KEY"),
        api_key_env=os.environ.get("CASCADE_LLM_API_KEY_ENV"),
        token_parameter=os.environ.get("CASCADE_LLM_TOKEN_PARAMETER"),
    )

    # read in analyze file
    print("start baseline")
    data = load_json_from_path("./analyzed.json")
    d = data[0]

    code = d["code"]
    doc = d["doc"]

    log = []
    results = [None, None, None, None]

    log.append("started Phase 1:\nFull code:")
    full_code = build_signature(d, doc=True) + code + "\n"

    log.append(full_code)

    try:
        # Phase 1 -----------------------------------------------------------------------------------------------
        promptList = []
        promptList.append({"role": "system",
                           "content": "Are the following docstring and code consistent? Answer first with Yes or No, then explain why."})
        promptList.append({"role": "user", "content": f"{full_code}"})

        answer = makeModelRequest(promptList, caller)

        log.append(f"question 1 - answer:\n{answer}")

        for word in answer.lower().split():
            if "yes" in word.strip():
                results[0] = "Negative"
                break

            if "no" in word.strip():
                results[0] = "Positive"
                break

        if results[0] is None:
            log.append("could not parse answer correctly in phase 1")
        else:
            print(results[0])

    except Exception as e:
        print("error1")
        log.append(f"error in phase 1: {e}")

    try:
        # Phase 2 -----------------------------------------------------------------------------------------------
        promptList = []
        promptList.append({"role": "system",
                           "content": "Is there an inconsistency between the following docstring and code? Answer first with Yes or No, then explain why."})
        promptList.append({"role": "user", "content": f"{full_code}"})

        answer = makeModelRequest(promptList, caller)

        log.append(f"question 2 - answer:\n{answer}")

        for word in answer.lower().split():
            if "yes" in word.strip():
                results[1] = "Positive"
                break

            if "no" in word.strip():
                results[1] = "Negative"
                break

        if results[1] is None:
            log.append("could not parse answer correctly in phase 2")
        else:
            print(results[1])

    except Exception as e:
        print("error2")
        log.append(f"error in phase 2: {e}")

    try:
        # Phase 3 -----------------------------------------------------------------------------------------------
        full_code = build_context(d, doc=True) + code + "\n}\n"

        log.append("started Phase 3:\nFull code:")
        promptList = []
        promptList.append({"role": "system",
                           "content": "You will get a snippet of a Java class. I want to know for a specific method if its code and documentation are consistent. Allways answer with Yes or No before you explain."})
        promptList.append({"role": "user",
                           "content": f"{full_code}\n\n\nAre code and documentation of {d['signature']['name']} consistent? The Documentation is {d['doc']}\n\n Answer with Yes or No?"})

        answer = makeModelRequest(promptList, caller)
        log.append(f"question 3 :\n{answer}")

        for word in answer.lower().split():
            if "yes" in word.strip():
                results[2] = "Negative"
                break

            if "no" in word.strip():
                results[2] = "Positive"
                break

        if results[2] is None:
            log.append("could not parse answer correctly in phase 3")
        else:
            print(results[2])

    except Exception as e:
        print("error3")
        log.append(f"error in phase 3: {e}")

    try:
        # Phase 4 -----------------------------------------------------------------------------------------------
        log.append("started Phase 4:\nFull code:")
        log.append(full_code)
        promptList = []
        promptList.append({"role": "system",
                           "content": "You will get a snippet of a Java class. I want to know for a specific method if there is an inconsistency between the documentation and the code. Allways answer with Yes or No before you explain."})
        promptList.append({"role": "user",
                           "content": f"{full_code}\n\n\n Is there an inconsistency between code and documentation of {d['signature']['name']}? The Documentation is {d['doc']}\n\n Answer with Yes or No?"})

        answer = makeModelRequest(promptList, caller)
        log.append(f"question 4 - answer: \n{answer}")

        for word in answer.lower().split():
            if "yes" in word.strip():
                results[3] = "Positive"
                break

            if "no" in word.strip():
                results[3] = "Negative"
                break

        if results[3] is None:
            log.append("could not parse answer correctly in phase 4")
        else:
            print(results[3])

    except Exception as e:
        print("error4")
        log.append(f"error in phase 4: {e}")

    # results output format is phase1 answer, phase2 answer, phase3 answer
    result_string = f"{results[0]}; {results[1]}; {results[2]}; {results[3]}"
    with open("result.txt", "w") as f:
        f.write(result_string)

    with open("log.txt", "w") as f:
        f.write("\n".join(log))
