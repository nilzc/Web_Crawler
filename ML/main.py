from data_prepare import QREL
from sklearn import linear_model
import random
import pandas as pd
import numpy as np


class Model:

    def __init__(self):
        self.qrel = QREL()
        self.query_ids = set()
        self.test_fold = []
        self.train_query = []

        self.initialize()

    def initialize(self):
        self.query_ids = set(self.qrel.df["query"])
        self.test_fold.append(random.sample(self.query_ids, 5))
        remain = self.query_ids.difference(set(self.test_fold[0]))
        self.test_fold.append(random.sample(remain, 5))
        remain = remain.difference(set(self.test_fold[1]))
        self.test_fold.append(random.sample(remain, 5))
        remain = remain.difference(set(self.test_fold[2]))
        self.test_fold.append(random.sample(remain, 5))
        remain = remain.difference(set(self.test_fold[3]))
        self.test_fold.append(random.sample(remain, 5))
        #
        # self.test_set = self.qrel.df[self.qrel.df["query"].isin(self.test_query)].copy()
        # self.train_set = self.qrel.df[self.qrel.df["query"].isin(self.train_query)].copy()

    def train(self):
        loop = 0
        while loop < 5:
            test_query = self.test_fold[loop]
            train_query = list(self.query_ids.difference(set(test_query)))
            test_set = self.qrel.df[self.qrel.df["query"].isin(test_query)].copy()
            train_set = self.qrel.df[self.qrel.df["query"].isin(train_query)].copy()

            reg = linear_model.LinearRegression()
            reg.fit(train_set.iloc[:, 2:-1], train_set.iloc[:, -1])
            test_predict = reg.predict(test_set.iloc[:, 2:-1])
            train_predict = reg.predict(train_set.iloc[:, 2:-1])
            test_set["predict"] = test_predict
            train_set["predict"] = train_predict

            self.output_test(test_query, test_set, loop)
            self.output_train(train_query, train_set, loop)

            loop += 1

    def output_test(self, query, test_set, version):
        with open("./output/test_{}.txt".format(version), "a") as f:
            for q_id in query:
                for idx, row in test_set[test_set["query"] == q_id].sort_values(by="predict", ascending=False).iterrows():
                    line = "{} Q0 {} 1 {} Exp\n".format(row["query"], row["doc"], row["es"])
                    f.write(line)

    def output_train(self, query, train_set, version):
        with open("./output/train_{}.txt".format(str(version)), "a") as f:
            for q_id in query:
                for idx, row in train_set[train_set["query"] == q_id].sort_values(by="predict", ascending=False).iterrows():
                    line = "{} Q0 {} 1 {} Exp\n".format(row["query"], row["doc"], row["es"])
                    f.write(line)


my_model = Model()
my_model.train()

# my_model.output_test()
# my_model.output_train()
