#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.01.2017

@author: MrFlamez
'''

import time, logging


class Session(object):
    """
    Die Session Klasse stellt die Kommunikation des Wurzelbots mit dem Spiel sicher und
    koordiniert alle HTTP-Anfragen inkl. der Informationgewinnung aus den Antworten.
    Sie ist das Pendant einer PHPSession auf Python-Ebene und dieser daher nachempfunden.
    
    Die Session weiß selbst für welchen Server/Spieler sie exklusiv geöffnet wurde.
    """

    __lifetime = 7200 #Gültigkeit der Session (2 h -> 7200 s)
    #TODO: evtl. 2 min. weniger __lifetime um Aktionen ungestört durchführen zu können
    
    
    def __init__(self):

        self.__logSession = logging.getLogger('bot.Session')
        self.__sessionID = None
        self.__server = None
        self.__userID = None
        self.__startTime = None
        self.__endTime = None  
        
    def openSession(self, sessionID, server, userID):
        """
        Die Methode createSession() soll einen Login durchführen und anschließend initial die
        Spielderdaten setzen.
        """

        self.__sessionID = sessionID
        self.__server = server
        self.__userID = userID
        
        self.__startTime = time.time()
        self.__endTime = self.__startTime + self.__lifetime
    
    
    def closeSession(self, wunr, server):
        """
        Die Methode closeSession() schließt die Session...
        """
        pass

    
    def getRemainingTime(self):
        """
        Die Methdoe gibt die verbleibende Zeit zurück, bis die Session ungültig wird.
        """
        return self.__endTime - time.time()
    
    def getSessionID(self):
        return self.__sessionID
    
    def getUserID(self):
        return self.__userID
    
    def getServer(self):
        return self.__server


        