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
# pandas, argparse, cnspy_spatial_csv_formats, cnspy_rosbag2csv, cnspy_script_utils, cnspy_trajectory_evaluation
########################################################################################################################
import os
import time
import argparse

from cnspy_spatial_csv_formats.CSVFormatPose import CSVFormatPose
from cnspy_rosbag2csv.ROSbag2CSV import ROSbag2CSV
from cnspy_script_utils.directory_info import get_list_of_dir, get_list_of_files
from cnspy_script_utils.string_parser import string_to_list
from cnspy_script_utils.utils import exit_success, exit_failure
from cnspy_trajectory_evaluation.TrajectoryEvaluation import TrajectoryEvaluation
from cnspy_trajectory_evaluation.EvaluationReport import EvaluationReport
from cnspy_trajectory_evaluation.TrajectoryAlignmentTypes import TrajectoryAlignmentTypes
from estimator_evaluation.EstimatorReport import EstimatorReport
from estimator_evaluation.EvaluationAnalyzer import EvaluationAnalyzer


# folder structure:
# - EVAL
#   - ATTR_1
#   - ATTR_*
#   - ATTR_N
#     - LVL_1
#     - LVL_*
#     - LVL_M
#       - RUN_1
#       - RUN_*
#       - RUN_K
#           - EVAL_<ATTR_N>_<LVL_M>_<RUN_K>_<EST_1>.bag
#           - EVAL_<ATTR_*>_<LVL_*>_<RUN_*>_<EST_*>.bag
#           - RESULTS
#               - EST_1
#               - EST_*
#                   - report.ini
#                   - *.csv

class EstimatorEvaluation:
    est_report = EstimatorReport()  # table holds: attr, lvl, run, est, armse_p, armse_q, anees_p, anees_q
    num_attributes = 0
    num_levels = 0
    num_runs = 0
    num_est = 0
    topic_list = ["/pose_gt", "/pose_est"]
    fn_list = ["pose-gt.csv", "pose-est-cov.csv"]
    alignment_type = TrajectoryAlignmentTypes.pos
    num_aligned_samples = -1

    def __init__(self, eval_dir=".", redo=False, plot=False, save_plot=False,
                 alignment_type_=TrajectoryAlignmentTypes.pos, frames_=-1):
        self.alignment_type = alignment_type_
        self.num_aligned_samples = frames_
        self.crawl_through(eval_dir, redo=redo, plot=plot, save_plot=save_plot)
        pass

    def crawl_through(self, eval_dir, redo=False, plot=False, save_plot=False):
        print("EVAL: " + str(os.path.abspath(eval_dir)))
        for ATTR in get_list_of_dir(eval_dir):
            head, tail = os.path.split(ATTR)

            if 'ATTR_' not in ATTR:
                continue
            l = string_to_list(ATTR, 'ATTR_{0}')
            assert (l is not None)
            attr_val = l[0]
            print("\t-ATTR: " + str(tail) + ' val:' + str(attr_val))

            for LVL in get_list_of_dir(ATTR):
                head, tail = os.path.split(LVL)
                if 'LVL_' not in LVL:
                    continue
                l = string_to_list(LVL, 'LVL_{0}')
                assert (l is not None)
                lvl_val = l[0]

                print("\t\t-LVL: " + str(tail) + ' val:' + str(lvl_val))

                for RUN in get_list_of_dir(LVL):
                    head, tail = os.path.split(RUN)
                    if 'RUN_' not in RUN:
                        continue

                    l = string_to_list(RUN, 'RUN_{0}')
                    assert (l is not None)
                    run_val = l[0]
                    print("\t\t\t-RUN: " + str(tail) + ' val:' + str(run_val))

                    for bag in get_list_of_files(RUN):
                        head, tail = os.path.split(bag)
                        if '.bag' in tail:
                            l = string_to_list(tail, 'ATTR_{0}_LVL_{1}_RUN_{2}_EST_{3}.bag')
                            # print(str(l))
                            assert (l is not None)
                            print("\t\t\t\t-bag: " + str(tail) + ', values: attr={0},lvl={1},run={2}, est={3}'.format(
                                l[0], l[1], l[2], l[3]))
                            self.evaluate_bag_file(bag_fn=bag, redo=redo, plot=plot, save_plot=save_plot)

    def evaluate_bag_file(self, bag_fn, redo=False, plot=False, save_plot=False):
        head, tail = os.path.split(bag_fn)
        l = string_to_list(tail, 'ATTR_{0}_LVL_{1}_RUN_{2}_EST_{3}.bag')
        if l is not None:
            attr_val = l[0]
            lvl_val = l[1]
            run_val = l[2]
            est_val = l[3]
            # check if there is already a report.ini for this estimator
            # if it does not exist, make a report!
            result_dir = head + "/RESULTS/EST_{0}".format(est_val)
            report_file = result_dir + "/report.ini"
            report = None
            if not os.path.exists(report_file) or redo:
                print('\t\t\t\t\t-report does not exist! evaluate: ' + str(tail))
                if not ROSbag2CSV.extract(bagfile_name=bag_fn, topic_list=self.topic_list, fn_list=self.fn_list,
                                          fmt=CSVFormatPose.PoseWithCov, result_dir=result_dir, verbose=True):
                    print("\t\t\t\t\tproblem extracting bag file!")
                    return

                fn_gt = os.path.join(result_dir, self.fn_list[0])
                fn_est = os.path.join(result_dir, self.fn_list[1])
                e = TrajectoryEvaluation(fn_gt=fn_gt, fn_est=fn_est,
                                         result_dir=result_dir, alignment_type=self.alignment_type,
                                         num_aligned_samples=self.num_aligned_samples, plot=plot, save_plot=save_plot)
                report = e.report
            else:
                print('\t\t\t\t\t-report does exist! read from : ' + str(report_file))
                report = EvaluationReport()
                report.load(fn=report_file)

            if report is not None:
                self.est_report.append_row(attr_val=attr_val, lvl_val=lvl_val, run_val=run_val, est_val=est_val,
                                           armse_p=report.ARMSE_p, armse_q=report.ARMSE_q, anees_p=report.ANEES_p,
                                           anees_q=report.ANEES_q)


