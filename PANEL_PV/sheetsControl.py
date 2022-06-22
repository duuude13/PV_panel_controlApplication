
# ---- libraries ----                                                                                             
import numpy as np
import matplotlib.pyplot as plt                                                                 # library -> matplotlib.pyplot -> PLOTING
import csv
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

# -------------------                                                                            
                                                                                                # --- part for authorization - connect Google Drive  --- 
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']      # use creds to create a client to interact with the Google Drive API and the Google Sheets API
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)           # JSON file in the same folder with API account
client = gspread.authorize(creds)                                                                               
ws2 = client.open("Excel")
work = ws2.worksheet("chka")                                                                    # chka = sheet contains csv files -> links/names
ws = ws2.worksheet("Panel")                                                                     # main sheet -> barcodes with tests date
work1 = ws2.worksheet("Test")                                                                   # sheet with info about TESTS -> date and csv file name
ws_ver = ws2.worksheet("verify")                                                                # sheet to control entered data
baza = ws2.worksheet("baza_panel")                                                              # sheet with panel reference params written in create part 


# global variables:
serial = [0]
indexExist = [0]
data = [0] * 6
dataName = [0] * 6
statusTest = 0

def headingValues():                                                                            # Reading headings from sheet with TEST DATA
    headingIndexValue = work1.row_values(1) 

    return headingIndexValue
                                          
def barCodeFinder(barCode):                                                                        # Searching for insert barCode in database
    cell = ws.find(barCode)
    
    headingIndexValue = headingValues() 
    
    if cell != None:
        barCodeID = ws.row_values(cell.row)                                                     # barCodeID - array with values from row with searched barCode
        
        index = [0] * len(barCodeID)                                                            # index - array for tests' dates
        indexValue = [0] * len(barCodeID)
        
        if len(barCodeID) > 1:                                                                  # finding rows form sheet2 with dates from index
             for i in range(1, len(barCodeID)):
                 index[i-1] = work1.find(barCodeID[i])
                 if work1.cell(index[i-1].row, 2).value != barCode:
                     index[i-1] = "none"
                 else:
                     indexValue[i-1] = work1.row_values(index[i-1].row)

    cell2 = baza.find(barCode)

    link2 = [0] * 6

    for i in range(6, 11):                                                                      # save data to the array with parameters from sheet1 and sheet2
        if cell2 != None:
             link2[i-6] = baza.cell(cell2.row, i).value
             link2[i-6] = str(link2[i-6])
        else:
             link2[i-6] = "no data"       
    link2[5] = baza.cell(cell2.row, 11).value 
    
    return index, barCodeID, link2 

def dataSearch(dateTest):                                                                       # get parameters from test data
    
    headingIndexValue = headingValues()
    
    param = [0] * len(headingIndexValue)
    testParam = work1.find(dateTest)
    for i in range(0, len(headingIndexValue)):                                                  # save data to the array with parameters from sheet1 and sheet2
        if testParam != None:
             param[i] = work1.cell(testParam.row, testParam.col+i).value
        else:
             param[i] = "no data"

    return param

                                                                                                
def serialNo():                                                                                 # function for finding available names and types of panels
    
    global serial
    serial = ws.col_values(2)

def csvFinder(dateTest):                                                                        # function for searching name of CSV file for current-voltage characteristic
    
    csvName = ""
    cellCsv = work.find(dateTest)                                                               # finding appropriate connected data
    if cellCsv != None:
        csvName = work.cell(cellCsv.row, 4).value                                               # csvName = name of csv file 

    return csvName
    

def csvGet(csvName):                                                                                   # function to read and use csv file 
                                                                                                # works ONLY for file located in path 
    global statusTest
    global data
    statusTest = 0
    
    fileName = csvName + ".csv"
    file = open(fileName)
    csvreader = csv.reader(file, delimiter=';')                                                 # delimeter ; 
    
    header = next(csvreader)
    rows = []

    U = [0] * 100                                                                               # first element in row VOLTAGE
    I = [0] * 100                                                                               # second element in row CURRENT
    P = [0] * 100                                                                               # calculated POWER = U*I
    counter  = 0
     
    for row in csvreader:                                                                       # getting data from csv file to arrays
        rows.append(row)
        if csvreader != None:
            U[counter] = row[0]
            I[counter] = row[1]
            U[counter] = float(U[counter].replace(",", "."))                                    # replace , to . and convert string to float 
            I[counter] = float(I[counter].replace(",", "."))
            P[counter] = U[counter] * I[counter];                                               # calculating POWER
            counter = counter + 1
        
    Up = [0] * counter                                                                          # Up, Ip, Pp - U, I, P for ploting
    Ip = [0] * counter   
    Pp = [0] * counter   

    for i in range(0, counter):                                                                 # rewriting to Up, Ip, Pp
        Up[i] = U[i]
        Ip[i] = I[i]
        Pp[i] = P[i]              
    
    
    if counter > 2:                                                                             # protection against empty file -> not plotting
        statusTest = 1
        paramCalc(Up, Ip, Pp)   
               
        fig,ax = plt.subplots()                                                                 # PLOT -> figure with 2 axes -> 1 plot: I-U characteristic, 2 plot: woltage 
    
        ax.plot(Up, Ip, color='r')                                                              # 1 AXIS ----------------- I(U)
        plt.xlabel("U, V")
        plt.ylabel("I, A")

        ax2 = ax.twinx()                                                                        # rewrite X axis -> U
        ax2.plot(Up, Pp, color='g')                                                             # 2 AXIS ----------------- P(U)
        ax2.set_ylabel("P, W")
    
        plt.title('Current-voltage characteristic')
        plt.show()                                                                              # show PLOT  ----------------- make window
        figName = csvName + ".png"                                                              # save plot as figure ( format .png )
        plt.savefig(figName)      
        
        
    else:
        data = [""] * 5

        
    file.close()                                                                                # close .csv file 


