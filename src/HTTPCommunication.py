#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from urllib import urlencode
import json, re, httplib2
from Cookie import SimpleCookie
from src.Session import Session
import yaml, time, logging


#Defines
HTTP_STATE_CONTINUE            = 100
HTTP_STATE_SWITCHING_PROTOCOLS = 101
HTTP_STATE_PROCESSING          = 102
HTTP_STATE_OK                  = 200
HTTP_STATE_FOUND               = 302 #moved temporarily

class HTTPConnection(object):
    """
    Mit der Klasse HTTPConnection wird eine HTTP-Verbindung realisiert, die alle
    Anfragen und Antworten verarbeitet.
    """
    
    def __init__(self):
        self.__webclient = httplib2.Http()
        self.__webclient.follow_redirects = False
        self.__userAgent = 'Opera/9.80 (Windows NT 6.1; Win64; x64) Presto/2.12.388 Version/12.17'
        self.__logHTTPConn = logging.getLogger('bot.HTTPConn')
        self.__Session = Session()
        self.__JWToken = None

    def __generateUserDataFromJSONContent(self, content):
        userData = {}
        userData['bar'] = str(content['bar'])
        userData['points'] = int(content['points'])
        userData['coins'] = int(content['coins'])
        userData['level'] = str(content['level'])
        userData['levelnr'] = int(content['levelnr'])
        userData['mail'] = int(content['mail'])
        userData['contracts'] = int(content['contracts'])
        userData['g_tag'] = str(content['g_tag'])
        userData['time'] = int(content['time'])
        return userData
    
    def __checkIfHTTPStateIsOK(self, response):
        if not (response['status'] == str(HTTP_STATE_OK)):
            raise HTTPStateError('HTTP Status ist nicht OK')

    def __generateJSONContentAndCheckForSuccess(self, content):
        jContent = json.loads(content)
        if (jContent['success'] == 1): return jContent
        else: raise JSONError()

    def __generateJSONContentAndCheckForOK(self, content):
        jContent = json.loads(content)
        if (jContent['status'] == 'ok'): return jContent
        else: raise JSONError()

    def __isFieldWatered(self, jContent, fieldID):

        oneDayInSeconds = (24*60*60) + 30 #30 s Sicherheit zur Serverzeit
        currentTimeInSeconds = time.time()
        waterDateInSeconds = int(jContent['water'][fieldID-1][1])

        if waterDateInSeconds == '0': return False #Wurde noch nie gegossen
        elif (currentTimeInSeconds - waterDateInSeconds) > oneDayInSeconds: return False
        else: return True


    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, plantSize):
        if (plantSize == '1x1'): return str(fieldID)
        if (plantSize == '2x1'): return str(fieldID) + ',' + str(fieldID + 1)
        if (plantSize == '1x2'): return str(fieldID) + ',' + str(fieldID + 17)
        if (plantSize == '2x2'): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        print 'Error der plantSize --> ' + plantSize

    
    def logIn(self, loginDaten):
        """
        Führt einen login durch und gibt alle gesammelten Daten für eine Session zurück.
        """
        #TODO: Rückgabewert definieren, derzeit int mit 0 (False) oder userID (True)
        parameter = urlencode({'do': 'login',
                            'server': 'server' + str(loginDaten.server),
                            'user': loginDaten.user,
                            'pass': loginDaten.password}) 
    
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Connection': 'Keep-Alive'}

        try:
            response, content = self.__webclient.request('http://www.wurzelimperium.de/dispatch.php', \
                                                         'POST', \
                                                         parameter, \
                                                         headers)

        except:
            print 'Fehler beim Anfordern eines Logins'
            return 0
        else:
            if not (response['status'] == str(HTTP_STATE_OK)):
                print 'Login fehlgeschlagen ' + response['status']
                return 0
            else:
                jContent = json.loads(content)

                #token extrahieren
                split = re.search(r'(http://.*/logw.php).*token=([a-f0-9]{32})', jContent['url'])
        
                if split:
                    #url           = split.group(1)
                    self.__JWToken = split.group(2)
                else:
                    print 'Fehler bei der Ermittlung des tokens'
        
                if (self.__JWToken == ''):
                    return 0

                response, content = self.__webclient.request(jContent['url'], 'GET')
                
                if (response['status'] == str(HTTP_STATE_FOUND)):
                    cookie = SimpleCookie(response['set-cookie'])
                    self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server), cookie['wunr'].value)
                    return cookie['wunr'].value
                else:
                    print 'Fehler bei der Öffnung der Session'
                    return 0


    def logOut(self):
        """

        """
        
        #TODO: Was passiert beim Logout einer bereits ausgeloggten Session
        
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID()}
        
        adresse = 'http://s'+str(self.__Session.getServer()) + '.wurzelimperium.de/main.php?page=logout'
        
        try: #content ist beim Logout leer
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
        except:
            print 'Fehler im HTTP Request der Funktion logOut()'
            return False
        else:
            if (response['status'] == str(HTTP_STATE_FOUND)):
                cookie = SimpleCookie(response['set-cookie'])
                if (cookie['PHPSESSID'].value == 'deleted'):
                    #Rücksetzaktionen
                    self.__JWToken = None
                    #TODO: python-phpSession killen nach erfolgreichem logout (destruktor)
                    print 'Logout erfolgreich'
                    return True
                else:
                    print 'session wurde nicht gelöscht'
                    return False
            else:
                print 'Response des Logouts != 302'
                return False
        
    def getNumberOfGardens(self):
        
        """
        Ermittelt die Anzahl der Gärten und gibt diese als int zurück. Konnte die Anzahl nicht ermittelt werden,
        wird -1 zurückgegeben.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=0&start=0&additional='+\
                  self.__Session.getUserID() + '&token=' + self.__JWToken
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)    
        except:
            print 'Fehler im HTTP Request der Funktion getNumberOfGardens()'
            return -1
        else:
            if (response['status'] == str(HTTP_STATE_OK)):
                jContent = json.loads(content)
                if (jContent['status'] == 'ok'):
                    result = False
                    for i in range(0, len(jContent['table'])):
                        sGartenAnz = str(jContent['table'][i].encode('utf-8'))   
                        if 'Gärten' in sGartenAnz:
                            sGartenAnz = sGartenAnz.replace('<tr>', '')
                            sGartenAnz = sGartenAnz.replace('<td>', '')
                            sGartenAnz = sGartenAnz.replace('</tr>', '')
                            sGartenAnz = sGartenAnz.replace('</td>', '')
                            sGartenAnz = sGartenAnz.replace('Gärten', '')
                            sGartenAnz = sGartenAnz.strip()
                            iGartenAnz = int(sGartenAnz)
                            result = True
                            break
                    if result:
                        return iGartenAnz
                    else:
                        print 'Anzahl der Gärten nicht gefunden.'
                        return -1
                else:
                    print 'Fehler bei der Auswertung der Gartenanzahl (Content)'
                    return -1
            else:
                print 'Fehler bei der Auswertung der Gartenanzahl (Response)'
                return -1

    def getUserName(self): 
        """
        Ermittelt den Usernamen auf Basis der userID und gibt diesen als str zurück. Konnte er nicht ermittelt werden,
        wird -1 zurückgegeben.
        """
    
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=0&start=0&additional='+\
                  self.__Session.getUserID() + '&token=' + self.__JWToken
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)    
        except:
            print 'Fehler im HTTP Request der Funktion getUserName()'
            return -1
        else:
            if (response['status'] == str(HTTP_STATE_OK)):
                jContent = json.loads(content)
                if (jContent['status'] == 'ok'):
                    result = False
                    for i in range(0, len(jContent['table'])):
                        sUserName = str(jContent['table'][i].encode('utf-8'))  
                        if 'Spielername' in sUserName:
                            sUserName = sUserName.replace('<tr>', '')
                            sUserName = sUserName.replace('<td>', '')
                            sUserName = sUserName.replace('</tr>', '')
                            sUserName = sUserName.replace('</td>', '')
                            sUserName = sUserName.replace('Spielername', '')
                            sUserName = sUserName.replace('&nbsp;', '')
                            sUserName = sUserName.strip()
                            result = True
                            break
                    if result:
                        return sUserName
                    else:
                        print 'Spielername nicht gefunden.'
                        return -1
                else:
                    print 'Fehler bei der Auswertung des Spielernames (Content)'
                    return -1
            else:
                print 'Fehler bei der Auswertung des Spielernamens (Response)'
                return -1

    
    def readUserDataFromServer(self):
        """
        
        """
        
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/menu-update.php'
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckSuccess(content)
        except:
            raise HTTPRequestError('Fehler im HTTP Request der Funktion getUserData()')
        else:
            return self.__generateUserDataFromJSONContent(jContent)


    def getFieldIDsAndPlantsizeToWater(self, iGarten):
        """
        Ermittelt alle bepflanzten Felder, die im Garten mit der Nummer iGarten wachsen und gibt diese zurück.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden='+str(iGarten)+'&token='+self.__JWToken

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            print jContent
        except:
            raise HTTPRequestError('Fehler im HTTP Request der Funktion getFieldsToWater()')
        else:
            plantsToBeWatered = {'fieldID':[], 'size':[]}
            for field in range(0, len(jContent['grow'])):
                
                plantedFieldID = jContent['grow'][field][0]
                plantSize = jContent['garden'][str(plantedFieldID)][9]
                #neededFields = self.getNumberOfFieldsFromSizeOfPlant(plantSize)
                
                if not self.__isFieldWatered(jContent, plantedFieldID):
                    fieldIDToBeWatered = jContent['water'][plantedFieldID-1][0]
                    plantsToBeWatered['fieldID'].append(fieldIDToBeWatered)
                    plantsToBeWatered['size'].append(plantSize)

            return plantsToBeWatered


    def waterField(self, iGarten, iField, sSize):
        
        """
        
        """

        sFieldsToWater = self.__getAllFieldIDsFromFieldIDAndSizeAsString(iField, sSize)
        
        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/save/wasser.php?feld[]='+str(iField)+'&felder[]='+sFieldsToWater+'&cid='+self.__JWToken+'&garden='+str(iGarten)

        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise HTTPRequestError('Fehler im HTTP Request der Funktion waterField()')
        else:
            content = content.replace('\n', ' ')
            content = content.replace('\t', ' ')
            yContent = yaml.load(content)
            if (yContent['success'] == 1):
                print yContent['felder']
                print '\n'
            else:
                print 'Fehler beim Giessen ' + str(yContent)
                return -1

    def waterGarden(self): #Wassergarten

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=watergardenGetGarden&token=' + self.__JWToken
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
        except:
            raise HTTPRequestError('Fehler im HTTP Request der Funktion waterField()')
        else:
            plantsToBeWatered = {'fieldID':[], 'size':[]}
            for field in range(0, len(jContent['grow'])):
                
                plantedFieldID = jContent['grow'][field][0]
                plantSize = jContent['garden'][str(plantedFieldID)][9]
                
                if not self.__isFieldWatered(jContent, plantedFieldID):
                    fieldIDToBeWatered = jContent['water'][plantedFieldID-1][0]
                    plantsToBeWatered['fieldID'].append(fieldIDToBeWatered)
                    plantsToBeWatered['size'].append(plantSize)

            return plantsToBeWatered

    def waterWatergardenField(self, iField, sSize):
        
        """
        
        """

        sFieldsToWater = self.__getAllFieldIDsFromFieldIDAndSizeAsString(iField, sSize)
        listFieldsToWater = sFieldsToWater.split(',')
        
        sFields = ''
        for i in listFieldsToWater:
            sFields += '&water[]='+str(i)

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=watergardenCache' + sFields + '&token='+self.__JWToken

        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
        except:
            raise HTTPRequestError('Fehler im HTTP Request der Funktion waterField()')
        else:
            content = content.replace('\n', ' ')
            content = content.replace('\t', ' ')
            yContent = yaml.load(content)
            if (yContent['status'] != 'ok'):
                print 'Fehler beim Giessen ' + str(yContent)
                return -1


    """
    
    def changeGarden(self, iGarten):

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__Session.getUserID(),\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden='+str(iGarten)+'&token='+self.__JWToken
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)    
        except:
            print 'Fehler im HTTP Request der Funktion waterField()'
            return -1
        else:
            pass
    """

    #TODO: Was passiert wenn ein Garten hinzukommt (parallele Sitzungen im Browser und Bot)? Globale Aktualisierungsfunktion?
        
class HTTPStateError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class JSONError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class HTTPRequestError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)