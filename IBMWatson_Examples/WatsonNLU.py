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
def IAM_Auth(APIKey, Version='2018-03-16'):
    ServiceAuthentication = NaturalLanguageUnderstandingV1(
        version= Version,
        iam_api_key= APIKey
    )
    ServiceAuthentication.set_url('https://gateway-fra.watsonplatform.net/natural-language-understanding/api')
    #To prevent IBM from accessing user input and Watson responses... https://www.ibm.com/watson/developercloud/conversation/api/v1/python.html?python#data-collection
    ServiceAuthentication.set_default_headers({'x-watson-learning-opt-out': "true"}) 
    return ServiceAuthentication

def Basic_Auth(UserName, Password, Version='2018-03-16'):
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

###############################################################################
# GUI
###############################################################################
import tkinter as tk #(https://wiki.python.org/moin/TkInter)
from tkinter import filedialog
from tkinter import scrolledtext
import configparser #(https://docs.python.org/3.4/library/configparser.html)
import traceback

class ApplicationWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.UserName = tk.StringVar()
        self.Password = tk.StringVar()
        self.APIKey = tk.StringVar()
        self.Version = tk.StringVar()
        self.ModelID = tk.StringVar()
        self.ConfigFile = tk.StringVar()
        self.InputTextFile = tk.StringVar()
        self.Input = tk.StringVar()
        self.CreateWidgets()        

    def CreateWidgets(self):
        #Menu
        MenuBar = tk.Menu(self.master)
        self.master.config(menu=MenuBar)
        
        FileMenu = tk.Menu(MenuBar)
        MenuBar.add_cascade(label='File', menu=FileMenu)  
        FileMenu.add_command(label='Load Config', command=None) 
        FileMenu.add_command(label='Save Config', command=self.SaveConfig)
        FileMenu.add_command(label='Save Config As', command=self.SaveConfigAs)
        FileMenu.add_command(label='Close', command=root.destroy) 
        
        HelpMenu = tk.Menu(MenuBar)
        MenuBar.add_cascade(label='Help', menu=HelpMenu) 
        HelpMenu.add_command(label='About', command=None)
               
        #Field
        self.Btn_InputTextFile = tk.Button(self, text='Input Text File', fg='blue', command=self.OpenInputTextFile)
        self.Ent_InputTextFile = tk.Entry(self, textvariable=self.InputTextFile)
        
        self.Btn_ConfigFile = tk.Button(self, text='Config File', fg='blue', command=self.OpenConfigFile)
        self.Ent_ConfigFile = tk.Entry(self, textvariable=self.ConfigFile)
        
        self.Lbl_UserName = tk.Label(self, text='User Name')
        self.Ent_UserName = tk.Entry(self, textvariable=self.UserName)
        
        self.Lbl_Password = tk.Label(self, text='Password')
        self.Ent_Password = tk.Entry(self, textvariable=self.Password)
        
        self.Lbl_APIKey = tk.Label(self, text='APIKey')
        self.Ent_APIKey = tk.Entry(self, textvariable=self.APIKey)

        self.Lbl_Version = tk.Label(self, text='Version')
        self.Ent_Version = tk.Entry(self, textvariable=self.Version)

        self.Lbl_ModelID = tk.Label(self, text='Model ID')
        self.Ent_ModelID = tk.Entry(self, textvariable=self.ModelID)

        # Input Text
        self.Txt_Input= scrolledtext.ScrolledText(self, height=15)
        
        # Output Textbox
        self.Txt_Output= scrolledtext.ScrolledText(self, height=15)        
        
        # Buttons
        self.Btn_Start = tk.Button(self, text='START', fg='green', command=self.Start)
        self.Btn_Close = tk.Button(self, text='CLOSE WINDOW', fg='red', command=root.destroy)
        
        #######################################################################
        # Pack Wigdgets
        self.Btn_InputTextFile.grid(row=0,column=0, padx=10)
        self.Ent_InputTextFile.grid(row=0,column=1, padx=10)
        
        self.Btn_ConfigFile.grid(row=1,column=0, padx=10)              
        self.Ent_ConfigFile.grid(row=1,column=1, padx=10)

        self.Lbl_Version.grid(row=2,column=0, padx=10)              
        self.Ent_Version.grid(row=2,column=1, padx=10)

        self.Lbl_UserName.grid(row=3,column=0, padx=10)
        self.Ent_UserName.grid(row=3,column=1, padx=10)

        self.Lbl_Password.grid(row=4,column=0, padx=10)              
        self.Ent_Password.grid(row=4,column=1, padx=10)
        
        self.Lbl_APIKey.grid(row=5,column=0, padx=10)              
        self.Ent_APIKey.grid(row=5,column=1, padx=10)        
 
        self.Lbl_ModelID.grid(row=6,column=0)              
        self.Ent_ModelID.grid(row=6,column=1, padx=10)
        
        self.Btn_Start.grid(row=7,column=0, columnspan=2)
        self.Btn_Close.grid(row=8,column=0, columnspan=2, pady=10)

        self.Txt_Input.grid(row=0,column=2, rowspan=6, columnspan=2, padx=10, pady=10)
        self.Txt_Input.insert(tk.END, 'Hello World')
        
        self.Txt_Output.grid(row=6,column=2, rowspan=3, columnspan=2, padx=10, pady=10)
        self.Txt_Output.insert(tk.END, '>')
        #######################################################################
    def Start(self):
        try:
            Version = self.Version.set('2018-03-16')
            TextID = 'GUI'
            Text = self.Txt_Input.get(1.0,tk.END)
            Version = self.Version.get()
            ModelID = self.ModelID.get()
            Emotion = True
            Sentiment = True
            UserName = self.UserName.get()
            Password = self.Password.get()
            APIKey = self.APIKey.get()            
            ServiceAuthentication = Basic_Auth(UserName, Password, Version)            
            WatsonResponseHeader, WatsonResponseDetail = TextNLU(ServiceAuthentication, TextID, Text, ModelID=None)#, Emotion=False, Sentiment=False, Mentions =False, =50, TextLimit=50000, ReturnText=True)
            
            print('Application Started')
            Text = '> Version:{}\n UserName:{} \n Password:{}\n APIKey:{}\n ModelID:{}\n\n'.format(self.Version.get(), self.UserName.get(),  self.Password.get(), self.APIKey.get(), self.ModelID.get())
            Text = Text + ' Text: {}\n\n'.format(Text)            
            self.Txt_Output.insert(tk.END, Text)
        except:
            print(traceback.print_exc())


    def OpenInputTextFile(self):
        try:
            FileName = filedialog.askopenfilename(title = 'Select Input Text File',filetypes = (('Text Files','*.txt'), ('All files','*.*')))
            if FileName!='':
                self.Txt_Input.delete(1.0, tk.END)
                self.InputTextFile.set(FileName)
                with open(FileName, 'r') as inputfile:
                    Text = inputfile.read()
                self.Txt_Input.insert(tk.END , Text)
                self.Input.set(Text)
            else:
                pass
            print(FileName)
        except:
            print(traceback.print_exc())
        
    def OpenConfigFile(self):
        try:
            config = configparser.ConfigParser()
            FileName = filedialog.askopenfilename(title = 'Select Config File',filetypes = (('Config Files','*.cfg'),('Text Files','*.txt'), ('All files','*.*')))
            if FileName!='':
                self.ConfigFile.set(FileName)   
                config.read(FileName)
                self.Version.set(config['DEFAULT']['version'])
                self.UserName.set(config['DEFAULT']['username']) 
                self.Password.set(config['DEFAULT']['password'])
                self.APIKey.set(config['DEFAULT']['apikey'])
                self.ModelID.set(config['DEFAULT']['modelid'])        
                self.Txt_Output.insert(tk.END, 'Config File Loded: {}\n>'.format(FileName))
            else:
                pass
        except:
            print(traceback.print_exc())
        
    def SaveConfig(self):
        FileName = self.ConfigFile.get()
        try:
            if FileName != '':
                config = configparser.ConfigParser()
                config['DEFAULT'] = {'Version': self.Version.get(), 'UserName': self.UserName.get(), 'Password': self.Password.get(), 'APIKey': self.APIKey.get(), 'ModelID': self.ModelID.get()}
                with open(FileName, 'w') as configfile:
                    config.write(configfile)
                    self.Txt_Output.insert(tk.END, 'Config File Saved: {}\n>'.format(FileName))
        except:
            print(traceback.print_exc())
        
    def SaveConfigAs(self): 
        try:
            File = filedialog.asksaveasfile(mode='w',defaultextension=".cfg")
            FileName=File.name
            if File is None:
                pass
            else:
                config = configparser.ConfigParser()
                config['DEFAULT'] = {'Version': self.Version.get(), 'UserName': self.UserName.get(), 'Password': self.Password.get(), 'APIKey': self.APIKey.get(), 'ModelID': self.ModelID.get()}        
                config.write(File)
                File.close()
                self.Txt_Output.insert(tk.END, 'Config File Saved As: {}\n>'.format(FileName))
        except:
            print(traceback.print_exc())
        
root = tk.Tk()
AppWindow = ApplicationWindow(master=root)
AppWindow.master.title('IBM Watson Natural Language Processing')
#AppWindow.master.maxsize(1024, 768)
AppWindow.mainloop()
