                                                                                                          # application to operate the photovoltaic panel with the use of a code reader and the ability to add new ones
                                                                                                          # panels and testing
# ---- libraries ----
from datetime import datetime
import csv

import sheetsControl
import panelDB
from Main import *                                                                                         
from not1 import *

import Main

from tk import *                                                                                          # Tkinter Library 
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from sheetsControl import *
from panelDB import *

import fpdf
from fpdf import FPDF

import random

# -------------------

#value = 0
value2 = "0"
dataCount = 0
pdfData = 0 
pdfData2 = 0
pdfInfo = 0
pdfDev = 0
barcodePDF = ""

class main_ui(Ui_MainWindow):                                                                             # Main class, MAIN WINDOW                                                                                                                                                                              # INIT 
   

    def __init__(self, window):                                                                           # INITIALIZATION 
        self.setupUi(window)
                                                                                                          # NEW PANEL
        self.addPanelTabManage() 

        self.table.setVisible(False)                                                                                                  
        self.okButton.clicked.connect(self.save)
       
        self.emptyTextLabel.setVisible(False)
        
        self.testTable.setVisible(False)
        self.label_14.setVisible(False)
        self.label_15.setVisible(False)
       
        self.referenceLabel.hide()
        self.testDataLabel.hide()
        
        self.datesComboBox.currentIndexChanged.connect(self.comboBoxGetData2)
        
        self.barCode.returnPressed.connect(self.save)
        self.raportButton.hide()

        self.raportButton.clicked.connect(self.pdfRaport)

        self.producerComboBox.currentIndexChanged.connect(self.addPanelComboBoxProducer)
        self.modelNoComboBox.currentIndexChanged.connect(self.addPanelComboBoxModel) 

        self.barcodeCheckBox.clicked.connect(self.createBarcode)

        self.modelNoComboBox.currentIndexChanged.connect(self.displayPanelData)
        self.pushButton_2.clicked.connect(self.sendData)
        
        producerData()

        self.tabWidget.setTabText(0, "Search Panel and Test")
        self.tabWidget.setTabText(1, "Make Test")
        self.tabWidget.setTabText(2, "Add New Panel")

        self.searchManage()

        self.barCodeLineEdit_NP.setEnabled(False)
        self.dateTimeLineEdit_NP.setEnabled(False)
        self.testIDLineEdit_NP.setEnabled(False)

        self.startTestButton.clicked.connect(self.makeNewTest)

        self.getBarcodeComboBox.addItem("- select -")
        self.producerComboBox_2.addItem("- select -")
        self.modelComboBox.addItem("- select -")
        self.getBarCode2ComboBox.addItem("- select -")
        self.selectBarcodeProducer()
        self.selectBarcodeModel()
        self.selectBarcodeBarcode()

        self.modelComboBox.currentIndexChanged.connect(self.selectBarcodeBarcode)
        self.producerComboBox_2.currentIndexChanged.connect(self.selectBarcodeModel)
        
    def searchManage(self):
        barcodes = getBarcodes()

        count = 0
        for i in barcodes:
            if count != 0:
                self.barcodeComboBox.addItem(i)
                self.getBarCode2ComboBox.addItem(i)
            count = count + 1

    def selectBarcodeProducer(self):
        
        producer = getProducer("producer")
            
        for i in producer:
            if i != "":
                self.producerComboBox_2.addItem(i)

    def selectBarcodeModel(self):
        
        if self.producerComboBox_2.currentText() != "- select -":
            producer = self.producerComboBox_2.currentText()
            models = getModel(producer)
            self.modelComboBox.clear()
            self.modelComboBox.addItem("- select -")

            for i in models:
                self.modelComboBox.addItem(i)
        
        else:
            models = getProducer("model")
            for i in models:
                if i != "":
                    self.modelComboBox.addItem(i)
    
    def selectBarcodeBarcode(self):
        if self.modelComboBox.currentText() == "- select -":
            barcodes = getBarcodes()

            count = 0
            for i in barcodes:
                if count != 0:
                    self.getBarcodeComboBox.addItem(i)
                count = count + 1
        else:
            model = self.modelComboBox.currentText()
            barcodes = getBarcode(model)
            self.getBarcodeComboBox.clear()
            self.getBarcodeComboBox.addItem("- select -")

            for i in barcodes:
                self.getBarcodeComboBox.addItem(i)

    def selectBarcodeMTModel(self):
        producer = self.producerComboBox_2.currentText()
        models = getModel(producer)
        if models != None:
            for i in models:
                if i != "":
                    self.modelComboBox.addItem(i)


   
    def comparisonData(self, refData, mesData):                                                           # comparison data from test - mesData -> refData from database 
        refData = float(refData)
        mesData = float(mesData)

        dev = format((refData - mesData) * 100 / refData , ".2f")                                         # dev - % -> format 2 decimal places
        print("dev",dev)
        return dev

    def comboBoxGetData2(self):                                                                           # function for handling the comboBox - reads available names from the database
                                                                                                          # for comboBox - SEARCH 
        global value2                                                                                     # variables: value2 - current text on ComboBox ;  dataCount - counter for rows found in database
        global dataCount
        
        value2 = self.datesComboBox.currentText()
        if (value2 != "- select -") & (value2 != "0"):                                                    # comboBox support if the selected option changes
            table = self.table                                                                            # table - table which shows data from dataBase for BarCode 
            table.setVisible(True)
            self.referenceLabel.show()
            table.setRowCount(dataCount)
            table.setColumnCount(2)                                                                       # data displayed in two columns (assumption)
            dataCount = 0
            table.setHorizontalHeaderLabels(["Parameter", "Value"])
            pdfCount = 0
            pdfCount2 = 0

            global pdfData
            global pdfData2
            global pdfInfo
            global pdfDev
            pdfData = [""] * len(sheetsControl.data)
            pdfData2 = [""] * len(sheetsControl.data)
            pdfDev = [""] * len(sheetsControl.data)

            record = ["Voc (V)", "Isc (A)", "Pm (W)", "Vpm (V)", "Ipm (A)", "FF (%)"]

            for i in range(0, len(link2)):                                                  # support for displaying and retrieving rows into a table
                if link2[i] != None:
                    table.setItem(dataCount, 0, QTableWidgetItem(record[i]))                              # record -> heading 
                    table.setItem(dataCount, 1, QTableWidgetItem(link2[i]))                 # link2 -> found data
                    dataCount = dataCount + 1
                    pdfData[pdfCount] = link2[i]
                    pdfCount = pdfCount + 1
            
            param = dataSearch(value2)                                                                    # dataSearch() - function from sheetsControl.py - get vector with data from tests
            print(param)

            table.setColumnWidth(0, 145)
            table.setColumnWidth(1, 140)

            headingIndexValue = headingValues()

            for j in range(2, len(headingIndexValue)-1):                                    # support for displaying and retrieving rows into a table NEXT part 
                if sheetsControl.param[j] != None:
                    table.insertRow(table.rowCount())
                    table.setItem(dataCount, 0, QTableWidgetItem(headingIndexValue[j]))     # headingIndexValue -> heading 
                    table.setItem(dataCount, 1, QTableWidgetItem(sheetsControl.param[j]))                 # param -> found data
                    dataCount = dataCount + 1
                    pdfData[pdfCount] = headingIndexValue[j] + ": " + sheetsControl.param[j]
                    pdfCount = pdfCount + 1
            
            csvName = ""
            csvName = csvFinder(value2)                                                                             # searching csv file -> chka sheet in database -> return global value (csvName)
            if csvName != "":                                                               # if upper function found csv file enable 
                csvGet(csvName)                                                                                  # csvGet() -> GET DATA (U, I) -> function makes plot I(U) and P(U) using data from csv 
            self.testDataLabel.show()
            table2 = self.testTable                                                                       # table - table which shows data from dataBase for BarCode 
            table2.setVisible(True)
            self.label_14.setVisible(True)
            self.label_15.setVisible(True)
            table2.setColumnCount(3) 
            temp = 0
            devCount = 0
            for k in range(0, len(sheetsControl.data)):
                table2.insertRow(table2.rowCount())    
                
                if sheetsControl.data[0] != "":
                    dev = self.comparisonData(link2[k], sheetsControl.data[k])                      # dev - error % 
                    dev = float(dev)

                    table2.setColumnWidth(1, 125)
                    table2.setColumnWidth(0, 125)

                    table2.setItem(temp, 0, QTableWidgetItem(sheetsControl.dataName[k]))                        # column 1 ---> parameter  
                    table2.setItem(temp, 1, QTableWidgetItem(sheetsControl.data[k]))                            # column 2 ---> value 
                                                                                                                # column 3 ---> coverage of test parameters with reference data
                    pdfData2[pdfCount2] = sheetsControl.dataName[k] + ": " + sheetsControl.data[k]
                    pdfCount2 = pdfCount2 + 1

                    table2.setHorizontalHeaderLabels(["Parameter", "Value", ""])                                # set table's header 
                    table2.setColumnWidth(2, 10)                                                                # 3rd column width
                    item = QTableWidgetItem("")                                                                 # item = "" -> for 3rd column place
                    if sheetsControl.statusTest == 1:
                        if dev <= 10:                                                                               # <= 10 % -> PASS
                            # green
                            item.setBackground(QColor(170, 255, 127))
                            table2.setItem(temp, 2, QTableWidgetItem(item))
                            pdfDev[k] = ""
                        elif dev <= 20:                                                                             # <= 20% -> WARNING                                                         
                            # orange 
                            item.setBackground(QColor(255, 170, 0))
                            table2.setItem(temp, 2, QTableWidgetItem(item))
                            pdfDev[k] = ""
                        else:                                                                                       # >20% -> FAIL
                            # red                   
                            item.setBackground(QColor(255, 52, 26))
                            table2.setItem(temp, 2, QTableWidgetItem(item))
                            pdfDev[k] = k
                            pdfInfo = "(!) The error exceeds 20%"
                temp = temp + 1
            self.raportButton.show()
            

    def pdfRaport(self):
        pdf = FPDF()                                                                                            # generate pdf file - RAPORT 
        pdf.add_page() 
        
        value2 = self.datesComboBox.currentText() 
        # # Go to 1.5 cm from bottom
        #pdf.set_y(-15)
        ## Select Arial italic 8
        #pdf.set_font('Arial', 'I', 8)
        ## Print centered page number
        #pdf.cell(0, 550, 'Page %s' % pdf.page_no(), 0, 0, 'C')

        pdf.l_margin = 25
        pdf.set_font("Arial", size = 8)            
        titlePdf = "Raport - Serial No. " + barcodePDF           
        pdf.cell(200, 10, txt = titlePdf, ln = 1, align = 'C')    
        line = "Test ID: " + value2
        pdf.cell(200, 10, txt = line, ln = 1, align = 'L') 
                
        pdf.cell(200, 10, txt = "Measurement data (Reference data):", ln = 2, align = 'L')
        for i in range(0, len(pdfData)):
            msg = pdfData2[i] + " (" + pdfData[i] + ") "
            if pdfDev[i] != "":
                msg = msg + "                 (!)"
            pdf.cell(100, 10, txt = msg, border = 1, ln = 2, align = 'L')
            
        pdf.set_font("Arial", size = 7)
        pdf.cell(200, 10, txt = pdfInfo, ln = 2, align = 'L')
        pdf.set_font("Arial", size = 8)

       
        csvName = csvFinder(value2) 
        imageName = csvName + ".png"
        img = open(imageName, "rb").read()

        pdf.l_margin = 0
        pdf.image(imageName, 50 , None, 100, 75, type='PNG')
        
        #pdf.cell(0, 5, 'Page ' + str(pdf.page_no()), 0, 0, 'C')

        name = "Raport_" + str(barcodePDF)
        name = name + ".pdf"
        pdf.output(name) 

        #path = 'my_file.pdf'
        path = "Raport_LZEAJ065-001787.pdf"
        os.system(name)
            

    def save(self):                                                                                       # function for checking whether the entered barcode is in the database, 
                                                                                                          # displaying its parameters or proposing to add a panel
        global link2
                                                                                                          
        global value2 
        global dataCount
        global barcodePDF
        
        temp = self.barcodeComboBox.currentText()
        barcodePDF = temp
        if temp == "- select -":
            temp = self.barCode.text()
            barcodePDF = temp
        if len(temp) > 0:
            self.emptyTextLabel.setVisible(False)

            index = [0]
            barCodeID = [0]
            link2 = [0]

            index = barCodeFinder(temp)                                                                       # barCodeFinder() - from sheetsControl.py - database handler function
            index, barCodeID, link2 = barCodeFinder(temp)                                                                       # barCodeFinder() - from sheetsControl.py - database handler function
        
            if (link2[0] != "no data") & (link2[0] != None):                      # display relevant data
                dataCount = 0
                for i in range(0, len(link2)):                                                  # check the number of available parameters
                    if link2[i] != None:
                        dataCount = dataCount + 1
                self.datesComboBox.addItem("- select -")                                                      # if data are available first element on comboBox is -select- 
                for j in range(1, len(barCodeID)):
                    if index[j-1] != "none":
                        self.datesComboBox.addItem(barCodeID[j])

                
            else:
                self.window = Main.QtWidgets.QDialog()                                                        # dialog box asking if we want to add the panel to the database
                self.ui = Ui_Dialog()
                self.ui.setupUi(self.window)
                self.window.show()  
                self.ui.yesButton.clicked.connect(self.changeTab)                                             # yes -> transfer to form
        else:
            self.emptyTextLabel.setVisible(True)
            self.emptyTextLabel.setText("The field is empty")
            
    def changeTab(self):                                                                                    # function to change tab on TabWidget
        self.tabWidget.setCurrentWidget(self.addPanel)
  
        
    def newPanelForm(self):                                                                                 # function for handling the form for adding a new panel
        text = self.barCodeLine.text()                                                                      # catching inserted text from barCodeLine 
        
    def makeNewTest(self):                                                                                     # makeTest -> function to start test -> create csv file with data from RasberryPie
        
        # (1) enter barcode
        if self.radioButton.isChecked() == True:
            temp1 = self.barcode2LineEdit.text()
            print(temp1)
            
        # (2) barcode from list
        elif self.radioButton_3.isChecked() == True:
            temp1 = self.getBarCode2ComboBox.currentText()
            print(temp1)
        # (3) barcode from 3 parts list 
        elif self.radioButton_2.isChecked() == True:
            temp1 = self.getBarcodeComboBox.currentText()
            print(temp1)
        else:
            print("NIC")

        print(self.radioButton.isChecked())
        self.barCodeLineEdit_NP.setText(temp1)

        now = datetime.now()
        dateNow = now.strftime("%Y-%m-%d %H:%M:%S")

        self.dateTimeLineEdit_NP.setText(dateNow)
       
        testName = saveDisk(temp1, dateNow)  
        if testName != "Panel not exist":
            self.testIDLineEdit_NP.setText(testName) 
        else: 
            print(testName)

        self.barcode2LineEdit.clear()
        self.getBarcodeComboBox.setCurrentIndex(0)
        self.getBarCode2ComboBox.setCurrentIndex(0)

    def addPanelTabManage(self):                                                                            # function for handling objects in tab 'ADD NEW PANEL' in app - initial commands
        # (1) set disable QLineEdit 
        self.vocLineEdit.setEnabled(False)
        self.iscLineEdit.setEnabled(False)
        self.pmLineEdit.setEnabled(False)
        self.vpmLineEdit.setEnabled(False)
        self.ipmLineEdit.setEnabled(False)
        self.ffLineEdit.setEnabled(False)

        self.safetyCertLineEdit.setEnabled(False)
        self.familyLineEdit.setEnabled(False)
        self.techLineEdit.setEnabled(False)
        self.noctLineEdit.setEnabled(False)
        self.shortSideLineEdit.setEnabled(False)
        self.longSideLineEdit.setEnabled(False)
        self.paralleLinksLineEdit.setEnabled(False)
        self.serialCellsLineEdit.setEnabled(False)

        self.safetyCertCheckBox.setEnabled(False)
        self.familyCheckBox.setEnabled(False)
        self.techCheckBox.setEnabled(False)
        self.noctCheckBox.setEnabled(False)
        self.shortSideCheckBox.setEnabled(False)
        self.longSideCheckBox.setEnabled(False)
        self.paralleLinksCheckBox.setEnabled(False)
        self.serialCellsCheckBox.setEnabled(False)

        # (2) hide QLineEdit - producer & model no.
        self.modelNoLineEdit.hide()
        self.producerLineEdit.hide()

        # (3) data to comboBox - producers 
        with open('producer.txt') as f:
            producers = f.read()

        temp = ""
        count = 3
        for producer in producers:
            if producer == "\n":
                producer = ""
            if producer != ";":
                temp = temp + producer
            else:
                if count % 3 == 0:
                    self.producerComboBox.addItem(temp)
                temp = ""
                count = count + 1
                

    def addPanelComboBoxProducer(self):                                                                      # function to check choosen item in comboBoxes PRODUCER
        # (1) producer comboBox
        temp = self.producerComboBox.currentText()
        if temp == "Other ":
            print("producer other")
            self.producerLineEdit.show()
            producer = self.producerLineEdit.text()                                                          # producer 
        elif temp != "- select -":
            self.producerLineEdit.hide()
            producer = self.producerComboBox.currentText()
                                                                                                             # add items to comboBox MODEL
            searchModel(producer)

            with open('model.txt') as f:
                models = f.read()

            temp = ""
            for model in models:
                if model != "\n":
                    temp = temp + model
                else:
                    self.modelNoComboBox.addItem(temp)
                    temp = ""
        else:
            self.producerLineEdit.hide()
            
    
    def addPanelComboBoxModel(self):                                                                      # function to check choosen item in comboBoxes MODEL
         # (2) model No. comboBox    
        temp = self.modelNoComboBox.currentText()
        if temp == "Other ":
            self.modelNoLineEdit.show()
            modelNo = self.modelNoLineEdit.text()

        elif temp != "- select -":
            self.modelNoLineEdit.hide()
            modelNo = self.modelNoComboBox.currentText()
        else:
            self.modelNoLineEdit.hide()
            modelNo = self.modelNoComboBox.currentText()
            
    def createBarcode(self):                                                                                # function which create barcode automatically -> tab ADD PANEL         
        # conditions to make barcode 
        if (self.barcodeCheckBox.checkState() == 2) & (self.modelNoComboBox.currentText() != "- select -") & (self.producerComboBox.currentText() != "- select -"):
            # (1) read data from apropriate objects
            if self.modelNoComboBox.currentText() == "Other ":
                x2 = self.modelNoLineEdit.text()
            else:
                x2 = self.modelNoComboBox.currentText()

            if self.producerComboBox.currentText() == "Other ":
                x1 = self.producerLineEdit.text()   
            else: 
                x1 = self.producerComboBox.currentText()
            
            # (2) get random 6-signs number
            rand = random.randint(100000,999999)

            barcode = ""
            # create barcode if model and producer names has min. 3 signs
            if (len(x1) > 2) & (len(x2) > 2):
                barcode = barcode + x1[0] + x1[1] + x1[2] + x2[0] + x2[1] + x2[2] + str(rand)
                self.barcodeLineEdit.setText(barcode)
        
    def displayPanelData(self):   
        # conditions when display is possible
        model = self.modelNoComboBox.currentText()
        data = None
        if (model != "Other ") & (model != "- select -"):
            producer = self.producerComboBox.currentText()

            # get data from drive
            data = getData(producer, model)

            self.vocLineEdit.setText(data[1])
            self.iscLineEdit.setText(data[0])
            self.pmLineEdit.setText(data[4])
            self.vpmLineEdit.setText(data[3])
            self.ipmLineEdit.setText(data[2])
            self.ffLineEdit.setText(data[5])

            self.safetyCertLineEdit.setText(data[6])
            self.familyLineEdit.setText(data[7])
            self.techLineEdit.setText(data[8])
            self.noctLineEdit.setText(data[9])
            self.shortSideLineEdit.setText(data[10])
            self.longSideLineEdit.setText(data[11])
            self.paralleLinksLineEdit.setText(data[12])
            self.serialCellsLineEdit.setText(data[13])

        elif model == "Other ":
            # unlock objects
            self.vocLineEdit.setEnabled(True)
            self.iscLineEdit.setEnabled(True)
            self.pmLineEdit.setEnabled(True)
            self.vpmLineEdit.setEnabled(True)
            self.ipmLineEdit.setEnabled(True)
            self.ffLineEdit.setEnabled(True)
            
            self.safetyCertCheckBox.setEnabled(True)
            self.familyCheckBox.setEnabled(True)
            self.techCheckBox.setEnabled(True)
            self.noctCheckBox.setEnabled(True)
            self.shortSideCheckBox.setEnabled(True)
            self.longSideCheckBox.setEnabled(True)
            self.paralleLinksCheckBox.setEnabled(True)
            self.serialCellsCheckBox.setEnabled(True)
            
    def sendData(self):                                                                                   # function to send data from form to database
        err = None
        # producer 
        producer = self.producerComboBox.currentText()
        if producer == "Other ":
            producer = self.producerLineEdit.text()
        elif producer != "- select -":
            producer = self.producerComboBox.currentText()
        else:
            err = "producer"
            self.error(err)

        # model
        model = self.modelNoComboBox.currentText()
        if model == "Other ":
            modelNo = self.modelNoLineEdit.text()
        elif model != "- select -":
            modelNo = self.modelNoComboBox.currentText()
        else:
            err = "model"
            self.error(err)

        # barCode 
        barcode = self.barcodeLineEdit.text()
        if barcode == None:
            err = "barcode"
            self.error(err)

        # parameters - mandatory 
        voc = self.vocLineEdit.text()
        isc = self.iscLineEdit.text()
        pm = self.pmLineEdit.text()
        vpm = self.vpmLineEdit.text()
        ipm = self.ipmLineEdit.text()
        ff = self.ffLineEdit.text()

        if voc == None:
            err = "voc"
            self.error(err)
        if  isc == None:
            err = "isc"
            self.error(err)
        if  pm == None:
            err = "pm"
            self.error(err)
        if  vpm == None:
            err = "vpm"
            self.error(err)
        if  ipm == None:
            err = "ipm"
            self.error(err)
        if  ff == None:
            err = "ff"
            self.error(err)
            
        # parameters - optional 
        safe = self.safetyCertLineEdit.text()
        fam = self.familyLineEdit.text()
        tech = self.techLineEdit.text()
        noct = self.noctLineEdit.text()
        sSide = self.shortSideLineEdit.text()
        lSide = self.longSideLineEdit.text()
        paral = self.paralleLinksLineEdit.text()
        serial = self.serialCellsLineEdit.text()

        # description - optional 
        descr = self.descriptionLineEdit.text()

        # message to admin 
        #message = self.messageAdminTextEdit.te
            
        if err == None:
            panelData = [producer, model, barcode, voc, isc, pm, vpm, ipm, ff, safe, fam, tech, noct, sSide, lSide, paral, serial, descr]

            verifyData(panelData)


            print(panelData)




    def error(self, err):
        print("error ", err)


app = QtWidgets.QApplication(sys.argv)                                                                    # display app main window 
MainWindow = QtWidgets.QMainWindow()                                                                      
ui = main_ui(MainWindow)                                                                                  
                                                                                                          
MainWindow.show()                                                                                        
sys.exit(app.exec_())   
