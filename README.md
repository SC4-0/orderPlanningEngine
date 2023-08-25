# orderPlanning
Initial commit on order planning problem formulation and solvers
Additional python libraries and its current version used:
-Python 3.10.4
- numpy 1.24.3
- pymoo 0.6.0.1
- scipy 1.10.1


To compute the Pareto solutions, run the plan function in the orderPlanner.py

- Input
  - param: problem parameters in dictionary format
  - R: number of replication
  - factPrefReq: dictates if factory level performace is required
  - allocRange: if true converts the solution to a min and max range

- Output
  - sol, 20 by (num of fact * num of cust + number of fact)
  - scPerf, 20 by 2 (average fulfillment Time, average UnUtilised Hr) - SC lvl performance
  - factPerf, 20 by (2 * num fact) - fact lvl performance
  - unUtilCapPref, 20 by 1 - preference value from 0 to 1 on the unutilised capacity
  - perfCat, 20 by 1 - categorises the solution into the following 4 categories
      - 0, Short Order Fulfilment Time with Higher Unutilized Production Capacity
      - 1, Mid Order Fulfilment Time with Slightly Higher Unutilized Production Capacity
      - 2, Mid Unutilized Production Capacity with Slightly Longer Order Fulfilment Time
      - 3, Low Unutilized Production Capacity with Longer Order Fulfilment Time
