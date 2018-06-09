#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017
@author: MrFlamez
'''
from collections import namedtuple

Login = namedtuple('Login', ['server', 'user', 'password'])

class Spieler():
    
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Spieler.
    """
    
    accountLogin = None
    userName = None
    userID = None
    GartenAnzahl = None
    userData = None
    imkerei = None

    def __init__(self):
        pass

    