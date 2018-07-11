# -*- coding: utf-8 -*-
"""
Created on Fri May 18 15:36:34 2018

@author: Sumudu Tennakoon
"""

import re

EMAIL_FORMAT = re.compile(r'([\w\.-]+@[\w\.-]+\.\w+)')
DOMAIN_FORMAT = re.compile(r'@([\w\.-]+)')
PHONENUM_FORMAT = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
MESSAGID_FORMAT = re.compile(r'<(.*?)>')

def ExtractEmailAddresses(text):
    return re.findall(EMAIL_FORMAT, text)

def ExtractDomains(text):
    return re.findall(DOMAIN_FORMAT, text)
	
def ExtractMessageIDs(EmailColumn):
    return re.findall(MESSAGID_FORMAT, str(EmailColumn))

def ExtractPhoneNumber(text):
    return re.findall(PHONENUM_FORMAT, text)

def RemoveQuotedPrintableEncoding(Text):
    #Quoted-Printable Content-Transfer-Encoding
    #Source: http://www.freesoft.org/CIE/RFC/1521/6.htm  
	#https://www.w3.org/Protocols/rfc1341/5_Content-Transfer-Encoding.html
	#https://stackoverflow.com/questions/25710599/content-transfer-encoding-7bit-or-8-bit
    QPCTE = {
            '= '    :'', #Soft line break (ignore).
            '==09'  :'', #Soft line break (ignore).
            '==20'  :'', #Soft line break (ignore).  
            '=\t'  :'', #Soft line break (ignore). 
            '=\n'  :'', #Soft line break (ignore). 			
            '=09'   :'\t',  
            '=0A'   :'\n',
            '=0C'   :'\f', 
            '=0D'   :'\r',
            '=0D=0A':'\r\n',
            '=20'   :' ',  #Space   
            '=21'   :'!',  
            '=22'   :'"',  
            '=23'   :'#',  
            '=24'   :'$',          
            '=25'   :'%',          
            '=26'   :'&', 
            '=27'   :"'",  
            '=28'   :'(',  
            '=29'   :')',  
            '=2A'   :'*', 
            '=2B'   :'+',  
            '=2C'   :',',  
            '=2D'   :'-',        
            '=2E'   :'.', 
            '=2F'   :'/', 
            '=3A'   :':', 
            '=3B'   :';', 
            '=3C'   :'<', 
            '=3D'   :'=',
            '=3E'   :'>', 
            '=3F'   :'?',
            '=85'   :'...',
            '=91'   :"'",
            '=92'   :"'",
            '=93'   :'"',
            '=94'   :'"',
            '=95'   :u'\x95',
            '=96'   :'-',
            '=97'   :'--',
            '=98'   :'~',
            '=99'   :u'\x99',  #TM
            '=A9'   :u'\xA9',  #Copyright
            '=AE'   :u'\xAE',   #Registered
            '=E0'   :u'\xE0',
            '=E1'   :u'\xE1',
            '=E2'   :u'\xE2',
            '=E3'   :u'\xE3',   
            '=E4'   :u'\xE4', 
            '=E8'   :u'\xE8', 
            '=E9'   :u'\xE9', 
            '=EA'   :u'\xEA', 
            '=EB'   :u'\xEB',
            '=EC'   :u'\xEC',
            '=ED'   :u'\xED',
            '=EE'   :u'\xEE',
            '=F1'   :u'\xF1',
            '=F2'   :u'\xF2',
            '=F3'   :u'\xF3',   
            '=F4'   :u'\xF4',        
            '=F5'   :u'\xF5',  
            '=F6'   :u'\xF6',
            '=F7'   :u'\xF7',
            '=F8'   :u'\xF8',   
            '=F9'   :u'\xF9',        
            '=FA'   :u'\xFA', 
            '=FB'   :u'\xFB', 
            '=FC'   :u'\xFC', 
            '=FD'   :u'\xFD', 
            }

    for (pattern,replacement) in QPCTE.items():
        Text = Text.replace (pattern, replacement)  
    
    return Text
        
    
def RemoveHTMLTagsEntities(Text):
    # apply rules in given order!
    rules =  [
            { r'\s+' : u' '},                   # Remove Consecutive spaces
            { r'\s*<br\s*/?>\s*' : u'\n'},      # Convert <br> to Newline 
            { r'</(p|h\d)\s*>\s*' : u'\n\n'},   # Add double newline after </p>, </div> and <h1/>
            { r'<head>.*<\s*(/head|body)[^>]*>' : u'' },     # Remove everything from <head> to </head>
            { r'<script>.*<\s*/script[^>]*>' : u'' },     # Remove evrything from <script> to </script> (javascipt)
            { r'<style>.*<\s*/style[^>]*>' : u'' },     # Remove evrything from <style> to </style> (stypesheet)
            { r'<[^<]*?/?>' : u'' },            # remove remaining tags
            #{ r'<[^>]+>' : u''}
            ]
     
    for rule in rules:
        for (pattern,replacement) in rule.items():
            Text  = re.sub (pattern, replacement, Text)
            
    #https://www.w3schools.com/charsets/ref_html_entities_4.asp
    #https://docs.python.org/3/library/html.entities.html#html.entities.html5     
    HTML5Entity={
            '&lt;'    :'<', 
            '&gt;'    :'>', 
            '&nbsp;'  :' ', 
            '& nbsp;' :' ',
            '&n bsp;' :' ',
            '&nb sp;' :' ',
            '&nbs p;' :' ',
            '&quot;'  :'"',
            'cent;'   :u'\xA2',
            '&pound;' :u'\xA3',
            '&copy;'  :u'\xA9',
            '&reg;'   :u'\xAE',
            '&plusmn;':u'\xB1',
            '&frac14;':u'\xBC',
            '&frac12;':u'\xBD',
            '&frac34;':u'\xBE',
            '&times;' :u'\xD7',
            '&prime;' :u'\x2032',
            '&Prime'  :u'\x2033',
            '&lowast;':u'\x2217',
            '&ne;'    :u'\x2260',
            '&trade;' :u'\x2122',
            '&amp;'   :'&'
            }

    for (pattern,replacement) in HTML5Entity.items():
        Text = Text.replace (pattern, replacement)  

    return Text
        
def RemoveConsecutiveWhiteSpace(Text):
    Text=re.sub('[\x20][\x20]+' , ' ', Text)
    Text=re.sub('[\n][\n]+' , '\n', Text)
    Text=re.sub('[\t][\t]+' , '\t', Text)
    Text=re.sub('[\r][\r]+' , '\r', Text)
    return Text