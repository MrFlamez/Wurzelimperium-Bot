#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2019

@author: MrFlamez
'''

class Product():
    
    def __init__(self, id, cat, sx, sy, name, lvl, crop, plantable, time, nInStock):
        self.__id = id
        self.__category = cat
        self.__sx = sx
        self.__sy = sy
        self.__name = name
        self.__level = lvl
        self.__crop = crop
        self.__isPlantable = plantable
        self.__timeUntilHarvest = time
        self.__numberInStock = nInStock
        
    def getID(self):
        return self.__id
    
    def getName(self):
        return self.__name

    def getNumberInStock(self):
        return self.__numberInStock
    
    def getSX(self):
        return self.__sx

    def getSY(self):
        return self.__sy
    
    def isProductPlantable(self):
        return self.__isPlantable

    def setNumberInStock(self, nmbr):
        self.__numberInStock = nmbr
        
    def printAll(self):
        print 'ID: ', str(self.__id).ljust(5), \
              'CAT: ', str(self.__category).ljust(8), ' ', \
              'Name: ', str(self.__name).ljust(50), ' ', \
              'Lager: ', str(self.__numberInStock).ljust(8), ' ', \
              'SX: ', str(self.__sx).ljust(4), ' ', \
              'SY: ', str(self.__sy).ljust(4)