def paramCalc(U, I, P):                                                                         # function to calculate parameters from csv file -> for test 
    iscx = np.argmax(I)                                                                         # np. -> numpy library ---- search max from array 
    vocx = np.argmax(U)
    pmx = np.argmax(P)
    isc = I[iscx]
    voc = U[vocx]
    pm = format(P[pmx],".2f")                                                                   # format(data, type format) --> ".2f" - two digits after decimal point
    vpm = U[pmx]
    ipm = I[pmx]
    ff = format((ipm * vpm) / (isc * voc) * 100, ".2f")
    
    global data
    global dataName
    dataName = ["Voc (V)", "Isc (A)", "Pm (W)", "Vpm (V)", "Ipm (A)", "FF (%)"]                       # dataName - heading of data
    data = [str(voc), str(isc), str(pm), str(vpm), str(ipm), str(ff)]                           # data 
        

def saveDisk(barCode, dateTest):                                                                # if NEW TEST -> save it on disk in appropraite position 
    
    temp2 = ws.find(barCode)

    if temp2 != None:
        row_list_panel = ws.row_values(temp2.row)
        ws.update_cell(temp2.row, len(row_list_panel)+1, dateTest)
    
        column_list_chka = work.col_values(1)
        column_list_test = work1.col_values(1)

        temp = work.findall(barCode)                                                                 # finall() --- gspread lib --- temp -> all found data 
        if temp != None:
            number = len(temp) + 1                                                                      # number of next csv file 
        else:
            number = 1

        work.update_cell(len(column_list_chka)+1, 1, barCode)                                        # update chka sheet ----> for finding appropriate name of csvFile
        work.update_cell(len(column_list_chka)+1, 2, dateTest)
        work.update_cell(len(column_list_chka)+1, 3, number)

        testName = barCode + "-" + str(number)
        work.update_cell(len(column_list_chka)+1, 4, testName)

        work1.update_cell(len(column_list_test)+1, 1, dateTest)                                       # update test sheet ----> for datedate of tests 
        work1.update_cell(len(column_list_test)+1, 2, barCode)
        work1.update_cell(len(column_list_test)+1, 3, testName)

        csvCreate(testName)                                                                         # creating NEW CSV FILE -> in path  
    
        return testName
    else:
        infoErr = "Panel not exist"
        return infoErr
    
def createNewPanel(barCode, formData):
    column_list = ws.col_values(1)                                                             # number of rows 
    
    ws.update_cell(len(column_list)+1, 2, barCode)                                               # ADD new panel - Serial No. to database 
    for i in range(3, 9):
        ws.update_cell(len(column_list)+1, i, formData[i-3]) 


def csvCreate(fileName):                                                                        # create NEW CSV FILE after ADD NEW PANEL 
    
    header = ['U;I']                                                                            # header 
    data = ['0;0']                                                                              # data --------------------------------- Need to change - depends on collected data 
    fileName = fileName + ".csv"
    with open(fileName, 'w', newline="") as f: #, encoding='UTF8'
        writer = csv.writer(f)
                                                                                                # WRITEROW() --- function which write data in one row -> next empty row
        writer.writerow(header)                                                                 # write the header
        writer.writerow(data)



def verifyData(panelData):                                                                      # function to send data to database to verification sheet
    row_count = ws_ver.col_values(2)                                                            # count the amount of using rows
    print(len(row_count), row_count)
    
    count = 1
    for i in panelData:
        ws_ver.update_cell(len(row_count)+1, count + 2, i) 
        count = count + 1


def getBarcodes():                                                                              # get Barcodes from sheet 'panel' -> all added barcodes
    barcodes = ws.col_values(1)

    return(barcodes)
            
def getProducer(what):                                                                          # get producer from reference database
    if what == "producer":
        temp = baza.col_values(1)
        producer = [""] * len(temp)

        count = 0
        x = temp[0]
    
        for i in temp:
            if i != x:
                producer[count] = i
                x = i
                count = count + 1

        return producer

    elif what == "model":
        temp = baza.col_values(3)
        model = [""] * len(temp)

        count = 0
        x = temp[0]
    
        for i in temp:
            if i != x:
                model[count] = i
                x = i
                count = count + 1

        return model

def getModel(producer):                                                                     # get model from reference database
    temp = baza.findall(producer)
    model = [""] * len(temp)

    x = baza.cell(temp[0].row, 3).value
    print(x)
    count = 0

    for i in temp:
        temp2 = baza.cell(i.row, 3).value
        if  temp != x:
            model[count] = temp2
            x = temp2
            count = count + 1

    return(model)

def getBarcode(model):                                                                      # get added barcodes
    temp = baza.findall(model)
    bar = [""] * len(temp)

    x = baza.cell(temp[0].row, 4).value
    print(x)
    count = 0

    for i in temp:
        temp2 = baza.cell(i.row, 4).value
        if  temp != x:
            bar[count] = temp2
            x = temp2
            count = count + 1

    return(bar)
