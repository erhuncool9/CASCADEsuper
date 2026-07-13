import os
import nvitop
import time
import sys
import fire
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import json
from tqdm import tqdm
from utils.prompter import Prompter
from sklearn.metrics import recall_score, precision_score, accuracy_score
import re


def build_signature(method_context, doc=False):
    doc_string = method_context["doc"] if doc else ""
    ctsig = method_context["signature"]

    return doc_string + (" ".join(ctsig["modifier"]) + " " + ('<' + ', '.join(ctsig["generics"]) + '> ' if ctsig["generics"] else '') +
           ctsig["returns"] + " " + ctsig["name"] + "(" + ", ".join(ctsig["params"]) + ")" +
           (" throws " + ", ".join(ctsig["exceptions"]) if ctsig.get("exceptions") else ""))


if torch.cuda.is_available():
    device = "cuda"
    print("cuda")
else:
    device = "cpu"


post_instruction = """Is the given code consistent with the corresponding {}?
```code
{}
```
```{}
{}
```
"""

def main(
    base_model: str = '/nvme1n1/LLM/CodeLlama-13b-hf',
    lora_weights: str = "",
    prompt_template: str = "llama",
):
    print("base_model", base_model)
    print("lora", lora_weights)
    

    base_model = base_model or os.environ.get("BASE_MODEL", "")
    assert (
        base_model
    ), "Please specify a --base_model, e.g. --base_model='huggyllama/llama-7b'"

    prompter = Prompter(prompt_template)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base_model, low_cpu_mem_usage=True
        )


    model.config.pad_token_id = tokenizer.pad_token_id = 0

    model.eval()
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)
    

    @torch.inference_mode()
    def evaluate(
        model,
        instruction,
        input=None,
        top_p=0.95,
        top_k=50,
        num_beams=1,
        max_new_tokens=512,
        **kwargs,
    ):
        prompt = prompter.generate_prompt(instruction, input)
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)

        with torch.no_grad():
            generation_output = model.generate(
                input_ids=input_ids,
                do_sample=True,
                top_p=top_p,
                top_k=top_k,
                num_beams=num_beams,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
            )
        s = generation_output.sequences[0]
        output = tokenizer.decode(s)
        res = prompter.get_response(output)

        return res

    try:
        with open("./analyzed.json") as f:
            data = json.load(f)
       

        sample = data[0]
        print("testing:" , sample["signature"]["name"] )
        
        full_code = build_signature(sample) + " " + sample["code"]
    
        instruction = post_instruction.format("docstring", full_code, "docstring", sample["doc"])
    
        with open("./log.txt", "a") as log:
            log.write("instruction:\n")
            log.write(str(instruction))

        print("evaluating...")
        res = evaluate(model, instruction)
        

        with open("./log.txt" , "a") as log:
            log.write("result:\n")
            log.write(res)


        judge = 1 if "inconsisten" in res else 0
        prediction = "Positive" if judge == 1 else "Negative"
        

        print("evaluated to: ", prediction)


        result = prediction

        print(result)

        with open("./result.txt", "w") as f:
            f.write(result)

    except Exception as e:
        with open("./log.txt" , "a") as log:
            log.write("Error:\n")
            log.write(str(e))


if __name__ == "__main__":
    fire.Fire(main)


