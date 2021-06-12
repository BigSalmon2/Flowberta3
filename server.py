import numpy as np
import os
import io

# import for server
from flask import Flask, render_template, request, Response, send_file, jsonify
from queue import Queue, Empty
import threading
import time

# import for model
from transformers import AutoTokenizer, AutoModelWithLMHead, top_k_top_p_filtering, AutoModelForMaskedLM
from torch.nn import functional as F
import torch
import time

# flask server
app = Flask(__name__)

# static variables
huggingtweets = "ok"
model_names = ['BigSalmon/Flowberta']
tokenizers = dict()
models = dict()

# change cpu to gpu so that model can use gpu (because default type is cpu)
device = torch.device('cpu')

# model loading
for model_name in model_names:
    tokenizers[model_name] = AutoTokenizer.from_pretrained(
        model_name)
    models[model_name] = AutoModelForMaskedLM.from_pretrained(
        model_name, return_dict=True)
    models[model_name].to(device)
    print(f'{model_name} model loadeding complete..')
 
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("roberta-base")
model = AutoModelForMaskedLM.from_pretrained("BigSalmon/Flowberta")

# request queue setting
requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

# static variable

# request handling


def handle_requests_by_batch():
    try:
        while True:
            requests_batch = []
            while not (len(requests_batch) >= BATCH_SIZE):
                try:
                    requests_batch.append(
                        requests_queue.get(timeout=CHECK_INTERVAL))
                except Empty:
                    continue

            batch_outputs = []
            for request in requests_batch:
                batch_outputs.append(run_model(
                    request["input"][0], request["input"][1], request["input"][2], request["input"][3]))

            for request, output in zip(requests_batch, batch_outputs):
                request["output"] = output

    except Exception as e:
        while not requests_queue.empty():
            requests_queue.get()
        print(e)


# request processing
threading.Thread(target=handle_requests_by_batch).start()

# run model


def run_model(prompt, num, length, model_name):
    try:
      sentence = prompt.strip()
      model = models[model_name]
      tokenizer = tokenizers[model_name]
      token_ids = tokenizer.encode(sentence, return_tensors='pt')
      token_ids_tk = tokenizer.tokenize(sentence, return_tensors='pt')
      masked_position = (token_ids.squeeze() == tokenizer.mask_token_id).nonzero()
      masked_pos = [mask.item() for mask in masked_position ]
      with torch.no_grad():
        output = model(token_ids)
        last_hidden_state = output[0].squeeze()
        list_of_list =[]
      for mask_index in masked_pos:
        mask_hidden_state = last_hidden_state[mask_index]
        idx = torch.topk(mask_hidden_state, k=30, dim=0)[1]
        words = [tokenizer.decode(i.item()).strip() for i in idx]
        list_of_list.append(words)
      return list_of_list

    except Exception as e:
        print(e)
        return 500

# routing


@app.route("/gpt2-story", methods=['POST'])
def generation():
    try:
        # only get one request at a time
        if requests_queue.qsize() > BATCH_SIZE:
            return jsonify({'message': 'TooManyReqeusts'}), 429

        try:
            args = []

            model_name = str(request.form['model'])
            if model_name not in model_names:
                return jsonify({'message': 'Error! There is no model'}), 400
            model_name = "BigSalmon/Flowberta
            prompt = str(request.form['text'])
            num = int(str(request.form['num_samples']))
            length = int(str(request.form['length']))

            args.append(prompt)
            args.append(num)
            args.append(length)
            args.append(model_name)

        except Exception:
            return jsonify({'message': 'Error! Can not read args from request'}), 500

        # put data to request_queue
        req = {'input': args}
        requests_queue.put(req)

        # wait output
        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)

        # send output
        generated_text = req['output']

        if generated_text == 500:
            return jsonify({'message': 'Error! An unknown error occurred on the server'}), 500

        result = jsonify(generated_text)

        return result

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error! Unable to process request'}), 400


@app.route('/healthz')
def health():
    return "ok", 200


@app.route('/')
def main():
    return "ok", 200


if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=80)
