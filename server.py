from flask import Flask, request, Response, jsonify

import json 
import time
import threading
from queue import Queue, Empty

import torch
from torch.nn import functional as F
from transformers import AutoModelWithLMHead


app = Flask(__name__)

requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

model = AutoModelWithLMHead.from_pretrained("pranavpsv/gpt2-genre-story-generator", return_dict=True)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue

            for requests in requests_batch:
                requests['output'] = run_generate(requests['input'][0], requests['input'][1], requests['input'][2])


threading.Thread(target=handle_requests_by_batch).start()

def run_generate(input_ids, num_samples, length):
    inputs = []

    for input_id in input_ids:
        inputs.append(int(input_id))

    token_tensor = torch.LongTensor([inputs]).to(device)

    outputs = model.generate(
        token_tensor,
        pad_token_id=50256,
        max_length=length,
        min_length=length,
        do_sample=True,
        top_k=50,
        num_return_sequences=num_samples,
    )

    outputs = str(outputs.tolist())

    return outputs

@app.route("/gpt2-story", methods=["POST"])
def gpt2():

    # 큐에 쌓여있을 경우,
    if requests_queue.qsize() > BATCH_SIZE:
        return jsonify({'error': 'TooManyReqeusts'}), 429

    data = request.json

    try:
        args= [] 
        args.append(data['text'])
        args.append(data['num_samples'])
        args.append(data['length'])
    except Exception:
        return jsonify({'error':'Invalid Inputs'}), 400
    
    req = {
        'input': args
    }
    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)
    
    result = req['output']

    return result

@app.route('/healthz')
def health():
    return "ok", 200

@app.route('/')
def main():
    return "USE API", 200

if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=80)