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
    Mit der Klasse HTTPConnection werden alle anfallenden HTTP-Verbindungen verarbeitet.
    """
    
    def __init__(self):
        self.__webclient = httplib2.Http()
        self.__webclient.follow_redirects = False
        self.__userAgent = 'Opera/9.80 (Windows NT 6.1; Win64; x64) Presto/2.12.388 Version/12.17'
        self.__logHTTPConn = logging.getLogger('bot.HTTPConn')
        self.__Session = Session()
        self.__token = None
        self.__userID = None
        
    def __del__(self):
        self.__Session = None
        self.__token = None
        self.__userID = None
        

    def __generateUserDataFromJSONContent(self, content):
        """
        Status: kA
        """
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
        """
        Prüft, ob der Status der HTTP Anfrage OK ist.
        """
        if not (response['status'] == str(HTTP_STATE_OK)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht OK')

    def __checkIfHTTPStateIsFOUND(self, response):
        """
        Prüft, ob der Status der HTTP Anfrage FOUND ist.
        """
        if not (response['status'] == str(HTTP_STATE_FOUND)):
            self.__logHTTPConn.debug('HTTP State: ' + str(response['status']))
            raise HTTPStateError('HTTP Status ist nicht FOUND')

    def __generateJSONContentAndCheckForSuccess(self, content):
        """
        Status: kA
        """
        jContent = json.loads(content)
        if (jContent['success'] == 1): return jContent
        else: raise JSONError()

    def __generateJSONContentAndCheckForOK(self, content):
        """
        Aufbereitung und Prüfung der vom Server empfangenen Daten.
        """
        jContent = json.loads(content)
        if (jContent['status'] == 'ok'): return jContent
        else: raise JSONError()

    def __isFieldWatered(self, jContent, fieldID):
        """
        Status: kA
        """

        oneDayInSeconds = (24*60*60) + 30 #30 s Sicherheit zur Serverzeit
        currentTimeInSeconds = time.time()
        waterDateInSeconds = int(jContent['water'][fieldID-1][1])

        if waterDateInSeconds == '0': return False #Wurde noch nie gegossen
        elif (currentTimeInSeconds - waterDateInSeconds) > oneDayInSeconds: return False
        else: return True


    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, plantSize):
        """
        Status: kA
        """
        if (plantSize == '1x1'): return str(fieldID)
        if (plantSize == '2x1'): return str(fieldID) + ',' + str(fieldID + 1)
        if (plantSize == '1x2'): return str(fieldID) + ',' + str(fieldID + 17)
        if (plantSize == '2x2'): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        print 'Error der plantSize --> ' + plantSize


    def __getTokenFromURL(self, url):
        """
        Ermittelt aus einer übergebenen URL den security token.
        """
        #token extrahieren
        split = re.search(r'(http://.*/logw.php).*token=([a-f0-9]{32})', url)
        
        iErr = 0
        if split:
            tmpToken = split.group(2)
            if (tmpToken == ''):
                iErr = 1
        else:
            iErr = 1
            
        if (iErr == 1):
            self.__logHTTPConn.debug(tmpToken)
            raise JSONError('Fehler bei der Ermittlung des tokens')
        else:
            self.__token = tmpToken


    def __getUserNameFromJSONContent(self, jContent):
        """
        Sucht im übergebenen JSON Objekt nach dem Usernamen und gibt diesen zurück.
        """
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
            self.__logHTTPConn.debug(jContent['table'])
            raise JSONError('Spielername nicht gefunden.')


    def __getNumberOfGardensFromJSONContent(self, jContent):
        """
        Sucht im übergebenen JSON Objekt nach der Anzahl der Gärten und gibt diese zurück.
        """
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
            self.__logHTTPConn.debug(jContent['table'])
            raise JSONError('Anzahl der Gärten nicht gefunden.')
        
    def __checkIfSessionIsDeleted(self, cookie):
        """
        Prüft, ob die Session gelöscht wurde.
        """
        if not (cookie['PHPSESSID'].value == 'deleted'):
            self.__logHTTPConn.debug('SessionID: ' + cookie['PHPSESSID'].value)
            raise HTTPRequestError('Session wurde nicht gelöscht')


    def logIn(self, loginDaten):
        """
        Führt einen login durch und öffnet eine Session.
        """

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
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            self.__getTokenFromURL(jContent['url'])
            
            response, content = self.__webclient.request(jContent['url'], 'GET')
            self.__checkIfHTTPStateIsFOUND(response)
        except:
            raise
        else:
            cookie = SimpleCookie(response['set-cookie'])
            self.__Session.openSession(cookie['PHPSESSID'].value, str(loginDaten.server))
            self.__userID = cookie['wunr'].value

            
    def getUserID(self):
        """
        Gibt die wunr als userID zurück die beim Login über das Cookie erhalten wurde.
        """
        return self.__userID


    def logOut(self):
        """
        Logout des Spielers inkl. Löschen der Session.
        """
        #TODO: Was passiert beim Logout einer bereits ausgeloggten Session
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + 'wunr=' + self.__userID}
        
        adresse = 'http://s'+str(self.__Session.getServer()) + '.wurzelimperium.de/main.php?page=logout'
        
        try: #content ist beim Logout leer
            response, content = self.__webclient.request(adresse, 'GET', headers=headers)
            self.__checkIfHTTPStateIsFOUND(response)
            cookie = SimpleCookie(response['set-cookie'])
            self.__checkIfSessionIsDeleted(cookie)
        except:
            raise
        else:
            self.__del__()

        
    def getNumberOfGardens(self):
        """
        Ermittelt die Anzahl der Gärten und gibt diese als int zurück.
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=0&start=0&additional='+\
                  self.__userID + '&token=' + self.__token
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            iNumber = self.__getNumberOfGardensFromJSONContent(jContent)
        except:
            raise
        else:
            return iNumber


    def getUserName(self): 
        """
        Ermittelt den Usernamen auf Basis der userID und gibt diesen als str zurück.
        """
    
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=statsGetStats&which=0&start=0&additional='+\
                  self.__userID + '&token=' + self.__token
        
        try:
            response, content = self.__webclient.request(adresse, 'GET', headers = headers)
            self.__checkIfHTTPStateIsOK(response)
            jContent = self.__generateJSONContentAndCheckForOK(content)
            userName = self.__getUserNameFromJSONContent(jContent)
        except:
            raise
        else:
            return userName

    
    def readUserDataFromServer(self):
        """
        Status: kA
        """
        
        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
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
        Status: kA
        """

        headers = {'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden='+str(iGarten)+'&token='+self.__token

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
        Status: kA
        """

        sFieldsToWater = self.__getAllFieldIDsFromFieldIDAndSizeAsString(iField, sSize)
        
        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/save/wasser.php?feld[]='+str(iField)+'&felder[]='+sFieldsToWater+'&cid='+self.__token+'&garden='+str(iGarten)

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
        """
        Status: kA
        """

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=watergardenGetGarden&token=' + self.__token
        
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
        Status: kA
        """

        sFieldsToWater = self.__getAllFieldIDsFromFieldIDAndSizeAsString(iField, sSize)
        listFieldsToWater = sFieldsToWater.split(',')
        
        sFields = ''
        for i in listFieldsToWater:
            sFields += '&water[]='+str(i)

        headers = {'User-Agent': self.__userAgent,\
                   'Cookie': 'PHPSESSID=' + self.__Session.getSessionID() + '; ' + \
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=watergardenCache' + sFields + '&token='+self.__token

        
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
                             'wunr=' + self.__userID,\
                   'X-Requested-With': 'XMLHttpRequest',\
                   'Connection': 'Keep-Alive'}
        adresse = 'http://s' + str(self.__Session.getServer()) + '.wurzelimperium.de/ajax/ajax.php?do=changeGarden&garden='+str(iGarten)+'&token='+self.__token
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