# -*- coding: utf-8 -*-
"""
Created on Fri May 18 22:15:35 2018

@author: Sumudu Tennakoon
References:
[1] https://www.ibm.com/watson/developercloud/natural-language-understanding/api/v1/
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

def Basic_Auth(UserName, Password, Version):
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
    except:
        EXP = sys.exc_info()
        Notes = str(EXP[0])+'['+''.join(EXP[1].args)+']'
    Notes = 'NLU:'+Notes

    # Process Response Header
    WatsonResponseHeader = pd.DataFrame({'TextID':[TextID]})
    try:      	 
        WatsonResponseHeader['language'] = Response['language']
        WatsonResponseHeader['text_characters'] = Response['usage']['text_characters'] #Number of characters processed
        WatsonResponseHeader['text_units'] = Response['usage']['text_units']	#Number of characters processed	
        WatsonResponseHeader['features'] = Response['usage']['features'] #Number of features used, such as entities, sentiment, etc.
        WatsonResponseHeader['entities'] = len(Response['entities'])
        WatsonResponseHeader['analyzed_text'] = Response['analyzed_text']		
    except:
        EXP = sys.exc_info()
        Notes= Notes+ '\tHEADER:' + str(EXP[0])+'['+''.join(EXP[1].args)+']'	


    # Process Response Details	
    try:
        if len(Response['entities']) != 0:
            WatsonResponseDetail = pd.DataFrame(Response['entities'])
            WatsonResponseDetail.insert(0, 'TextID', TextID)
            if 'sentiment' in WatsonResponseDetail.columns:
                Split= WatsonResponseDetail.sentiment.apply(pd.Series)
                WatsonResponseDetail['sentiment_'+Split.columns]= Split
                WatsonResponseDetail.drop('sentiment', axis=1, inplace=True)
        else:
            raise Exception('NO ENTITIES FOUND')
    except:
        EXP = sys.exc_info()
        Notes= Notes+ '\tDETAIL:' + str(EXP[0])+'['+''.join(EXP[1].args)+']'	
        WatsonResponseDetail = pd.DataFrame()

    WatsonResponseHeader['Notes'] = Notes	

    return WatsonResponseHeader, WatsonResponseDetail