# VINSEval - Estimator Evaluation Tool (cnspy_estimator_evaluation)

## License
This software is made available to the public to use (_source-available_),
licensed under the terms of the BSD-2-Clause-License with no commercial use allowed, the full terms of which are made available in the LICENSE file. No license in patents is granted.

### Usage for academic purposes
If you use this software in an academic research setting, please cite the
corresponding paper and consult the `LICENSE` file for a detailed explanation.

```latex
@inproceedings{vinseval,
   author   = {Alessandro Fornasier and Martin Scheiber and Alexander Hardt-Stremayr and Roland Jung and Stephan Weiss},
   journal  = {2021 Proceedings of the IEEE International Conference on Robotics and Automation (ICRA21 - accepted)},
   title    = {VINSEval: Evaluation Framework for Unified Testing of Consistency and Robustness of Visual-Inertial Navigation System Algorithms},
   year     = {2021},
}
```

---

## Prerequisites

There are different ways to set up this python project. Most conveniently is to execute the `setup-env.sh` in the root of the project.
This will create a virtual python3 environment and install the dependencies.
```
$ chmod +x setup-env.sh
$ ./setup-env.sh
```
Then that you have to activate the new python environment via:
```
$ source ./python-venv/env/bin/activate
```


Otherwise, the requirements can be installed system wide:
```
pip install -r requirements.txt
```

As this project is not installed on your system, we need add this project to the `PYTHONPATH`:
```
$ export PYTHONPATH=$PYTHONPATH:< >/eval_tools
# or
eval_tools$ export PYTHONPATH=$PYTHONPATH:$PWD
```


## Dependencies

- [cnspy_csv2dataframe](https://github.com/aau-cns/cnspy_csv2dataframe) and the [official package](https://pypi.org/project/cnspy-csv2dataframe/)
- [cnspy_numpy_utils](https://github.com/aau-cns/cnspy_numpy_utils) and the [official package](https://pypi.org/project/cnspy-numpy-utils/)
- [cnspy_rosbag2csv](https://github.com/aau-cns/cnspy_rosbag2csv) and the [official package](https://pypi.org/project/cnspy-rosbag2csv/)
- [cnspy_script_utils](https://github.com/aau-cns/cnspy_script_utils) and the [official package](https://pypi.org/project/cnspy-script-utils/)
- [cnspy_spatial_csv_formats](https://github.com/aau-cns/cnspy_spatial_csv_formats) and the [official package](https://pypi.org/project/cnspy-spatial-csv-formats/)
- [cnspy_timestamp_association](https://github.com/aau-cns/cnspy_timestamp_association) and the [official package](https://pypi.org/project/cnspy-timestamp-association/)
- [cnspy_trajectory](https://github.com/aau-cns/cnspy_trajectory) and the [official package](https://pypi.org/project/cnspy-trajectory/)
- [cnspy_trajectory_evaluation](https://github.com/aau-cns/cnspy_trajectory_evaluation) and the [official package](https://pypi.org/project/cnspy-trajectory-evaluation/)


## Estimator Evaluation

A package to evaluate estimated trajectories recorded in ROS bagfiles having different properties.
[More](estimator_evaluation/README.md)
