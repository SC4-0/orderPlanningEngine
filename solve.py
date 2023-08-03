# -*- coding: utf-8 -*-
"""
Interface to run various multi-objective optimization algorithms
- runTransferOpt, calls the trNSGA2 with source transfer
- runOpt, calls the trNSGA2 without source transfer, similar to NSGA2
- runNSGAII, calls NSGA2 in pymoo

@author: cstan
"""

import numpy as np
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

import trNSGA2 as trOpt
import guassMixtureModel as gmm
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2

#use transfer optimization solver with human prior
def runTransferOpt(problem, num_gen=100, pop_size=100):
    nVar = problem.p["nF"] * problem.p["nC"] + problem.p["nF"]
    solver = None
    #setup source task/ human prior
    srcCov = np.diag(np.ones(problem.p["nF"] * problem.p["nC"]) * 0.1)
    srcMean = np.zeros(problem.p["nF"] * problem.p["nC"])
    #single customer to factory allocation based on nearest distance
    for c in range(problem.p["nC"]):
        idxF = np.argmin(problem.p["tLT"][:,c])
        srcMean[problem.p["nF"] * c + idxF] = 1
    srcModel = gmm.GuassModel()
    srcModel.build_from_param(srcMean, srcCov)
    srcModel.mod_dim(nVar)
    mm = gmm.GuassMixtureModel([srcModel])

    solver_trf = trOpt.trNSGA2(problem, num_gen, pop_size, nVar, mixture_model=mm, tr_int=2)
    #get Pareto solution & its obj values
    sol, obj = np.array(solver_trf.sol), np.vstack([solver_trf.obj1, solver_trf.obj2]).T
    p_idx = NonDominatedSorting().do(obj, only_non_dominated_front=True)

    return sol[p_idx], obj[p_idx]

def runOpt(problem, num_gen=100, pop_size=100):
    nVar = problem.p["nF"] * problem.p["nC"] + problem.p["nF"]
    solver_noTrf = trOpt.trNSGA2(problem, num_gen, pop_size, nVar, mixture_model=None, tr_int=None)
    #get Pareto solution & its obj values
    sol, obj = np.array(solver_noTrf.sol), np.vstack([solver_noTrf.obj1, solver_noTrf.obj2]).T
    p_idx = NonDominatedSorting().do(obj, only_non_dominated_front=True)

    return sol[p_idx], obj[p_idx]


#use plain vanilla NSGA2 solver from pymoo
def runNSGAII(problem, num_gen=100, pop_size=100):
    solver = NSGA2(pop_size=pop_size)
    result = minimize(problem, solver, ('n_gen', num_gen), seed=1, verbose=False)

    return result.X, result.F