
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '7'

import torch

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel, pipeline
from transformers.generation import GenerationConfig


model_name_or_path = "/data/gongyao/models/Llama-2-7b-chat-hf/"

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    device_map="auto",
    trust_remote_code=True,
    load_in_8bit=True,
    torch_dtype=torch.bfloat16,
).eval()

generation_config = GenerationConfig.from_pretrained(model_name_or_path)
pipe = pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.bfloat16,
    device_map='auto',
    max_length=2048,
    temperature=1.0,
    top_p=0.8,
    repetition_penalty=1.15,
    tokenizer=tokenizer,
    generation_config=generation_config,
)


app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    input_text = request.json['text']
    
    output_text = pipe(input_text)[0]['generated_text']
    
    return jsonify({'output_text': output_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, ssl_context="adhoc")