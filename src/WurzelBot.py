#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from src.Spieler import Spieler, Login
from src.HTTPCommunication import HTTPConnection
from src.Messenger import Messenger
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
        self.Messenger = Messenger(self.__HTTPConn)


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
            self.__Spieler.setUserNameFromServer(self.__HTTPConn)
        except:
            self.__logBot.error('Username konnte nicht ermittelt werden.')


        try:
            self.__Spieler.setUserDataFromServer(self.__HTTPConn)
        except:
            self.__logBot.error('UserDaten konnten nicht aktualisiert werden')


        try:
            tmpNumberOfGardens = self.__HTTPConn.getNumberOfGardens()
        except:
            self.__logBot.error('Anzahl der Gärten konnte nicht ermittelt werden.')
        else:
            self.__Spieler.numberOfGardens = tmpNumberOfGardens
        
        try:
            tmpHoneyFarmAvailability = self.__HTTPConn.isHoneyFarmAvailable(self.__Spieler.userData['levelnr'])
        except:
            self.__logBot.error('Verfügbarkeit der Imkerei konnte nicht ermittelt werden.')
        else:
            self.__Spieler.setHoneyFarmAvailability(tmpHoneyFarmAvailability)

        try:
            tmpAquaGardenAvailability = self.__HTTPConn.isAquaGardenAvailable(self.__Spieler.userData['levelnr'])
        except:
            self.__logBot.error('Verfügbarkeit des Wassergartens konnte nicht ermittelt werden.')
        else:
            self.__Spieler.setAquaGardenAvailability(tmpAquaGardenAvailability)
        
        
        self.__Spieler.accountLogin = loginDaten
        self.__Spieler.setUserID(self.__HTTPConn.getUserID())


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
            plants = self.__HTTPConn.getPlantsToWaterInGarden(gardenID)
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                self.__HTTPConn.waterPlantInGarden(gardenID, plants['fieldID'][i], sFields)
        except:
            self.__logBot.error('Garten ' + str(gardenID) + ' konnte nicht bewässert werden.')
        else:
            self.__logBot.info('Im Garten ' + str(gardenID) + ' wurden ' + str(nPlants) + ' Pflanzen gegossen.')


    def waterPlantsInAquaGarden(self):
        """
        Alle Pflanzen im Wassergarten werden bewässert.
        """
        if self.__Spieler.isAquaGardenAvailable() == True:
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
        for gardenID in range(1, self.__Spieler.numberOfGardens + 1):
            self.waterPlantsInGarden(gardenID)
        self.waterPlantsInAquaGarden()


    def writeMessagesIfMailIsConfirmed(self, recipients, subject, body):
        """
        Erstellt eine neue Nachricht, füllt diese aus und verschickt sie.
        recipients muss ein Array sein!.
        Eine Nachricht kann nur verschickt werden, wenn die E-Mail Adresse bestätigt ist.
        """
        if (self.__Spieler.isEMailAdressConfirmed()):
            try:
                self.Messenger.writeMessage(self.__Spieler.getUserName(), recipients, subject, body)
            except:
                self.__logBot.error('Konnte keine Nachricht verschicken.')
            else:
                pass
        
    def getEmptyFieldsOfGarden(self, gardenID):
        """
        Gibt alle leeren Felder eines Gartens mit der gardenID zurück.
        """
        try:
            self.__HTTPConn.getEmptyFields(gardenID)
        except:
            self.__logBot.error('Konnte leere Felder von Garten ' + str(gardenID) + ' nicht ermitteln.')
        else:
            pass
        
    def getEmptyFieldsOfAllGardens(self):
        """
        Gibt alle leeren Felder aller Gärten zurück.
        """
        #TODO: Wassergarten ergänzen
        emptyFields = []
        try:
            for gardenID in range(1, self.__Spieler.numberOfGardens + 1):
                emptyFields.append(self.__HTTPConn.getEmptyFields(gardenID))
        except:
            self.__logBot.error('Konnte leere Felder von Garten ' + str(gardenID) + ' nicht ermitteln.')
        else:
            pass
        
    def harvestAllGarden(self):
        #TODO: Wassergarten ergänzen
        try:
            for gardenID in range(1, self.__Spieler.numberOfGardens + 1):
                self.__HTTPConn.harvestGarden(gardenID)
        except:
            self.__logBot.error('Konnte nicht alle Gärten ernten.')
        else:
            pass


    def __isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, maxFields, lenX, sx):
        if not (fieldID in emptyFields): return False
        if not ((maxFields - fieldID)%lenX >= int(sx) - 1): return False
        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)
        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True
        
        
    def growPlantInGarden(self, gardenID, plantID, sx, sy):
        
        maxFields = 204
        lenX = 17
        
        sx = str(sx)
        sy = str(sy)
        
        emptyFields = self.__HTTPConn.getEmptyFields(gardenID)
        
        for field in range(1, 205):
            
            fieldsToPlant = self.__getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)
            
            if (self.__isPlantGrowableOnField(field, emptyFields, fieldsToPlant, maxFields, lenX, sx)):
                fields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
                self.__HTTPConn.growPlant(field, plantID, gardenID, fields)
                fieldsToPlantSet = set(fieldsToPlant)
                emptyFieldsSet = set(emptyFields)
                tmpSet = emptyFieldsSet - fieldsToPlantSet
                emptyFields = list(tmpSet)


    def growPlantInAllGardens(self, plantID, sx, sy):

        for gardenID in range(1, self.__Spieler.numberOfGardens + 1):
            self.growPlantInGarden(self, gardenID, plantID, sx, sy)
            

    def test(self):
        #TODO: Für Testzwecke, kann später entfernt werden.
        #return self.__HTTPConn.getUsrList(1, 15000)
        #self.__HTTPConn.readStorageFromServer()
        pass






