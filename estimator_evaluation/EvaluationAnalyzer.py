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
import time
import pandas as pandas
import numpy as numpy
import argparse
from cnspy_numpy_utils.numpy_statistics import numpy_statistics
from sys import version_info
import matplotlib.pyplot as plt

from estimator_evaluation.EstimatorReport import EstimatorReport


class AnalyzerPlotConfig:
    dpi = 200
    title = ""
    scale = 1.0
    save_fn = ""
    result_dir = "."
    show = True
    close_figure = False

    def __init__(self, dpi=200, title="",
                 scale=1.0, save_fn="", result_dir=".", show=True, close_figure=False):
        self.dpi = dpi
        self.title = title
        self.scale = scale
        self.save_fn = save_fn
        self.result_dir = result_dir
        self.show = show
        self.close_figure = close_figure

    @staticmethod
    def show_save_figure(cfg, fig):
        plt.draw()
        plt.pause(0.001)
        if cfg.save_fn:
            filename = os.path.join(cfg.result_dir, cfg.save_fn)
            print("save to file: " + filename)
            plt.savefig(filename, dpi=int(cfg.dpi))
        if cfg.show:
            fig.tight_layout(pad=1.1)
            plt.show()
        if cfg.close_figure:
            plt.close(fig)


class EvaluationAnalyzer:
    est_report = EstimatorReport()  # table holds: attr, lvl, run, est, armse_p, armse_q, anees_p, anees_q
    data_frame_analyzer = None  # table holds: attr, lvl, run, est, aarmse_p, aarmse_q, aanees_p, aanees_q

    # private data member that define the thresholds
    rmse_p_th = 0
    rmse_q_th = 0

    def __init__(self, fn, rmse_p_th=0, rmse_q_th=0):
        self.est_report.load(fn)
        self.data_frame_analyzer = pandas.DataFrame(columns=EvaluationAnalyzer.get_column_format())
        self.rmse_p_th = rmse_p_th
        self.rmse_q_th = rmse_q_th
        self.data_frame_analyzer = self.compute_statistics()

    def get_dataframe_at(self, attr, lvl, est=None):
        if est is None:
            df = self.est_report.data_frame
            df = df.loc[df['attr'] == attr]
            return df.loc[df['lvl'] == lvl]
        else:
            df = self.est_report.data_frame
            df = df.loc[df['attr'] == attr]
            df = df.loc[df['lvl'] == lvl]
            return df.loc[df['est'] == est]

    # def boxplot_at(self, attr, lvl, est=None):
    #     df = self.get_dataframe_at(attr, lvl, est)
    #     fig, ax = plt.subplots()
    #     boxplot = df.boxplot(ax=ax, column=['armse_p', 'armse_q', 'anees_p', 'anees_q'])
    #     plt.show()

    def boxplot_at(self, attr, lvl, fig=None, cfg=AnalyzerPlotConfig()):
        if fig is None:
            fig = plt.figure(figsize=(20, 15), dpi=int(cfg.dpi))

        df = self.get_dataframe_at(attr, lvl)
        if not df.empty:
            df.boxplot(ax=fig.add_subplot(2, 2, 1), column=['armse_p'], by='est', showmeans=True, meanline=True)
            df.boxplot(ax=fig.add_subplot(2, 2, 2), column=['armse_q'], by='est', showmeans=True, meanline=True)
            df.boxplot(ax=fig.add_subplot(2, 2, 3), column=['anees_p'], by='est', showmeans=True, meanline=True)
            df.boxplot(ax=fig.add_subplot(2, 2, 4), column=['anees_q'], by='est', showmeans=True, meanline=True)

            cfg.title = "Attr:{0}, Lvl:{1}".format(attr, lvl)
            fig.suptitle(cfg.title, fontsize=16)
            AnalyzerPlotConfig.show_save_figure(cfg, fig)

    # TODO: do what ever here!
    def compute_average_over_runs(self, attr, lvl, est):
        df = self.get_dataframe_at(attr, lvl, est)

        df_res = df
        # print(df)
        df_res['aarmse_p'] = df['armse_p'].mean()
        df_res['aarmse_q'] = df['armse_q'].mean()
        df_res['aanees_p'] = df['anees_p'].mean()
        df_res['aanees_q'] = df['anees_q'].mean()
        return df_res.sort_values(by=['run'])

    def compute_statistics_over_runs(self, attr, lvl, est):
        df = self.get_dataframe_at(attr, lvl, est)
        if df.empty:
            return pandas.DataFrame()

        dict_ale = {'attr': attr, 'lvl': lvl, 'est': est}
        df_ale = pandas.DataFrame.from_dict(dict_ale, orient='index').T
        # print(df_ale)

        # get normalized dataframe
        armse_p_norm = {'armse_p': df['armse_p'].values / numpy.max(df['armse_p'].values)}
        df_armse_p_norm = pandas.DataFrame.from_dict(armse_p_norm, orient='index').T
        armse_q_norm = {'armse_q': df['armse_q'].values / numpy.max(df['armse_q'].values)}
        df_armse_q_norm = pandas.DataFrame.from_dict(armse_q_norm, orient='index').T
        anees_p_norm = {'anees_p': df['anees_p'].values / numpy.max(df['anees_p'].values)}
        df_anees_p_norm = pandas.DataFrame.from_dict(anees_p_norm, orient='index').T
        anees_q_norm = {'anees_q': df['anees_q'].values / numpy.max(df['anees_q'].values)}
        df_anees_q_norm = pandas.DataFrame.from_dict(anees_q_norm, orient='index').T
        df_norm = pandas.concat([df_armse_p_norm, df_armse_q_norm, df_anees_p_norm, df_anees_q_norm], axis=1)
        # print df_norm

        # sum up the columns of the normalized dataframe and append to it
        df_norm.insert(len(df_norm.columns), 'norm_sum', df_norm.sum(axis=1, skipna=True).values)
        # reindex normailized dataframe
        df_norm.index = df.index
        # print df_norm

        # remove outliers removing always the 10% of the worse runs if numbers of run smaller than 10 just remove
        # the worse run. The worse run is defined as the one for which the normalized sum of the armse_p, armse_q,
        # anees_p, annes_q is maximum
        num_runs = self.est_report.get_run_num()
        num_rm = num_runs / 10
        if int(num_rm) > 0:
            for i in range(0, int(num_rm)):
                # to make it works iteratively i first need to drop elements from df and then drop the same element
                # from df_norm such that the next iteration it finds the next maximum
                df.drop(df.loc[df_norm['norm_sum'] == df_norm['norm_sum'].max()].index, inplace=True)
                df_norm.drop(df_norm.loc[df_norm['norm_sum'] == df_norm['norm_sum'].max()].index, inplace=True)
        else:
            if num_runs > 1:
                df.drop(df.loc[df_norm['norm_sum'] == df_norm['norm_sum'].max()].index, inplace=True)

        # numpy statistics automatically computes rmse, mean, median, std, min, max, ...
        stat_armes_p = numpy_statistics(df['armse_p'].values, 'armse_p')
        df_stat_armes_p = pandas.DataFrame.from_dict(stat_armes_p, orient='index').T
        stat_armes_q = numpy_statistics(df['armse_q'].values, 'armse_q')
        df_stat_armes_q = pandas.DataFrame.from_dict(stat_armes_q, orient='index').T
        stat_anees_p = numpy_statistics(df['anees_p'].values, 'anees_p')
        # normalize anees given the state dimension (=3)
        stat_anees_p['anees_p.mean'] = stat_anees_p['anees_p.mean'] / 3
        df_stat_anees_p = pandas.DataFrame.from_dict(stat_anees_p, orient='index').T
        stat_anees_q = numpy_statistics(df['anees_q'].values, 'anees_q')
        # normalize anees given the state dimension (=3)
        stat_anees_q['anees_q.mean'] = stat_anees_q['anees_q.mean'] / 3
        df_stat_anees_q = pandas.DataFrame.from_dict(stat_anees_q, orient='index').T
        df_res = pandas.concat([df_ale, df_stat_armes_p, df_stat_armes_q, df_stat_anees_p, df_stat_anees_q], axis=1)
        # print df_res

        # estimator judging based on the given thresholds
        if ((df_res['armse_p.mean'].values > self.rmse_p_th) | (df_res['armse_q.mean'].values > self.rmse_q_th)):
            df_res.insert(len(df_res.columns), 'failure', "True")
        else:
            df_res.insert(len(df_res.columns), 'failure', "False")

        return df_res

    def compute_average(self):
        df = pandas.DataFrame()
        for a in self.est_report.get_attr_values():
            for l in self.est_report.get_lvl_values():
                for e in self.est_report.get_est_values():
                    df_ = self.compute_average_over_runs(a, l, e)
                    if not df_.empty:
                        df = df.append(df_)

        return df.reset_index(drop=True)

    def compute_statistics(self):
        df = pandas.DataFrame()
        for a in self.est_report.get_attr_values():
            for l in self.est_report.get_lvl_values():
                for e in self.est_report.get_est_values():

                    df_ = self.compute_statistics_over_runs(a, l, e)
                    if not df_.empty:
                        df = df.append(df_)

        return df.reset_index(drop=True)

    def save(self, fn, save_index=False):

        EstimatorReport.save_data_frame(data_frame=self.data_frame_analyzer, fn=fn,
                                        fmt=self.data_frame_analyzer.columns,
                                        save_index=save_index)

    def load(self, fn):
        self.data_frame_analyzer = EstimatorReport.load_data_frame(fn=fn, fmt=EvaluationAnalyzer.get_column_format())

    @staticmethod
    def get_column_format():
        return ['attr', 'est', 'lvl', 'armse_p.max', 'armse_p.min', 'armse_p.pairs', 'armse_p.var', 'armse_p.rmse',
                'armse_p.median', 'armse_p.mean', 'armse_p.std', 'armse_q.mean', 'armse_q.pairs', 'armse_q.rmse',
                'armse_q.min', 'armse_q.max', 'armse_q.var', 'armse_q.median', 'armse_q.std', 'anees_p.max',
                'anees_p.rmse', 'anees_p.std', 'anees_p.median', 'anees_p.var', 'anees_p.mean', 'anees_p.pairs',
                'anees_p.min', 'anees_q.median', 'anees_q.mean', 'anees_q.var', 'anees_q.std', 'anees_q.pairs',
                'anees_q.min', 'anees_q.rmse', 'anees_q.max']


########################################################################################################################
#################################################### T E S T ###########################################################
########################################################################################################################
import unittest


class EvaluationAnalyzer_Test(unittest.TestCase):

    def test_init(self):
        analyzer = EvaluationAnalyzer(fn="./sample_data/EVAL/eval.csv")

        cfg = AnalyzerPlotConfig()
        cfg.show = False
        cfg.close_figure = False

        fig = plt.figure(figsize=(20, 15), dpi=int(cfg.dpi))
        analyzer.boxplot_at(1, 1, fig, cfg)

        df_ = analyzer.compute_average_over_runs(1, 1, 1)
        print(df_)
        df_ = df_.append(analyzer.compute_average_over_runs(1, 1, 2))
        print(df_)

        df = analyzer.compute_average()
        print(df)

        df = analyzer.compute_statistics()
        print(df)

        analyzer.save(fn="./sample_data/EVAL/eval_analized.csv", save_index=True)

        print('load again...')
        analyzer.load(fn="./sample_data/EVAL/eval_analized.csv")
        print(analyzer.data_frame_analyzer)


if __name__ == "__main__":
    unittest.main()
