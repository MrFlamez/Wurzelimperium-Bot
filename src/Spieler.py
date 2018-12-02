#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017
@author: MrFlamez
'''
from collections import namedtuple


Login = namedtuple('Login', 'server user password')

class Spieler():
    
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Spieler.
    """
    
    accountLogin = None
    userName = None
    userID = None
    numberOfGardens = None
    userData = None
    __honeyFarmAvailability = None
    __aquaGardenAvailability = None
    eMailAdressConfirmed = True #TODO: Muss ermittelt werden im Wurzelbot

    def __init__(self):
        pass

    def setHoneyFarmAvailability(self, bAvl):
        self.__honeyFarmAvailability = bAvl

    def isHoneyFarmAvailable(self):
        return self.__honeyFarmAvailability

    def setAquaGardenAvailability(self, bAvl):
        self.__aquaGardenAvailability = bAvl

    def isAquaGardenAvailable(self):
        return self.__aquaGardenAvailability
    
    def getUserName(self):
        return self.userName
    
