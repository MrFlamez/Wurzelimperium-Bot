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
    
    __HTTPConn = HTTPConnection()
    __Spieler = Spieler()
    #TODO: __logging?
    __Parser = None #TODO: Parser als dict anlegen?


    def __init__(self):
        logging.basicConfig(filename='wurzelbot.log', level=logging.INFO)


    def start(self, server, user, pw):
        """
        Diese Funktion startet den Wurzelbot durch folgenden Aktionen
        - setzt den AccountLogin in der Spieler-Klasse
        - öffnet eine Session
        """
        logging.info('Starte Wurzelbot')
        loginDaten = Login(server=server, user=user, password=pw)
        userID = self.__HTTPConn.logIn(loginDaten)
        userName = self.__HTTPConn.getUserName()
        #TODO: Zuweisung der wunr sieht sehr ungünstig aus, elegantere Lösung?
        if (userID != 0):
            self.__Spieler.accountLogin = loginDaten
            self.__Spieler.userName = userName
            self.__Spieler.userID = userID
        else:
            print 'Fehler beim Starten des Bots'

        self.__Spieler.GartenAnzahl = self.__HTTPConn.getNumberOfGardens()


    def stop(self):
        #TODO: Name der Methode ändern
        self.__HTTPConn.logOut()
        logging.info('Beende Wurzelbot')


    def updateUserData(self):
        """
        Ermittelt die Userdaten und setzt sie in der Spielerklasse.
        """
        try:
            userData = self.__HTTPConn.readUserDataFromServer()
        except:
            print 'UserDaten konnten nicht aktualisiert werden'
        else:
            self.__Spieler.userData = userData


    def waterPlantsInGarden(self, gardenID):
        """
        Ein Garten mit der gardenID wird komplett bewässert.
        """
        # Zurückgegebene Felderindizes für Pflanzen der Größe 1-, 2- und 4-Felder
        # Wichtig beim Gießen; dort müssen alle Indizes angegeben werden.
        # (Sowohl die mit x als auch die mit o gekennzeichneten).
        # +---+   +---+---+   +---+---+
        # | x |   | x | o |   | x | o |
        # +---+   +---+---+   +---+---+
        #                     | o | o |
        #                     +---+---+
        plants = self.__HTTPConn.getFieldIDsAndPlantsizeToWater(gardenID)
        for i in range(0, len(plants['fieldID'])):
            self.__HTTPConn.waterField(gardenID, plants['fieldID'][i], plants['size'][i])
            
    def waterPlantsInWatergarden(self):
        """
        Alle Pflanzen im Wassergarten werden bewässert.
        """
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


    def test(self):
        #TODO: Für Testzwecke, kann später entfernt werden.       
        pass