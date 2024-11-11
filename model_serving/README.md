# Serving llm model on Marenostrum using ollama

## Preparing on the Marenostrum

Before running the model it is needed to install the dependencies and downloading the models before connecting to an ACC node.

1. Connect to transfer3.bsc.es
```bash
ssh transfer3.bsc.es
```
2. copy your local git folder to your userfolder on Marenostrum
```bash
scp git ./$FOLDER
```
Once theses steps are done, you can log out from the `transfer3.bsc.es` node and connect to the ACC node `alogin4.bsc.es`

3. Install libraries
To install the library and activate the virtuanl env
```bash
cd ./$FOLDER
module purge
module load mkl intel impi hdf5 python cuda/12.1 ollama # Cuda 12.1 is the last version supported by vllm 
python3.12 -m venv venv_mn5
source venv/bin/activate
pip install -U openai pandas
```
Alternatively to installing packages manually
```bash
pip install -U -r requirements.txt
```

4. Dataset preparation

The data are not in the github repository. You need to copy your local data in the data folder.

### Activate environment

1. Activate the environment
```bash
module purge &&
module load  mkl/2024.0 nvidia-hpc-sdk/23.11-cuda11.8 openblas/0.3.27-gcc cudnn/9.0.0-cuda11 tensorrt/10.0.0-cuda11 impi/2021.11 hdf5/1.14.1-2-gcc gcc/11.4.0 python/3.11.5-gcc nccl/2.19.4 pytorch
source venv_mn5/bin/activate
```

### Preparing the model before running the node
```bash
module load mkl intel impi hdf5 python cuda/12.1 ollama
```

Starting ollama with env variables to ensure the right folder being used 
```bash
export OLLAMA_NUM_PARALLEL=100
export OLLAMA_TMPDIR=/gpfs/projects/bsc02/llm_models/ollama/tmp
export OLLAMA_MODELS=/gpfs/projects/bsc02/llm_models/ollama/models
ollama serve &
```

Run the creation of several identical models to ensure we can run them concurrently because it is not supported to spam the same model several time (see [https://github.com/ollama/ollama/pull/3418#issuecomment-2138044209](https://github.com/ollama/ollama/pull/3418#issuecomment-2138044209)).
So a workaround is to create several identical model with a ModelFile but with different names.  
[> [!NOTE]] Not sure it works at intented need further test

1. Need to pull the model into the folder
```bash
MODEL_NAME="llama3.2"
OLLAMA_TMPDIR=/gpfs/projects/bsc02/llm_models/ollama/tmp OLLAMA_MODELS=/gpfs/projects/bsc02/llm_models/ollama/models ollama pull $MODEL_NAME
```

2. Create a Modelfile
```bash
cd /gpfs/projects/bsc02/sla_projects/BioHackathonEU-2024/model_serving
echo -e "FROM  llama3.2\nPARAMETER temperature 1 \n PARAMETER num_ctx 2048" > Modelfile
```

3. Create the model
```bash
olllama create $MODEL_NAME_1 -f ./ModelFile
olllama cp $MODEL_NAME_1 -f $MODEL_NAME_2
```


## Run the script

1. Init a interactive job
```bash
salloc -A bsc02 -t 01:00:00 -q acc_debug -n 1 -c 80 --gres=gpu:4
```
2. cd into the folder
```bash
cd /gpfs/projects/bsc02/sla_projects/BioHackathonEU-2024/
```

3. Load the modules
```bash
module purge
module load mkl intel impi hdf5 python cuda/12.1 ollama 
source venv_mn5/bin/activate
```
4. Starting the ollama server 
```bash
export OLLAMA_NUM_PARALLEL=100
export OLLAMA_TMPDIR=/gpfs/projects/bsc02/llm_models/ollama/tmp
export OLLAMA_MODELS=/gpfs/projects/bsc02/llm_models/ollama/models
ollama serve &
```
6. Run the script
```bash
python code/retrieve_gender.py -m llama3.2 -d data/1312_splitnames.csv
```
