# -*- coding: utf-8 -*-
"""
Objects to model the order planning problem
- Order, storing order-related data
- Factory, storing factory-related data & its state and mimics the production behaviour
@author: cstan
"""

class Order():
    def __init__(self, cust, arrivalTime, reqHr, f):
        self.cust = cust
        self.arrivalTime = arrivalTime
        self.reqHr = reqHr #multi-product
        
        self.id = str(arrivalTime) + str(cust)
        self.fact = f
        
        self.fulfilmentTime = None
        
    def clone(self, qty):
        return Order(self.cust, self.arrivalTime, qty)

class Factory():
    def __init__(self, f, maxHr, tLT):
        self.id = f
        self.maxHr = maxHr
        self.tLT = tLT #nC by 1 transportation lead time
        self.activeOrder = [] #active order to produce
        self.unUtilHr, self.totAvailHr = 0, 0

        self.dailyUnUtilHr = []
        self.dailyFillTime, self.dailyOrderFilled, self.dailyOrderAlloc = [], [], []

    def reset(self):
        self.activeOrder = []
        self.unUtilHr, self.totAvailHr = 0, 0

        self.dailyUnUtilHr = []
        self.dailyFillTime, self.dailyOrderFilled, self.dailyOrderAlloc = [], [], []

    def produce(self, currT, minPHr):
        completedOrder = []
        if minPHr < sum(o.reqHr for o in self.activeOrder):
            availHr = self.maxHr
            #print("Production for F", self.id, "with min hr", minPHr, "and tot hr", sum(o.reqHr for o in self.activeOrder))
            while len(self.activeOrder) > 0 and availHr > 0:
                if availHr>= self.activeOrder[0].reqHr:
                    order = self.activeOrder.pop(0)  # remove orders
                    availHr -= order.reqHr
                    completeT = currT + self.tLT[order.cust] + 1
                    order.fulfilmentTime = completeT - order.arrivalTime
                    completedOrder.append(order)
                    #print("Order ", order.id, " is fulfilled with lead time of", order.fulfilmentTime)
                else:
                    self.activeOrder[0].reqHr -= availHr
                    availHr = 0
                    #print("Partial production of order ", self.activeOrder[0].id,
                          #" with ", round(self.activeOrder[0].reqHr, 2), "remaining hours")
            #print("Req Hr", sum(o.reqHr for o in self.activeOrder))
            self.unUtilHr += availHr
            self.totAvailHr += self.maxHr
            self.dailyUnUtilHr.append(availHr/ self.maxHr)
            if len(completedOrder) > 0:
                self.dailyFillTime.append(sum(o.fulfilmentTime for o in completedOrder)/len(completedOrder))
                self.dailyOrderFilled.append(len(completedOrder))
            else:
                self.dailyFillTime.append(0)
                self.dailyOrderFilled.append(0)
            #print("Tot order processed:", len(completedOrder))
        else:
            self.dailyUnUtilHr.append(0)
            self.dailyFillTime.append(0)
            self.dailyOrderFilled.append(0)

        return completedOrder