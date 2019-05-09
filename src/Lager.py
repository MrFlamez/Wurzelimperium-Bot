#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from Produkt import Product

CATEGORY_DECORATION       = 'd'
CATEGORY_HERBS            = 'h'
CATEGORY_HONEY            = 'honey'
CATEGORY_WATER_PLANTS     = 'w'
CATEGORY_VEGETABLES       = 'v' 
CATEGORY_WATER_DECORATION = 'wd'
CATEGORY_COINS            = ''
CATEGORY_ADORNMENTS       = 'z'
CATEGORY_OTHER            = 'u'

class Storage():
    
    def __init__(self, httpConnection):
        self.__httpConn = httpConnection
        self.__products = []
    
    def __setAllPricesOfNPC(self):
        """
        Ermittelt alle möglichen NPC Preise und setzt diese in den Produkten.
        """
        
        dNPC = self.__httpConn.getNPCPrices()
        dNPCKeys = dNPC.keys()
        
        for product in self.__products:
            productname = product.getName()
            if productname in dNPCKeys:
                product.setPriceNPC(dNPC[productname])
    
    def getProductByID(self, id):
        for product in self.__products:
            if int(id) == int(product.getID()): return product
            
    def getProductByName(self, name):
        try:
            for product in self.__products:
                if (name == product.getName()): return product
        except:
            pass #TODO: Exception-Fall definieren
        else:
            pass

    def initAllProducts(self):
        """
        Initialisiert alle Produkte.
        """
        products = self.__httpConn.getAllProductInformations()
        jProducts = json.loads(products)
        dictProducts = dict(jProducts)
        keys = dictProducts.keys()
        keys = sorted(keys)
        #Nicht genutzte Attribute: img, imgPhase, fileext, clear, edge, pieces, speedup_cooldown in Kategorie z
        for key in keys:
            if key != '999' and key != '0':
                #999 ist nur ein Testeintrag und wird nicht benötigt.
                #0 sind Coins, diese werden direkt dem Spieler zugeordnet.
                name = dictProducts[key]['name'].replace('&nbsp;', ' ')
                self.__products.append(Product(id        = key, \
                                               cat       = dictProducts[key]['category'], \
                                               sx        = dictProducts[key]['sx'], \
                                               sy        = dictProducts[key]['sy'], \
                                               name      = name.encode('utf-8'), \
                                               lvl       = dictProducts[key]['level'], \
                                               crop      = dictProducts[key]['crop'], \
                                               plantable = dictProducts[key]['plantable'], \
                                               time      = dictProducts[key]['time'], \
                                               nInStock  = 0))
                
        self.__setAllPricesOfNPC()
        self.updateNumberInStock()
    
    def updateNumberInStock(self):
        """
        Führt ein Update des Lagerbestands für alle Produkte durch.
        """
        
        for product in self.__products:
            product.setNumberInStock('0')
            
        inventory = self.__httpConn.getInventory()
        
        for i in inventory:
            product = self.getProductByID(i)
            product.setNumberInStock(inventory[i])
    
    
    def test(self): #TODO: Kann entfernt werden am Ende
        for product in self.__products:
            product.printAll()


