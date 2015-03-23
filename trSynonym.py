#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
from bs4 import BeautifulSoup
from mechanize import Browser
import xml.etree.ElementTree as ET
import os.path

# TODO: 
# Writing to local archive should be alphabetic.

# Dictionary information:
# id: descriptive
# form: form name
# grap: type of where results appear
# inputField: input field id of given form
# type: how identified given grap
# url: url address where dictionary form exists
# value: value of given type of given grap
onlineDictionaries = (
{
	'id':'TDK',
    'form': 'lehcelerform',
    'grap': 'td',
    'inputField': 'keyword',
    'type': 'class',
    'url': 'http://tdk.org.tr/index.php?option=com_esanlamlar&view=esanlamlar',
    'value': 'meaning'
},
{
	'id':'DEU',
    'form': 'ctl01',
    'grap': 'font',
    'inputField': 'TextBox1',
    'type': 'color',
    'url': 'http://nlpapps.cs.deu.edu.tr/esveyakin/sonuc.aspx',
    'value': 'CadetBlue'
})

storageName = "mySynonym.xml" # local archive file name
localDictName = "kelime-esanlamlisi.txt" # local dictionary file name
fileArgumentTag = "-f"	# tag for loading file
startupForXML = "<data>\n\t<word value=\"bilgisayar\">\n\t\t<synonym id=\"0\" dict=\"TDK\">elektronik beyin</synonym>\n\t\t<synonym id=\"1\" dict=\"google\">kompiter</synonym>\n\t</word>\n</data>"

##############################
#####  TURKISH SYNONYM  ######
##############################

def writeElementToXMLFile(element, isExist):
	root = mySynonym.getroot()
	if (not isExist):
	    root.append(element)
	prettyPrintToXML(root)
	mySynonym.write(storageName)

# onlineSearch: Looking for word in online dictionaries.
def onlineSearch(word):
	myBrowser = Browser()
	newWord, isExist = isWordExist(word)
	synonymID = len(newWord)
	
	for dict in onlineDictionaries:
		myBrowser.open(dict['url'])
		myBrowser.select_form(name = dict['form'])
		myBrowser[dict['inputField']] = word
		response = myBrowser.submit()    
		html = myBrowser.response().read()
		soup = BeautifulSoup(html)
		cols = soup.findAll(dict['grap'], attrs={dict['type'] : dict['value']})
		if (len(cols) != 0 and not isSynonymExist(newWord, cols[0].renderContents())):
		    storeResult(newWord, dict['id'], str(synonymID), cols[0].renderContents())
		    synonymID += 1
		elif (len(cols) == 0):
			print ("no result from " +  dict['id'] + " dictionary for " + "\"" + word + "\"" )
	if (len(newWord) != 0):
		writeElementToXMLFile(newWord, isExist)
	
# localSearch: Looking for argument in local dictionary.
def localSearch(word):
    localDict = open(localDictName, "r")
    newWord, isExist = isWordExist(word)
    synonymID = len(newWord)
    
    for line in localDict:
        if (word == line.split('\t')[0] and not isSynonymExist(newWord, line.split('\t')[1].split('\n')[0]) ):
            storeResult(newWord, 'localDict', str(synonymID), line.split('\t')[1].split('\n')[0])
            synonymID += 1
            
    if (len(newWord) != 0):
        writeElementToXMLFile(newWord, isExist)

# prettyPrintToXML: Writing to XML is demanded to be indented.
def prettyPrintToXML(elem, level=0):
	#	http://effbot.org/zone/element-lib.htm#prettyprint
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            prettyPrintToXML(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            		
# analyzeFile: Input file is enhanced for words in it.
def analyzeFile(_inputFile):
	inputFile = open(_inputFile, "r")
	for line in inputFile:
		for word in line.split():
			onlineSearch(word)
			localSearch(word)

# storeResult: Enhanced words are stored in Element Tree object.
def storeResult(newWord, dictionary, synonymID, result):
	newWordSynonym = ET.SubElement(newWord, 'synonym')
	newWordSynonym.attrib = {'id': synonymID, 'dict': dictionary}
	newWordSynonym.text = result.decode('utf8') # to print turkish chars

# isWordExist: If given word is enhanced before return it, else create new one.
def isWordExist(word):
	root = mySynonym.getroot()
	for child in root:
		if (child.attrib['value'].encode('utf8') == word):
			return child, True
	newWord = ET.Element('word')
	newWord.attrib = {'value': word.decode('utf8')}
	return newWord, False
	
# isSynonymExist: In a given Element Tree, has synonym exist already.
def isSynonymExist(newWord, result):
    for child in newWord:
        if (child.text.encode('utf8') == result):
            return True
    return False
    
##############################
#########   MAIN   ###########
##############################

if (not os.path.isfile(storageName)):
	myfile = open(storageName, "w")
	myfile.write(startupForXML)
	myfile.close()

mySynonym = ET.parse(storageName) 

if (sys.argv[1] == fileArgumentTag):   
    analyzeFile(sys.argv[2])
else:
	onlineSearch(sys.argv[1])
	localSearch(sys.argv[1])
