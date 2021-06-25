# In this script we're going to generate jobs for the condition
# were we test multiple random odours on the same bulb.
import os, sys
import numpy as np
import pickle
import json
import itertools

header = """#!/bin/bash
# Simple SLURM sbatch example
#SBATCH --job-name=JOBNAME
#SBATCH --ntasks=1
#SBATCH --time=6:00:00
#SBATCH --mem-per-cpu=32G
#SBATCH --partition=cpu

#SWEEP_PARAM PNAME  S, leak_pg
#SWEEP_PARAM PVALUE _pvalue_
#SWEEP_PARAM PRUN   _prun_

ml purge > /dev/null 2>&1
python -u ../run_sisters.py PARAMSFILE --write_every 1000
"""

import datatools as dt

default_params = dt.load_default_params()
default_params["dt"]        = 1e-6
default_params["t_end"]     = 2.1
default_params["keep_till"] = 0.6

default_params["k"]         = 3
sweep_name = f"sweep_random_odours"
os.system("mkdir -p {}".format(sweep_name))

S_vals       = [1,2,4,8,16, 25] #,12,16,20,25,30,40,50,60,80,100,120]
#leak_pg_vals = [3,4,6,7,8,9] #[0,1,2,5,10]
leak_pg_vals = list(np.arange(0.1,1,0.1)) + [1.5]
n_odours     = 10
n_runs       = 5

job_id = 5000
for S, leak_pg in itertools.product(S_vals, leak_pg_vals):
    for run in range(n_runs):
        params = dict(default_params)
        params["S"]       = S
        params["leak_pg"] = leak_pg
        params["seed"]    = run
        for which_odour in range(n_odours):
            params["which_odour"] = which_odour
        
            job_name = f"{S}S{leak_pg}L{run}O{which_odour}"
            job_script = header.replace("JOBNAME", job_name).replace("_pvalue_", f"{S}, {leak_pg}").replace("_prun_", str(run)).replace("PARAMSFILE", f"params{job_id}.json")
            
            params_file = os.path.join(sweep_name, f"params{job_id}.json")
            with open(params_file, "w") as out_file:
                json.dump(params, out_file)
    
            job_file = os.path.join(sweep_name, f"job{job_id}.sh")
            with open(job_file, "w") as out_file:
                out_file.write(job_script)
    
            print(f"Wrote {job_file}.")
            
            job_id+=1
            

