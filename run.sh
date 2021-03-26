#! /bin/bash
################################################################################
#
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
################################################################################


# directory from where the bash file was executed
CUR_DIR=${PWD}

# directory where the bash file is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR=${DIR}/python-venv


if [ -d "$VENV_DIR" ]; then
  source ${VENV_DIR}/env/bin/activate
else
  echo "run setup first"
  #exit 1
  chmod +x ${DIR}/setup-env.sh
  ${DIR}/setup-env.sh
fi


# execute the evaluation:
export PYTHONPATH=$PYTHONPATH:$DIR

if [ -z "$1" ]; then
    echo "First argument should specify the EVAL_DIR"
    exit 1
else
  EVAL_DIR=$1
  echo "Eval directory: ${EVAL_DIR}"
fi


cd ${DIR}/estimator_evaluation

echo ${PWD}
ls -la
python3 ./EstimatorEvaluation.py --eval_dir $EVAL_DIR --thresholds 0.5 5  --redo

cd ${CUR_DIR}

exit 0
