
import os
import torch
from .model import Seq2Seq
from transformers import (RobertaConfig, RobertaModel, RobertaTokenizer)
import torch.nn as nn
import gdown 

class DocCheckerNet(nn.Module):

    def __init__(self):
        super().__init__()
        self.tokenizer = RobertaTokenizer.from_pretrained('microsoft/unixcoder-base')
        self.config = RobertaConfig.from_pretrained('microsoft/unixcoder-base')
        self.config.is_decoder = True
        encoder = RobertaModel.from_pretrained('microsoft/unixcoder-base',config=self.config) 

        self.tokenizer.add_tokens(["<REPLACE_OLD>", '<REPLACE_NEW>', "<REPLACE_END>", "<KEEP>","<KEEP_END>", "<INSERT_END>", "<DELETE_END>",
                                "<INSERT>", "<DELETE>","<INSERT_OLD_KEEP_BEFORE>", "<INSERT_NEW_KEEP_BEFORE>"],special_tokens=True)
        self.config.vocab_size = len(self.tokenizer)
        encoder.resize_token_embeddings(len(self.tokenizer))


        model = Seq2Seq(encoder=encoder,decoder=encoder,config=self.config,
                    sos_id=self.tokenizer.convert_tokens_to_ids(["<mask0>"])[0],eos_id=self.tokenizer.sep_token_id)
        self.model = model
        
        if os.path.exists('./pretrained_model/') is False:
            os.makedirs('./pretrained_model/')
            url = "https://drive.google.com/file/d/1-9VrBkLm6U2WUu1NFxkydAIUN2-qvFQq/view?usp=sharing"
            gdown.download(url, './pretrained_model/', quiet=False, fuzzy=True)

        output_dir = './pretrained_model/pytorch_model.bin'
        model_to_load = self.model.module if hasattr(self.model, 'module') else self.model  
        model_to_load.load_state_dict(torch.load(output_dir,map_location='cuda:0')  )
        #model_to_load.load_state_dict(torch.load(output_dir, map_location=torch.device('cpu')))
        self.model.eval()

    def tokenize(self, code, docstring, max_sou_length=200, max_tar_length=32):
        source_tokens = self.tokenizer.tokenize(code)[:max_sou_length-5]
        source_tokens = [self.tokenizer.cls_token, "<encoder-decoder>",
                            self.tokenizer.sep_token, "<mask0>"]+source_tokens+[self.tokenizer.sep_token]
        source_ids = self.tokenizer.convert_tokens_to_ids(source_tokens)
        padding_length = max_sou_length - len(source_ids)
        source_ids += [self.tokenizer.pad_token_id]*padding_length
        source_ids = torch.tensor(
            source_ids, dtype=torch.long)

        target_tokens = self.tokenizer.tokenize(docstring)[:max_tar_length-2]
        target_tokens = ["<mask0>"] + target_tokens + [self.tokenizer.sep_token]
        target_ids = self.tokenizer.convert_tokens_to_ids(target_tokens)
        padding_length = max_tar_length - len(target_ids)
        target_ids += [self.tokenizer.pad_token_id] * padding_length
        target_ids = torch.tensor(target_ids, dtype=torch.long)
        return source_ids, target_ids
    

    def inference(self, code, docstring):
        """
        inference file
        """
        code_ids, docstring_ids = self.tokenize(code, docstring)
        
        with torch.no_grad():
            output_label, pred_text = self.model(code_ids,target_ids=docstring_ids, stage='inference')   
            output_label = output_label[0]
        print('-----------------')
        if output_label == 0:
            print("Inconsistent!")
            pred_text = pred_text[0]
            t = pred_text[0].cpu().numpy()
            t = list(t)
            if 0 in t:
                t = t[:t.index(0)]
            output_text = self.tokenizer.decode(t,clean_up_tokenization_spaces=False)
            print("Recommended docstring: ", output_text)
        else:
            print("Consistent!")

if __name__ == "__main__":
    model = DocCheckerNet()
    code= "def aspect(self):\n        \"\"\"Control the mapping from domains to ranges.\n\n        By default, each axis maps its domain to its range separately, which is\n        what is usually expected from a plot.  Sometimes, both axes have the same\n        domain.  In this case, it is desirable that both axes are mapped to a consistent\n        range to avoid \"squashing\" or \"stretching\" the data.  To do so, set `aspect`\n        to \"fit-range\".\n        \"\"\"\n        return self._aspect"
    docstring= "False"
    model.inference(code, docstring)

