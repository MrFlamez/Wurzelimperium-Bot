#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class Garden():
    
    __lenX = 17
    __lenY = 12
    __nMaxFields = __lenX * __lenY
    
    def __init__(self, httpConnection, gardenID):
        self.__httpConn = httpConnection
        self.__id = gardenID
        self.__logGarden = logging.getLogger('bot.Garden_' + str(gardenID))
        self.__logGarden.setLevel(logging.DEBUG)

    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        if (sx == 1 and sy == 1): return str(fieldID)
        if (sx == 2 and sy == 1): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == 1 and sy == 2): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == 2 and sy == 2): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self.__logGarden.debug('Error der plantSize --> sx: ' + str(sx) + ' sy: ' + str(sy))


    def __getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als Integer-Liste zurück.
        """
        sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray
                        
        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])
            
        return listFields
    
    def __isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, sx):
        """
        Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist.
        """
        #Feld darf nicht besetzt sein
        if not (fieldID in emptyFields): return False
        
        #
        if not ((self.__nMaxFields - fieldID)%self.__lenX >= sx - 1): return False
        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)
        
        #
        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True

    def getID(self):
        """
        Gibt die Garten ID aus dem Spiel zurück.
        """
        return self.__id

    def waterPlants(self):
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
        self.__logGarden.info('Gieße alle Pflanzen im Garten ' + str(self.__id) + '.')
        try:
            plants = self.__httpConn.getPlantsToWaterInGarden(self.__id)
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                self.__httpConn.waterPlantInGarden(self.__id, plants['fieldID'][i], sFields)
        except:
            self.__logGarden.error('Garten ' + str(self.__id) + ' konnte nicht bewässert werden.')
        else:
            self.__logGarden.info('Im Garten ' + str(self.__id) + ' wurden ' + str(nPlants) + ' Pflanzen gegossen.')
            
    def getEmptyFields(self):
        """
        Gibt alle leeren Felder des Gartens zurück.
        """
        try:
            tmpEmptyFields = self.__httpConn.getEmptyFieldsOfGarden(self.__id)
        except:
            self.__logGarden.error('Konnte leere Felder von Garten ' + str(self.__id) + ' nicht ermitteln.')
        else:
            return tmpEmptyFields

    def harvest(self):
        """
        Erntet alles im Garten.
        """
        try:
            self.__httpConn.harvestGarden(self.__id)
        except:
            raise
        else:
            pass

    def growPlant(self, plantID, sx, sy):
        """
        Pflanzt eine Pflanze beliebiger Größe an.
        """
        #TODO: Soll nur so viele anpflanzen wie gewünscht (neuer Übergabeparameter)
        #TODO: Soll nur so viele anfpflanzen wie verfügbar (Muss im Wurzelbot geprüft werden)
        
        emptyFields = self.getEmptyFields()
        
        for field in range(1, self.__nMaxFields + 1):
            
            fieldsToPlant = self.__getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)
            
            if (self.__isPlantGrowableOnField(field, emptyFields, fieldsToPlant, sx)):
                fields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
                self.__httpConn.growPlant(field, plantID, self.__id, fields)
                fieldsToPlantSet = set(fieldsToPlant)
                emptyFieldsSet = set(emptyFields)
                tmpSet = emptyFieldsSet - fieldsToPlantSet
                emptyFields = list(tmpSet)


