#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.

import random
import pandas as pd
from os import path

from model import SimpleSeq2seq


class Seq2seqExperiment(object):
    default_ranges = {
        'cell_type': ('LSTM', 'GRU'),
        'cell_size': (16, 32, 64, 128, 256, 512),
        'embedding_size': tuple(range(1, 30)),
    }
    def __init__(self, dataset, result_fn, custom_pranges=None):
        self.dataset = dataset
        self.result_fn = result_fn
        self.custom_pranges = custom_pranges
        self.result = {}

    def create_model(self):
        conf = Seq2seqExperiment.generate_config(self.custom_pranges)
        self.model = SimpleSeq2seq(conf['cell_type'], conf['cell_size'],
                                   conf['embedding_size'])
        self.model.create_model(self.dataset)
        self.conf = conf
        print(conf)
        
    def to_dict(self):
        d = {}
        for param, val in self.conf.items():
            d['conf.{}'.format(param)] = val
        for param, val in self.model.result.items():
            d['result.{}'.format(param)] = val
        for param, val in self.dataset.to_dict().items():
            d['data.{}'.format(param)] = val
        return d

    def run(self, save=True):
        self.create_model()
        self.model.train_and_test(self.dataset, batch_size=1000)
        if save:
            self.save()

    def save(self):
        d = self.to_dict()
        if not path.exists(self.result_fn):
            df = pd.DataFrame(columns=d.keys())
        else:
            df = pd.read_table(self.result_fn)
        df = df.append(d, ignore_index=True)
        df.sort_index(axis=1).to_csv(self.result_fn, sep='\t', index=False)

    @staticmethod
    def generate_config(ranges=None):
        if ranges is not None:
            r = Seq2seqExperiment.default_ranges.copy()
            r.update(ranges)
        else:
            r = Seq2seqExperiment.default_ranges
        conf = {}
        for param, prange in r.items():
            conf[param] = random.choice(prange)
        return conf