########################################################################################################################
#################################################### T E S T ###########################################################
########################################################################################################################
# import unittest
# import time
#
#
# class EstimatorEvaluation_Test(unittest.TestCase):
#     start_time = None
#
#     def start(self):
#         self.start_time = time.time()
#
#     def stop(self, info="Process time"):
#         print(str(info) + " took : " + str((time.time() - self.start_time)) + " [sec]")
#
#     def test_init(self):
#         self.start()
#         est_eval = EstimatorEvaluation("./sample_data/EVAL")
#         self.stop('Loading + ATE')
#         est_eval.est_report.save(fn="./sample_data/EVAL/eval.csv", save_index=False)


########################################################################################################################
################################################### APPLICATION ########################################################
########################################################################################################################
if __name__ == "__main__":
    # unittest.main()

    parser = argparse.ArgumentParser(
        description=str('EstimatorEvaluation: crawling through a folder structure and evaluating estimators:\n' +
                        '- EVAL/ \n\t - ATTR_*/ \n\t\t - LVL_*/ \n\t\t\t - RUN_*/ \n\t\t\t\t - ' +
                        'EVAL_<ATTR_*>_<LVL_*>_<RUN_*>_<EST_*>.bag \n\t\t\t\t - RESULTS/  (will be created by ' +
                        'EstimatorEvaluation) \n\t\t\t\t\t - EST_*/\n\t\t\t\t\t\t - report.ini (check point) ' +
                        ' \n\t\t\t\t\t\t - *.csv  \n\t\t\t\t\t\t - *.png \n - eval.csv (final result)' +
                        ' \n - eval_analyzed.csv (final result)'))

    parser.add_argument('--eval_dir', help='root directory of evaluation', default="not specified", required=True)
    parser.add_argument('--redo', help='redo the entire evaluation (ignoring check points)', action='store_true',
                        default=False)
    parser.add_argument('--plot', help='shows the different plots of TrajectoryEvaluation()', action='store_true',
                        default=False)
    parser.add_argument('--save_plot', help='store the different plots of TrajectoryEvaluation()', action='store_true',
                        default=False)
    parser.add_argument('--alignment_type', default='se3', help='alignment types are: None, se3, sim3, posyaw, pos')
    parser.add_argument('--thresholds', nargs='+', type=float,
                        help='position and orientation ARMSE thresholds (<float>[m] <float>[deg]) for estimators judging',
                        required=True)
    parser.add_argument('--frames', type=int, help='# of frames for trajectory alignment, -1 = all', default=-1)
    args = parser.parse_args()

    alignment_type = TrajectoryAlignmentTypes(str(args.alignment_type))
    tp_start = time.time()
    est_eval = EstimatorEvaluation(eval_dir=args.eval_dir, redo=args.redo, plot=args.plot, save_plot=args.save_plot,
                                   alignment_type_=alignment_type, frames_=args.frames)
    est_eval.est_report.save(fn=os.path.join(args.eval_dir, "eval.csv"), save_index=False)

    eval_analyzer = EvaluationAnalyzer(fn=os.path.join(args.eval_dir, "eval.csv"), rmse_p_th=args.thresholds[0],
                                       rmse_q_th=args.thresholds[1])
    eval_analyzer.save(fn=os.path.join(args.eval_dir, "eval_analyzed.csv"), save_index=True)

    print("\nfinished after [%s sec]\n" % str(time.time() - tp_start))
    exit_success()
