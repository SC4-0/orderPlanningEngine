# orderPlanning
Initial commit on order planning problem formulation and solvers
Additional python libraries and its current version used:
-Python 3.10.4
- numpy 1.24.3
- pymoo 0.6.0.1
- scipy 1.10.1

To compute the Pareto solutions, run the plan function in the orderPlanner.py
-Input 
  - param: problem parameters in dictionary format
  - R: number of replication
  - factPrefReq: dictates if factory level performace is required
- Output
  - sol, 20 by (num of fact * num of cust + number of fact)
  - scPerf, 20 by 2 (average fulfillment Time, average UnUtilised Hr) - SC lvl performance
  - factPerf, 20 by (2 * num fact) - fact lvl performance
