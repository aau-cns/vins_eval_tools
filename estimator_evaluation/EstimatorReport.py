#!/usr/bin/env python
# Copyright (C) 2021, Roland Jung, Control of Networked Systems, University of Klagenfurt, Austria.
#
# All rights reserved.
#
# This software is licensed under the terms of the BSD-2-Clause-License with
# no commercial use allowed, the full terms of which are made available in the
# LICENSE file. No license in patents is granted.
#
# You can contact the author at <roland.jung@aau.at>
#
# Requirements:
# pandas, argparse, spatial_csv_formats, rosbag2csv, script_utils, trajectory_evaluation
########################################################################################################################
import os
import pandas as pandas
import numpy as numpy
import copy
from sys import version_info


class EstimatorReport:
    data_frame = None

    def __init__(self):
        self.data_frame = pandas.DataFrame(columns=EstimatorReport.get_column_format())
        pass

    def append_row(self, attr_val, lvl_val, run_val, est_val, armse_p, armse_q, anees_p, anees_q):
        df = pandas.DataFrame([[attr_val, lvl_val, run_val, est_val, armse_p, armse_q, anees_p, anees_q]],
                              columns=EstimatorReport.get_column_format())
        # print(df)
        self.data_frame = self.data_frame.append(df)

    def save(self, fn, save_index=False):
        EstimatorReport.save_data_frame(data_frame=self.data_frame, fn=fn,
                                        fmt=EstimatorReport.get_column_format(), save_index=save_index)

    def load(self, fn):
        self.data_frame = EstimatorReport.load_data_frame(fn=fn, fmt=EstimatorReport.get_column_format())

    def get_attr_num(self):
        return self.get_num('attr')

    def get_lvl_num(self):
        return self.get_num('lvl')

    def get_run_num(self):
        return self.get_num('run')

    def get_est_num(self):
        return self.get_num('est')

    def get_attr_values(self):
        return self.get_unique_values('attr')

    def get_lvl_values(self):
        return self.get_unique_values('lvl')

    def get_run_values(self):
        return self.get_unique_values('run')

    def get_est_values(self):
        return self.get_unique_values('est')

    def get_unique_values(self, column):
        if self.data_frame is not None:
            df_attr = self.data_frame.get([column])
            if version_info[0] < 3:
                return numpy.unique(df_attr.values)
            else:
                return numpy.unique(df_attr.to_numpy())

        else:
            return []

    def get_num(self, column):
        return self.get_unique_values(column).size

    @staticmethod
    def get_column_format():
        return ['attr', 'lvl', 'run', 'est', 'armse_p', 'armse_q', 'anees_p', 'anees_q']

    @staticmethod
    def load_data_frame(fn, fmt):
        header = fmt

        data = pandas.read_csv(fn, sep='\s+|\,', comment='#', header=None, names=header,
                               engine='python')
        return data

    @staticmethod
    def save_data_frame(data_frame, fn, fmt, save_index=False):
        head = os.path.dirname(os.path.abspath(fn))
        if not os.path.exists(head):
            os.makedirs(head)
        # list.copy() does not exist prior python 3.3
        header = copy.deepcopy(fmt)
        if not save_index:
            header[0] = '#' + header[0]  # add comment

        df = data_frame.reset_index()
        df.to_csv(fn, sep=',', index=save_index, index_label='#idx',
                  header=header, columns=fmt)
        pass


########################################################################################################################
#################################################### T E S T ###########################################################
########################################################################################################################
import unittest


class EstimatorReport_Test(unittest.TestCase):
    def test_init(self):
        report = EstimatorReport()

        report.append_row(attr_val=1, lvl_val=1, run_val=1, est_val=1, armse_p=1.52, armse_q=1.33, anees_p=13.01,
                          anees_q=4.34)
        report.append_row(attr_val=1, lvl_val=1, run_val=1, est_val=2, armse_p=2.52, armse_q=2.33, anees_p=23.01,
                          anees_q=24.34)
        report.append_row(attr_val=1, lvl_val=1, run_val=1, est_val=3, armse_p=0.52, armse_q=20.33, anees_p=13.01,
                          anees_q=1.34)

        report.save("./sample_data/example_eval.csv")
        print(report.data_frame)
        r2 = EstimatorReport()
        r2.load("./sample_data/example_eval.csv")
        print(r2.data_frame)

    def test_get_info(self):
        report = EstimatorReport()
        report.load("./sample_data/EVAL/eval.csv")
        print("attributes: \n\t" + str(report.get_attr_values()))
        print("level: \n\t" + str(report.get_lvl_values()))
        print("run: \n\t" + str(report.get_run_values()))
        print("estimators: \n\t" + str(report.get_est_values()))


if __name__ == "__main__":
    unittest.main()
