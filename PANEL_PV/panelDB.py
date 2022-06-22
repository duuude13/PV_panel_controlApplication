# -*- coding: utf-8 -*-

# ----- libraries -----
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# ---------------------       


                                                                                                # --- part for authorization - connect Google Drive  --- 
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']      # use creds to create a client to interact with the Google Drive API and the Google Sheets API
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)           # JSON file in the same folder with API account
client = gspread.authorize(creds)                                                                               
ws2 = client.open("PVModule")                                                                   # PVModule - Google Sheets file - database with reference data from Institut of California 
ws3 = ws2.worksheet("PVModuleFull")                                                             # main worksheet             


def producerData():                                                                             # function to read PRODUCERS' names - save in temporary file - doing ones during __init__ 
    temp = ws3.col_values(1)
    f = open("producer.txt", "w")

    temp2 = temp[2]
    counter = 1
    model_count = 3
    

    for i in range(3, len(temp)):
        if temp[i] != temp2:
            f.write(temp2)
            temp2 = temp[i]
            f.write(";" + str(model_count) + ";" + str(i) + ";" + "\n")
            counter = counter + 1
            model_count = i + 1

    f.close()

def searchModel(producer):                                                                      # function to read MODELS' names for appropriate producer - save in file 

    with open('producer.txt') as f2:
        producers = f2.readlines()

    open("model.txt", "w").close()

    for line in producers:
        
        temp = ""
        if len(producer) > 12:
            x = 12
            producerName = ""
            for i in range(0, 12):
                producerName = producerName + producer[i]
        else:
            x = len(producer)
            producerName = producer


        for s in range(0, x):
            temp = temp + line[s]
        
        if temp == producerName:
            temp2 = ""
            for s in range(len(producer)+1, len(line)):
                temp2 = temp2 + line[s]
    
    count = 0
    i_start = ""
    i_end = ""
    temp3 = ""
    for i in temp2:                                                                             # read fro producer.txt starting index and ending index of models 
        if i == ";":
            count = count + 1;
            if count == 1:
                i_start = temp3
                temp3 = ""
            if count == 2:
                i_end = temp3
                temp3 = ""
        else:
            temp3 = temp3 + i

    i_start = int(i_start)
    i_end = int(i_end)

    f = open("model.txt", "w")

    for i in range(i_start, i_end):
        f.write(ws3.cell(i, 2).value)
        f.write("\n")
        
    f.close()

    f2.close()

def getData(producer, model):                                                                   # get data assigned for choosen model -> electric param 
    temp = ws3.find(model)
    
    # MANDATORY DATA
    if ws3.cell(temp.row, 1).value == producer:
        isc = ws3.cell(temp.row, 16).value
        voc = ws3.cell(temp.row, 17).value
        ipm = ws3.cell(temp.row, 18).value
        vpm = ws3.cell(temp.row, 19).value
        pm = float(ipm) * float(vpm)
        if (float(isc) * float(voc) != 0):
            ff = float(isc) * float(voc) / pm
        else:
            ff = 0
        # OPTIONAL DATA 
        saf = ws3.cell(temp.row, 4).value
        fam = ws3.cell(temp.row, 10).value
        tech = ws3.cell(temp.row, 11).value
        ave = ws3.cell(temp.row, 20).value
        sSide = ws3.cell(temp.row, 32).value
        lSide = ws3.cell(temp.row, 33).value
        parallel = ws3.cell(temp.row, 14).value
        serial = ws3.cell(temp.row, 13).value

        # create vector with whole params as text 
        data = [str(isc), str(voc), str(ipm), str(vpm), str(pm), str(ff), str(saf), str(fam), str(tech), str(ave), str(sSide), str(lSide), str(parallel), str(serial)]

    return data