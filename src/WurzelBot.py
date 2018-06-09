#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from src.Spieler import Spieler, Login
from src.HTTPCommunication import HTTPConnection
import logging


class WurzelBot(object):
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """
    
    #__Parser = None


    def __init__(self):
        """
        
        """
        self.__logBot = logging.getLogger("bot")
        self.__logBot.setLevel(logging.DEBUG)
        self.__HTTPConn = HTTPConnection()
        self.__Spieler = Spieler()
        

    def launchBot(self, server, user, pw):
        """
        Diese Methode startet und initialisiert den Wurzelbot. Dazu wird ein Login mit den
        übergebenen Logindaten durchgeführt und alles nötige initialisiert.
        """
        self.__logBot.info('Starte Wurzelbot')
        loginDaten = Login(server=server, user=user, password=pw)
        try:
            self.__HTTPConn.logIn(loginDaten)
        except:
            self.__logBot.error('Problem beim Starten des Wurzelbots.')
            return
        
        try:
            userName = self.__HTTPConn.getUserName()
        except:
            self.__logBot.error('Username konnte nicht ermittelt werden.')
        else:
            self.__Spieler.userName = userName

        try:
            nGarden = self.__HTTPConn.getNumberOfGardens()
        except:
            self.__logBot.error('Anzahl der Gärten konnte nicht ermittelt werden.')
        else:
            self.__Spieler.GartenAnzahl = nGarden
        
        try:
            bBee = self.__HTTPConn.isBeekeepingAvailable()
        except:
            self.__logBot.error('Verfügbarkeit der Imkerei konnte nicht ermittelt werden.')
        else:
            self.__Spieler.imkerei = bBee
        
        
        self.__Spieler.accountLogin = loginDaten
        self.__Spieler.userID = self.__HTTPConn.getUserID()


    def exitBot(self):
        """
        Diese Methode beendet den Wurzelbot geordnet und setzt alles zurück.
        """
        self.__logBot.info('Beende Wurzelbot')
        try:
            self.__HTTPConn.logOut()
        except:
            self.__logBot.error('Wurzelbot konnte nicht korrekt beendet werden.')
        else:
            self.__logBot.info('Logout erfolgreich.')


    def updateUserData(self):
        """
        Ermittelt die Userdaten und setzt sie in der Spielerklasse.
        """
        try:
            userData = self.__HTTPConn.readUserDataFromServer()
        except:
            self.__logBot.error('UserDaten konnten nicht aktualisiert werden')
        else:
            self.__Spieler.userData = userData


    def waterPlantsInGarden(self, gardenID):
        """
        Ein Garten mit der gardenID wird komplett bewässert.
        """
        # Zurückgegebene Felderindizes (x) für Pflanzen der Größe 1-, 2- und 4-Felder.
        # Wichtig beim Gießen; dort müssen alle Indizes angegeben werden.
        # (Sowohl die mit x als auch die mit o gekennzeichneten).
        # x: fieldID
        # o: ergänzte Felder anhand der size
        # +---+   +---+---+   +---+---+
        # | x |   | x | o |   | x | o |
        # +---+   +---+---+   +---+---+
        #                     | o | o |
        #                     +---+---+
        self.__logBot.info('Gieße alle Pflanzen im Garten ' + str(gardenID) + '.')
        try:
            plants = self.__HTTPConn.getFieldIDsAndPlantsizeToWater(gardenID)
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                self.__HTTPConn.waterField(gardenID, plants['fieldID'][i], plants['size'][i])
                print (str(i+1) + ' von ' + str(nPlants)) #TODO: Kann später entfernt werden
        except:
            self.__logBot.error('Garten ' + str(gardenID) + ' konnte nicht bewässert werden.')
        else:
            self.__logBot.info('Im Garten ' + str(gardenID) + ' wurden ' + str(nPlants) + ' Pflanzen gegossen.')


    def waterPlantsInWatergarden(self):
        """
        Alle Pflanzen im Wassergarten werden bewässert.
        Status: kA
        """
        #TODO: Maintenance
        try:
            plants = self.__HTTPConn.waterGarden()
        except:
            logging.warning('Kein Wassergarten vorhanden')
        else:
            for i in range(0, len(plants['fieldID'])):
                self.__HTTPConn.waterWatergardenField(plants['fieldID'][i], plants['size'][i])


    def waterPlantsInAllGardens(self):
        """
        Alle Gärten des Spielers werden komplett bewässert.
        """
        for gardenID in range(1, self.__Spieler.GartenAnzahl + 1):
            self.waterPlantsInGarden(gardenID)
        #TODO: Wassergarten ergänzen


    def test(self):
        #TODO: Für Testzwecke, kann später entfernt werden.
        self.__HTTPConn.isTest()


