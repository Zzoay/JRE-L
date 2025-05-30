# LLMs Meet Automatic Science Journalism
This repository contains implementation code on *JRE-L: Journalist, Reader, and Editor LLMs in the Loop for Science Journalism for the General Audience*, published in NAACL 2025.

## Requirements
The main environments are listed below, if there are other packages that need to be installed at runtime, just install them.
- Python 3.8+
- torch
- transformers
- vllm
- textstat

Furthermore, you should download the Qwen1.5-7B-Chat and Qwen1.5-1.8B-Chat from Huggingface or other platforms, and set or record their paths, which will be used in the following。

## Getting Started

### Downloading the data
Since the datasets are considerable in size, it is suggested to acquire them from the original source link. You can access the data via the provided link and proceed to extract it into the `data` folder.
- https://github.com/ronaldahmed/scitechnews
- https://github.com/TGoldsack1/Corpora_for_Lay_Summarisation

For prompting, you can only download the `test` directory.

### Running LLM services
Run the following command to start the LLM service
```bash
CUDA_VISIBLE_DEVICES={gpu_id} python -m vllm.entrypoints.openai.api_server \
    --model {model_name_or_path} \
    --gpu-memory-utilization 0.95 \
    --max-model-len 8192 \
    --port {port_for_call, eg. 8000} \
```
Typically, you should run three models and specify their ports.

### Config
Edit the configuration files (`config`) according to the data path and model path.

### Running prompting
Run the following command to start the prompting.

```bash
python run.py \
    --total-steps 3 \
    --batch-size 8 \
    --journalist_port 8000 \
    --reader_port 8001 \
    --editor_port 8002 \
```
where the journalist_port, reader_port, and editor_port should be the same as those models set in the service running.

## Citation
If you find our work useful, please cite our paper.
```tex
@inproceedings{jiang-etal-2025-jre,
    title = "JRE-L: Journalist, Reader, and Editor LLMs in the Loop for Science Journalism for the General Audience",
    author = "Jiang, Gongyao  and
      Shi, Xinran  and
      Luo, Qiong",
    editor = "Chiruzzo, Luis  and
      Ritter, Alan  and
      Wang, Lu",
    booktitle = "Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)",
    month = apr,
    year = "2025",
    address = "Albuquerque, New Mexico",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.naacl-long.335/",
    pages = "6579--6594",
    ISBN = "979-8-89176-189-6"
}
```
