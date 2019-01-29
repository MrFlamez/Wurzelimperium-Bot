#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from src.Spieler import Spieler, Login
from src.HTTPCommunication import HTTPConnection
from src.Messenger import Messenger
from src.Garten import Garden
import logging


class WurzelBot(object):
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """

    def __init__(self):
        """
        
        """
        self.__logBot = logging.getLogger("bot")
        self.__logBot.setLevel(logging.DEBUG)
        self.__HTTPConn = HTTPConnection()
        self.Spieler = Spieler()
        self.Messenger = Messenger(self.__HTTPConn)
        self.Garten = []


    def __initGardens(self):
        """
        Ermittelt die Anzahl der Gärten und initialisiert alle.
        """
        try:
            tmpNumberOfGardens = self.__HTTPConn.getNumberOfGardens()
            self.Spieler.numberOfGardens = tmpNumberOfGardens
            for i in range(1, tmpNumberOfGardens + 1):
                self.Garten.append(Garden(self.__HTTPConn, i))
        except:
            raise


    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        if (sx == '1' and sy == '1'): return str(fieldID)
        if (sx == '2' and sy == '1'): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == '1' and sy == '2'): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == '2' and sy == '2'): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self.__logBot.debug('Error der plantSize --> sx: ' + sx + ' sy: ' + sy)


    def __getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als Integer-Liste zurück.
        """
        sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray
                        
        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])
            
        return listFields


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
            self.Spieler.setUserNameFromServer(self.__HTTPConn)
        except:
            self.__logBot.error('Username konnte nicht ermittelt werden.')


        try:
            self.Spieler.setUserDataFromServer(self.__HTTPConn)
        except:
            self.__logBot.error('UserDaten konnten nicht aktualisiert werden')

        try:
            self.__initGardens()
        except:
            self.__logBot.error('Anzahl der Gärten konnte nicht ermittelt werden.')
        
        try:
            tmpHoneyFarmAvailability = self.__HTTPConn.isHoneyFarmAvailable(self.Spieler.getLevelNr())
        except:
            self.__logBot.error('Verfügbarkeit der Imkerei konnte nicht ermittelt werden.')
        else:
            self.Spieler.setHoneyFarmAvailability(tmpHoneyFarmAvailability)

        try:
            tmpAquaGardenAvailability = self.__HTTPConn.isAquaGardenAvailable(self.Spieler.getLevelNr())
        except:
            self.__logBot.error('Verfügbarkeit des Wassergartens konnte nicht ermittelt werden.')
        else:
            self.Spieler.setAquaGardenAvailability(tmpAquaGardenAvailability)
        
        
        self.Spieler.accountLogin = loginDaten
        self.Spieler.setUserID(self.__HTTPConn.getUserID())


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
            self.Spieler.userData = userData


    def waterPlantsInAquaGarden(self):
        """
        Alle Pflanzen im Wassergarten werden bewässert.
        """
        if self.Spieler.isAquaGardenAvailable() == True:
            try:
                plants = self.__HTTPConn.getPlantsToWaterInAquaGarden()
                nPlants = len(plants['fieldID'])
                for i in range(0, nPlants):
                    sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                    self.__HTTPConn.waterPlantInAquaGarden(plants['fieldID'][i], sFields)
            except:
                self.__logBot.error('Wassergarten konnte nicht bewässert werden.')
            else:
                self.__logBot.info('Im Wassergarten wurden ' + str(nPlants) + ' Pflanzen gegossen.')


    def waterPlantsInAllGardens(self):
        """
        Alle Gärten des Spielers werden komplett bewässert.
        """
        for garden in self.Garten:
            garden.waterPlants()
        self.waterPlantsInAquaGarden()


    def writeMessagesIfMailIsConfirmed(self, recipients, subject, body):
        """
        Erstellt eine neue Nachricht, füllt diese aus und verschickt sie.
        recipients muss ein Array sein!.
        Eine Nachricht kann nur verschickt werden, wenn die E-Mail Adresse bestätigt ist.
        """
        if (self.Spieler.isEMailAdressConfirmed()):
            try:
                self.Messenger.writeMessage(self.Spieler.getUserName(), recipients, subject, body)
            except:
                self.__logBot.error('Konnte keine Nachricht verschicken.')
            else:
                pass

        
    def getEmptyFieldsOfAllGardens(self):
        """
        Gibt alle leeren Felder aller Gärten zurück.
        """
        #TODO: Wassergarten ergänzen
        emptyFields = []
        try:
            for garden in self.Garten:
                emptyFields.append(Garden.getEmptyFields())
        except:
            self.__logBot.error('Konnte leere Felder von Garten ' + str(garden.getID()) + ' nicht ermitteln.')
        else:
            pass
        
    def harvestAllGarden(self):
        #TODO: Wassergarten ergänzen
        try:
            for garden in self.Garten:
                garden.harvest()
        except:
            self.__logBot.error('Konnte nicht alle Gärten ernten.')
        else:
            pass


    def growPlantsInGardens(self, plantID, sx, sy):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        for garden in self.Garten:
            garden.growPlant(plantID, sx, sy)
            

    def test(self):
        #TODO: Für Testzwecke, kann später entfernt werden.
        #return self.__HTTPConn.getUsrList(1, 15000)
        #self.__HTTPConn.readStorageFromServer()
        pass






