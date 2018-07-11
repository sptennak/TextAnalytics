# -*- coding: utf-8 -*-
"""
Created on Fri May 18 22:15:35 2018

@author: Sumudu Tennakoon
"""

from watson_developer_cloud import NaturalLanguageUnderstandingV1, WatsonException, WatsonApiException
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, RelationsOptions
import pandas as pd
import numpy as np
from timeit import default_timer as timer
import multiprocessing
import sys

###############################################################################
def IAM_Auth(APIKey, Version):
	ServiceAuthentication = NaturalLanguageUnderstandingV1(
		version= Version,
		iam_api_key= APIKey
	)
	ServiceAuthentication.set_url('https://gateway-fra.watsonplatform.net/natural-language-understanding/api')
    #To prevent IBM from accessing user input and Watson responses... https://www.ibm.com/watson/developercloud/conversation/api/v1/python.html?python#data-collection
    ServiceAuthentication.set_default_headers({'x-watson-learning-opt-out': "true"}) 
	return ServiceAuthentication

def Basic_Auth(UserName, Password, Version)
	ServiceAuthentication = NaturalLanguageUnderstandingV1(
		version= Version,
		username= UserName,
		password= Password
	)
	ServiceAuthentication.set_url('https://gateway-fra.watsonplatform.net/natural-language-understanding/api')
    #To prevent IBM from accessing user input and Watson responses... https://www.ibm.com/watson/developercloud/conversation/api/v1/python.html?python#data-collection
    ServiceAuthentication.set_default_headers({'x-watson-learning-opt-out': "true"}) 
	return ServiceAuthentication
###############################################################################

def TextNLU(ServiceAuthentication, TextID, Text, ModelID=None, Emotion=False, Sentiment=False, Mentions =False, EntityLimit=50, TextLimit=50000, ReturnText=True):
	Notes = ''	
    try:
        Response = ServiceAuthentication.analyze(
            text=Text,
            features=Features(
                relations=RelationsOptions(
                  model = ModelID,
                ),
                entities=EntitiesOptions(
                  emotion=Emotion,
                  sentiment=Sentiment,
				  mentions=Mentions,
                  model = ModelID,  
                  limit=EntityLimit				  
                ),     
            ),
			limit_text_characters = TextLimit, #https://console.bluemix.net/docs/services/natural-language-understanding/usage-limits.html#usage-limits
            return_analyzed_text=ReturnText    
        )
		Notes='RECIEVED'
    except WatsonException:  
		Notes = str(WatsonException)
		print('Watson NLU: WatsonException [{}]'.format(Response))
	except WatsonApiException:
		Notes = str(WatsonApiException)
		print('Watson NLU: WatsonApiException [{}]'.format(Response))
	except WatsonInvalidArgument:
		Notes = str(WatsonInvalidArgument)
		print('Watson NLU: WatsonInvalidArgument [{}]'.format(Response))	
	except:
		Notes = sys.exc_info()[0]
		print('Watson NLU: Unexpected error [{}]'.format(Response))
	Notes = 'NLU:'+Notes
	
	# Process Response Header
	WatsonResponseHeader = pd.DataFrame({'TextID':[TextID]})
    try:      	 
        WatsonResponseHeader['Language'] = Response['language']
        WatsonResponseHeader['CharacterCount'] = Response['usage']['text_characters'] #Number of characters processed
        WatsonResponseHeader['NLUUnits'] = Response['usage']['text_units']	#Number of characters processed	
		WatsonResponseHeader['Features'] = Response['usage']['features'] #Number of features used, such as entities, sentiment, etc.
		WatsonResponseHeader['EntitiesCount'] = len(Response['entities'])
        WatsonResponseHeader['AnalyzedText'] = Response['analyzed_text']		
    except:
		Notes= Notes+ '\tHEADER:' + sys.exc_info()[0]		
	
	
	# Process Response Details	
    try:
        if len(Response['entities']) != 0:
            WatsonResponseDetail = pd.DataFrame(Response['entities'])
			WatsonResponseDetail.insert(0, 'EmailID', EmailID)
        else:
            raise Exception('NO ENTITIES FOUND')
    except:
        Notes= Notes+ '\DETAIL:' + sys.exc_info()[0]
		WatsonResponseDetail = pd.DataFrame()
		
	WatsonResponseHeader['Notes'] = Notes	
	
	return WatsonResponseHeader, WatsonResponseDetail
	