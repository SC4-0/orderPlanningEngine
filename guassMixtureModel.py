# -*- coding: utf-8 -*-
"""
- Helper class to trNSGA2
- Models the correlation between source (human prior) and current (in optimization) solution distributions based on a probabilistic Guassin mixture model
@author: cstan
"""

import numpy as np
from scipy.stats import multivariate_normal

class GuassModel():
    def __init__(self, sol=None):
        self.dim = None
        self.mean, self.cov = None, None
        self.mean_noisy, self.cov_noisy = None, None
        
        if sol is not None: self.build_frm_sol(sol)
        
    #determine the distribution from src sol
    def build_frm_sol(self, sol):
        self.dim = sol.shape[1]
        self.mean = np.mean(sol, axis=0)
        self.cov = np.diag(np.diag(np.cov(sol.T))) # assume indenpendence among varaible
        
        #create 20% of random solution
        rand_sol = np.random.rand(int(0.2*sol.shape[0]), sol.shape[1])
        sol_noisy = np.vstack([sol, rand_sol])
        self.mean_noisy = np.mean(sol_noisy, axis=0)
        self.cov_noisy = np.diag(np.diag(np.cov(sol_noisy.T))) # assume indenpendence among varaible
        
    
    #initial the distribution parameters
    def build_from_param(self, mean, cov):
        self.dim = mean.shape[0]
        self.mean, self.mean_noisy = mean, mean    
        self.cov, self.cov_noisy = cov, cov*1.2
        
    #ensure that the dimensionality of src & tar problem are the same
    def mod_dim(self, dim):
        #remove additional dimension
        if dim < self.dim:
            self.mean = self.mean[:dim]
            self.mean_noisy = self.mean_noisy[:dim]
            
            self.cov = self.cov[:dim, : dim]
            self.cov_noisy = self.cov_noisy[:dim, : dim]
            
        #pad it with with mean 0.5, var 1
        elif dim > self.dim:
            mean_dim = np.ones(dim)*0.5
            mean_dim[:self.dim] = self.mean
            self.mean = mean_dim.copy()
            self.mean_noisy = mean_dim.copy()
            
            cov_dim = np.diag(np.ones(dim))
            cov_dim[:self.dim, :self.dim] = self.cov
            self.cov = cov_dim.copy()
            self.cov_noisy = cov_dim.copy()
            
    #sampling based on actual distribution
    def sample(self, sampleSize):      
        return np.random.multivariate_normal(self.mean, self.cov, sampleSize)

    #prob density evaluation based on noisy distribution
    def pdFunc(self, s):
        return multivariate_normal.pdf(s, mean=self.mean_noisy, cov=self.cov_noisy)

class GuassMixtureModel():
    def __init__(self, srcModel):
        self.model = [*srcModel] #srcModwl
        self.model.append(GuassModel()) #tarModel
        self.mTot = len(self.model)
        self.probTable = None
        
        self.trf = np.ones(self.mTot)/ self.mTot #transfer coefficient
        self.trf_records = []

    def update(self, tarSol):
        self.computeProb(tarSol)
        self.computeTrf()

    def computeProb(self, tarSol):
        self.model[-1].build_frm_sol(tarSol)
        self.probTable = np.ones([tarSol.shape[0], self.mTot])
        
        #src model: compute pdf of each sol
        for m in range(self.mTot-1):
            self.probTable[:, m] = self.model[m].pdFunc(tarSol)
        #target model: compute pdf of sol i with Guassian Model built without sol i
        for i in range(tarSol.shape[0]):  # Leave-one-out cross validation
            x = np.concatenate((tarSol[:i, :], tarSol[i+1:, :]))
            tarModel = GuassModel(sol=x)
            self.probTable[i, -1] = tarModel.pdFunc(tarSol[[i], :])
    
    #determine transfer coefficient with emStacking
    def computeTrf(self, nIter=100, perturb=True):
        #reset transfer coefficient
        self.trf = np.ones(self.mTot)/ self.mTot
        for i in range(nIter):
            probVector = np.matmul(self.probTable, self.trf.T) #final weighted prob
            for i in range(self.mTot):
                self.trf[i] = np.sum((self.trf[i]*self.probTable[:, i]) / probVector)
                self.trf[i] /= self.probTable.shape[0] #num of sol
            self.trf = np.around(self.trf, decimals=5) #round it to neart 5 decimal place
        
        #record trf coeeficient b4 perturbation
        self.trf_records.append(self.trf)

        #perturb transfer coefficient slightly
        if perturb: self.perturb()
        
        #ensure sum of trf is 1
        trf_sum = np.sum(self.trf)
        if trf_sum == 0: 
            self.trf = np.zeros(self.mTot)
            self.trf[-1] = 1
        else:
            self.trf /= trf_sum

    def perturb(self):
        self.trf = np.maximum(self.trf + np.random.normal(0, 0.01, self.mTot), 0)

    def sample(self, sampleSize):
        modelSampleSize = np.ceil(sampleSize*self.trf).astype(int) #number of samples for each model
        modelSampleSize[-1] -= modelSampleSize.sum() - sampleSize
        sol = np.array([])-sampleSize
        for i in range(self.mTot):
            if modelSampleSize[i] > 0:
                s = self.model[i].sample(modelSampleSize[i])
                sol = np.vstack([sol, s]) if sol.size else s
        
        #shuffle the solutions
        sol = sol[np.random.permutation(sol.shape[0]), :]
        sol = sol[:sampleSize, :]
        
        return sol