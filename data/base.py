# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
from torch.utils.data import Dataset, DataLoader
from .utils import load_data



class TransformerXHDataset(Dataset):
    def __init__(self, json_obj, config_model, isTrain=False, bert_tokenizer=None):
        self.config_model = config_model
        self.bert_tokenizer = bert_tokenizer
        self.istrain = isTrain
        # self.data = load_data(json_obj, isTrain)
        self.data = json_obj
        self.len = len(self.data)

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        return 
