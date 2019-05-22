#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 15.05.2019

@author: MrFlamez
'''

class Marketplace():
    
    def __init__(self, httpConnection):
        self.__httpConn = httpConnection
        self.__tradeableProductIDs = None
        
    def getAllTradableProducts(self):
        return self.__tradeableProductIDs
    
    def updateAllTradableProducts(self):
        self.__tradeableProductIDs = self.__httpConn.getAllTradeableProductsFromOverview()
    
    def getCheapestOffer(self, id):
        """
        Ermittelt das günstigste Angebot eines Produkts.
        """
        self.updateAllTradableProducts()
        
        if self.__tradeableProductIDs != None \
           and \
           id in self.__tradeableProductIDs:

            listOffers = self.__httpConn.getOffersFromProduct(id)
            if len(listOffers) >= 1:
                return listOffers[0][1]
            else: #No Offers
                return None

        else: #Product is not tradeable
            return None
