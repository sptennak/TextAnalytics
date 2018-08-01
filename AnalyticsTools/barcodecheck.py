# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 06:32:40 2018

@author: Sumudu Tennakoon
"""
import re
import numpy as np

Code = '844702072077'#'078910629277' # '078742040370' #'036000291452' #

def split_upc(Code):
    #https://en.wikipedia.org/wiki/Universal_Product_Code
    Code = re.sub('[^0-9]+', '', Code) #Cleanup the code
    SystemDigit = Code[0]
    CheckDigit = Code[-1]
    #######################################################################
    LLLLL = Code[1:6] #LLLLL is the item number, and the , with the 
    RRRRR = Code[-6:-1] #RRRRR is either the weight or the price
    R1 = Code[-6] #first R determining which (0 for weight)
    #######################################################################
    RRR_ = Code[-6:-3] # LLLLL digits are the manufacturer code, the first three RRR are a family code (set by manufacturer)
    _RR = Code[-3:-1] #last 2 digits: coupon code, which determines the amount of the discount
    #######################################################################
    LR10 = Code[1:-1] # National Drug Code (NDC). (UPN Codes)
    
    return {'SystemDigit':SystemDigit, 'CheckDigit':CheckDigit , 'LLLLL':LLLLL, 'RRRRR':RRRRR, 'R1':R1, 'RRR_':RRR_, 'LR10':LR10}

def upc_check_digit(Code):
    #https://en.wikipedia.org/wiki/Universal_Product_Code
    Code = re.sub('[^0-9]+', '', Code) #Cleanup the code

    DigitCount = len(Code)
    
    if DigitCount==12:
        #######################################################################
        CheckFormula=np.array([3,1,3,1,3,1,3,1,3,1,3,1])
        Digits = np.zeros(DigitCount, dtype=np.int)
        for i in range(DigitCount-1):
            Digits[i] = int(Code[i])
        M = np.sum(Digits*CheckFormula) % 10
        if M != 0:
            CheckDigitValue = 10 - M
        else:
            CheckDigitValue = 0
        #######################################################################
    else:
        CheckDigitValue = -1
        
    return CheckDigitValue
 
def check_upc(Code):
    CheckDigitValue = upc_check_digit(Code)
    if CheckDigitValue==int(Code[-1]):
        return True
    else:
        return False

print(Code)
print(check_upc(Code))
print(split_upc(Code))