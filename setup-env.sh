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





CUR_DIR=${PWD}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR=${DIR}/python-venv


if [ ! -d "$VENV_DIR" ]; then
  mkdir ${VENV_DIR}
fi

cd ${VENV_DIR}

sudo apt-get install python3-venv
python3 -m pip install virtualenv
python3 -m venv env
source env/bin/activate
which python
pip install -r ${DIR}/requirements.txt

#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-trajectory==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-trajectory-evaluation==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-rosbag2csv==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-csv2dataframe==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-timestamp-association==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-spatial-csv-formats==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-script-utils==0.1.0
#pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple cnspy-numpy-utils==0.1.0

cd ${CUR_DIR}
