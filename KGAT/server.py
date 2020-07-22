import random, os
import argparse
import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F
from tqdm import tqdm
from torch.autograd import Variable
from pytorch_pretrained_bert.tokenization import whitespace_tokenize, BasicTokenizer, BertTokenizer

from data_loader import DataLoaderTest
from bert_model import BertForSequenceEncoder
from pytorch_pretrained_bert.optimization import BertAdam
import logging
import json
import random, os
import argparse
import numpy as np
from models import inference_model

from flask_socketio import SocketIO, send
from flask import Flask, Response

app = Flask(__name__)
logger = logging.getLogger(__name__)

def input():
  evi_list = []
  global claim
  evidences = ["the Earth is roughly a sphere.", "The Earth is an irregularly shaped ellipsoid."]
  claim = "Earth is round"
  for evi in evidences: 
    evi_list.append(["placeholder", 1, evi, 0])

  print(evi_list)

  dictionary ={ 
      "id" : 98, 
      "evidence" : evi_list,
      "claim" : claim
  }

  json_object = json.dumps(dictionary)

  with open("/content/KernelGAT/data/bert_test_1.json", "w") as outfile: 
      outfile.write(json_object)

def eval_model(model, label_list, validset_reader, outdir, name):
    outpath = outdir + name

    with open(outpath, "w") as f:
        for index, data in enumerate(validset_reader):
            inputs, ids = data
            logits = model(inputs)
            preds = logits.max(1)[1].tolist()
            assert len(preds) == len(ids)
            for step in range(len(preds)):
                instance = {"id": ids[step], "predicted_label": label_list[preds[step]]}
                f.write(json.dumps(instance) + "\n")

def get_results_kgat():
  results_path = "/content/KernelGAT/outputtest_1.json"
  with open(results_path, "w") as f:
        for index, data in enumerate(validset_reader):
            inputs, ids = data
            logits = model(inputs)
            preds = logits.max(1)[1].tolist()
            assert len(preds) == len(ids)
            for step in range(len(preds)):
              print("ID: ", ids[step])
              print("Claim: ", claim)
              print("Prediction: ", label_list[preds[step]])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_path', help='train path', default='bert_test_1.json')
    parser.add_argument('--name', help='train path', default='output.json')
    parser.add_argument('--test_origin_path', help='train path')
    parser.add_argument("--batch_size", default=4, type=int, help="Total batch size for training.")
    parser.add_argument('--outdir', required=False, default='EnFVe/KGAT/output_new')
    parser.add_argument('--bert_pretrain', required=False, default='EnFVe/KGAT/bert_base')
    parser.add_argument('--checkpoint', required=False, default='EnFVe/KGAT/model.best.pt')
    parser.add_argument('--dropout', type=float, default=0.6, help='Dropout.')
    parser.add_argument('--no-cuda', action='store_true', default=False, help='Disables CUDA training.')
    parser.add_argument("--bert_hidden_dim", default=768, type=int, help="Total batch size for training.")
    parser.add_argument("--layer", type=int, default=1, help='Graph Layer.')
    parser.add_argument("--num_labels", type=int, default=3)
    parser.add_argument("--kernel", type=int, default=21, help='Evidence num.')
    parser.add_argument("--evi_num", type=int, default=5, help='Evidence num.')
    parser.add_argument("--threshold", type=float, default=0.0, help='Evidence num.')
    parser.add_argument("--max_len", default=130, type=int,
                        help="The maximum total input sequence length after WordPiece tokenization. Sequences "
                             "longer than this will be truncated, and sequences shorter than this will be padded.")




    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    args.cuda = not args.no_cuda and torch.cuda.is_available()
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%d-%m-%Y %H:%M:%S')
    logger.info(args)
    logger.info('Start testing!')

    label_map = {'SUPPORTS': 0, 'REFUTES': 1, 'NOT ENOUGH INFO': 2}
    label_list = ['SUPPORTS', 'REFUTES', 'NOT ENOUGH INFO']
    args.num_labels = len(label_map)
    tokenizer = BertTokenizer.from_pretrained(args.bert_pretrain, do_lower_case=False)
    logger.info("loading validation set")
    input()
    validset_reader = DataLoaderTest(args.test_path, label_map, tokenizer, args, batch_size=args.batch_size)
    logger.info('initializing estimator model')
    bert_model = BertForSequenceEncoder.from_pretrained(args.bert_pretrain)
    bert_model = bert_model.cuda()
    bert_model.eval()
    model = inference_model(bert_model, args)
    model.load_state_dict(torch.load(args.checkpoint)['model'])
    model = model.cuda()
    model.eval()
    eval_model(model, label_list, validset_reader, args.outdir, args.name)
    model.eval()
    print("\n")
    get_results_kgat()

@app.route('/', methods=['GET', 'POST'])
'''
def answer():
    claim = request.json['claim']
    evidences = request.json['evidences']
    argmax, evidences, vals = get_results_gear(claim, evidences)

    return Response(
                json.dumps({
                    'argmax': argmax,
                    'evidences': evidences,
                    'vals': vals,
                }),
                mimetype='application/json',
                headers={
                    'Cache-Control': 'no-cache',
                    'Access-Control-Allow-Origin': '*'
                }
            )
'''

app.run(
        host='0.0.0.0',
        port=14000,
        debug=False,
        threaded=True
    )
