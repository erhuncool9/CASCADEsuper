
echo "build CASCADE venv"

python3.11 -m venv venv-cascade

# install it:

./venv-cascade/bin/pip install ..



echo "build DocChecker venv"

python3.11 -m venv venv-DocChecker
./venv-DocChecker/bin/pip install torch transformers gdown codetext tree_sitter_languages tree_sitter==0.20.4

   
echo "build C4RLLaMA venv"

python3.11 -m venv venv-C4RLLaMA
./venv-C4RLLaMA/bin/pip install -r ./drivers/C4RLLaMA/requirements.txt

echo "you have to download the retrained DocChecker model https://figshare.com/s/981c2fbe830b905b01a9 and put it in /drivers/DocChecker/pretrained_model"
echo "you have to download the retrained C4RLLaMA weights https://figshare.com/s/812541da6a1f33025f69 and put them in /drivers/C4RLLaMA/weights"
