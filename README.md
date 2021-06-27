# Olfactory bulb model with sister mitral cells
- Code to reproduce the simulations and figures in Tootoonian et al. 2021.

## Requirements
- Code was written and tested using Python 3.8.5 provided by Anaconda.
- Other versions/distributions of Python 3.8+ should also work with minimal modification.
- This code requires [cvxpy](https://www.cvxpy.org/install/). This can be installed using `pip install cvxpy`.
- This code also requires `tqdm` progress monitor, which can be installed using `pip install tqdm`
- This code was written and tested on CentOS Linux 7.
- Some of the simulations and analyses require large amounts of RAM, 64 GB is recommended.
## Basic setup
- Download this repository to a directory of your choice.
- Set an environment variable `SISTER_MCS` to this top level folder.
- Create a folder at a location of your choice, and set environment variable `SISTER_MCS_DATA` to this folder.
- To test the code, navigate to `$SISTER_MCS/code/test` 
- Run `./run.sh`.
- This will run a basic instance of the model.
- Once the run is complete, process the results using `python proc.py`
- This will create `proc.pdf`, showing some of the outputs.

## Code structure
- Most of the code is in the `code` subfolder.
- The file containing the olfactory bulb model is [olfactory_bulb.py](code/olfactory_bulb.py).
- An example of basic usage of the model can be found in the `create_and_run_olfactory_bulb` in [datatools.py](code/datatools.py).

### `gen_sweep_*.py`: Parameter sweeps
- To test the model at different parameter setting we ran several sweeps.
- The default parameters around which the model was tested are in [default_params.json](default_params.json).
- The parameters for each sweep were generated by a corresponding `gen_jobs_XYZ.py` script.
- Each script generates:
  - The folder to contain the sweep.
  - A number of JSON files, prefixed `params` and each containing the parameter settings for a single run of the model.
  - Shell scripts that create SLURM jobs for running the model for subsets of the parameter files using [run_sisters.py](code/run_sisters.py).
- `run_sisters.py` creates a subfolder e.g. `params123` where it stores the model output for `params123.json`.
- The data for the paper were generated from the following sweeps:
  - `sweep_S_k`
    - Aim was to determine the effect of the number of sisters for odours of various density.
	- Generated by [gen_jobs_S_k_sweep.py](code/gen_jobs_S_k_sweep.py).
    - Number of sisters `S` and number of molecules `k` present in the true odour were varied.
    - Results stored in `sweep_S_k`.
    - Used by [effect_of_sisters.py](code/effect_of_sisters.py).
  - `sweep_S_k_long`
    - Aim was to determine the effect of the odour density on inference.
	- Generated by [gen_jobs_S_k_long.py](code/gen_jobs_S_k_long.py).
    - `k` was varied.
	- `S` as fixed at 8.
    - Results stored in `sweep_S_k_long`.
    - Used by [effect_of_density.py](code/effect_of_density.py).	
  - `sweep_all_but_k3`
	- Aim was to determine the effect of membrane time constants and prior and likelihood parameters.
	- Generated by [gen_jobs_for_all_but_k_sweep.py](code/gen_jobs_for_all_but_k_sweep.py).
	- `S` was varied.
	- The parameters `be`, `sd`, `ga`, `tau_mc`, `tau_gc`, `tau_pg` were individually varied from 0.5x to 2x their default values.	
	- Used by [effect_of_parameters.py](code/effect_of_parameters.py).
  - `sweep_conc_spread`
    - Aim was to run the model for odours with a spread in concentration to aid visual inspection of inference results.
	- Generated by [gen_jobs_conc_spread_sweep.py](code/gen_jobs_conc_spread_sweep.py)
	- `spread = 0.4`: Concentration of molecules present in the true odour spread from 0.8 to 1.2.
	- `S`, `k`, and `leak_pg` were varied.
	- Used by [effect_of_leaky_pgs.py](code/effect_of_leaky_pgs.py) and [figfuns.py](code/figfuns.py).
  - `sweep_MNk_conc_spread`
	- Aim was to determine the effect of the olfactory bulb size, using a spread of concentration in the true odour to aid visual inspection.
	- `M`, `N` and `k` were varied.
	- `S` was fixed at 25.
	- `spread` was fixed at 0.4.
	- Used by [effect_of_size.py](code/effect_of_size.py).	
  - `sweep_qeps`
    - Aim was to determine effect of `leak_pg`.
	- Generated by [gen_jobs_qeps_sweep.py](code/gen_jobs_qeps_sweep.py).
	- `S`, `leak_pg` varied.
	- Used by [effect_of_leaky_pgs.py](code/effect_of_leaky_pgs.py).
  - `sweep_random_odours`
    - Aim was to use multiple odours to determine variation in sister cell activity ratios at convergence.
	- Generated by [gen_jobs_random_odours.py](code/gen_jobs_random_odours.py).
	- `S` varied, `leak_pg` varied.
	- 10 different random odours were generated for the same bulb.
	- Used by [effect_of_leaky_pgs.py](code/effect_of_leaky_pgs.py).

### Computing MAP estimates
- When `leak_pg` = 0 the model should arrive at the MAP solution at convergence.
- To check this, we computed the MAP solution directly using `cvxpy`.
- This was done for each `param...json` file in the relevant sweeps using [compute_x_MAP.py](code/compute_x_MAP.py).
- This script loads the parmeter values from each JSON file and uses `get_x_MAP_for_params` in [datatools.py](code/datatools.py), which uses CVXPY to compute the MAP estimate for those parameter values.
- The output is written to `x_MAP.npy` in the corresponding `params...` directory.
- The script [compare_x_final_and_x_MAP.py](code/compare_x_final_and_x_MAP.py) compares the solution found by the model `x_final` to the solution found by CVXPY.

### `effect_of_*.py`: Processing sweep results
- Once the sweeps have been computed, including MAP estimates using CVXPY where relevant, the results can be plotted by running the relevant section of the notebook [make_figures.ipynb](make_figures.ipynb).
- This notebook calls the various `effect_of_*.py` scripts to load the data from the sweeps, save the processed data to the related `*_data.p` files, and plot the relevant figure data.
- Each `effect_of` script has a `load_data` function which loads the relevant data from the sweeps folder.
- Each `effect_of` script also has a variety of plotting functions that `make_figures.ipynb` uses to plot the results of each sweep as various figure panels.

### Other files
- [demo_linearization.py](code/demo_linearization.py): Files for computing and plotting the actual and predicted eigenvalues of the linearized system.
- [figtools.py](code/figtools.py): Various utility functions related mainly to plotting.
- [figfuns.py](code/figfuns.py): Functions for loading the data and plotting timecourses of the various model variables.
- [run_sisters.py](code/run_sisters.py): Runs the model for parameters provided as a comma separated list of JSON files.
- [test_linearization.py](code/test_linearization.py): Unit test code for testing the equations of the linear analysis. Run with `python -m unittest test_linearization`.
- [transient_response.py](code/transient_response.py): Combines the data generated by `effect_of_sisters.py` and `effect_of_parameters.py` to produce the transient response figure.
- [util.py](code/util.py): Contains a function to create loggers used throughout the code.
