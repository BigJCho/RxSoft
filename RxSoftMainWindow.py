import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtSql as qts

class MainWindow(qtw.QMainWindow):
    editSelected = qtc.pyqtSignal(int)
    scheduleSelected = qtc.pyqtSignal(int)
    refillSelected = qtc.pyqtSignal(int)
    def __init__(self):
        super().__init__()
        #Code
        #Database
        db = qts.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('rxsoft.db')
        if not db.open():
            print("Unable to connect to database")
            sys.exit(1)
        #Create central widget to add to and a main layout
        self.centralWidget = qtw.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = qtw.QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
        #Add TopBar for the top view
        self.topbar = TopBarView()
        self.mainLayout.addWidget(self.topbar)
        #Creating the middle view
        self.centerStack = qtw.QStackedWidget()
        #Patient Model and View
        self.patientView = PatientView()
        self.patientModel = PatientModel()
        #Browse Model and View
        self.browseRight = BrowseView()
        self.datesDisplay = DatesDisplay()
        self.browseModel = BrowseModel()
        self.browseLayout = qtw.QHBoxLayout()
        self.browseLayout.addWidget(self.datesDisplay)
        self.browseLayout.addWidget(self.browseRight)
        self.browseView = qtw.QWidget()
        self.browseView.setLayout(self.browseLayout)

        self.centerStack.addWidget(self.patientView)
        self.centerStack.addWidget(self.browseView)
        self.mainLayout.addWidget(self.centerStack)
        
        #Creating the bottom widget command line
        self.command = CommandLineView()
        self.mainLayout.addWidget(self.command)
        
        
        #Connecting logic
        self.topbar.patientButton.clicked.connect(self.showPatient)
        self.topbar.browseButton.clicked.connect(self.showBrowse)
        self.topbar.refillButton.clicked.connect(self.refill)
        self.topbar.scheduleButton.clicked.connect(self.scheduleClicked)
        self.patientView.patient_id_input.returnPressed.connect(self.showPatientSearch)
        self.datesDisplay.view.clicked.connect(self.date_submit)
        self.topbar.editButton.clicked.connect(self.editClicked)
        self.editSelected.connect(self.showEdit)
        self.scheduleSelected.connect(self.showSchedule)
        self.refillSelected.connect(self.refill)
        
        #End Code
        self.show()
    #Methods
    def showPatient(self):
        self.centerStack.setCurrentIndex(0)
    def showPatientSearch(self):
        input = self.patientView.patient_id_input.text()
        self.patientSearchView = PatientSearch(input)
        self.patientSearchView.patient_selected.connect(self.patient_submit)
        self.patientSearchView.show()
    def showBrowse(self):
        self.centerStack.setCurrentIndex(1)
    def patient_submit(self, patient_id):
        self.patientView.set_model(self.patientModel.update_query(patient_id))
        self.patientSearchView.close()
    def date_submit(self, index: qtc.QModelIndex):
        row = index.row()
        date = self.datesDisplay.model.data(self.datesDisplay.model.index(row,0))
        self.browseRight.set_model(self.browseModel.show_date(date))
    def editClicked(self):
        selectedIndexes = self.patientView.view.selectionModel().selectedRows()
        if selectedIndexes:
            selectedRow = selectedIndexes[0].row()
            self.editSelected.emit(selectedRow)
    def showEdit(self, row):
        rxnumber = self.patientModel.model.data(self.patientModel.model.index(row,0))
        self.editView = EditWindow(rxnumber)
        self.editView.show()
    def scheduleClicked(self):
        selectedIndexes = self.patientView.view.selectionModel().selectedRows()
        if selectedIndexes:
            selectedRow = selectedIndexes[0].row()
            self.scheduleSelected.emit(selectedRow)
    def showSchedule(self, row):
        rxnumber = self.patientModel.model.data(self.patientModel.model.index(row,0))
        self.scheduleView = Schedule(rxnumber)
        self.scheduleView.show()
    def refillClicked(self):
        selectedIndexes = self.patientView.view.selectionModel().selectedRows()
        if selectedIndexes:
            selectedRow = selectedIndexes[0].row()
            self.refillSelected.emit(selectedRow)
    def refill(self, row):
        rxnumber = self.patientModel.model.data(self.patientModel.model.index(row,0))
        #Refill logic
        self.refillCheckQuery = qts.QSqlQuery()
        self.refillCheckQuery.prepare("SELECT refill_number, refill_total FROM rx where rx_number = :rx")
        self.refillCheckQuery.bindValue(":rx", rxnumber)
        self.refillCheckQuery.exec()
        self.refillCheckQuery.next()
        if self.refillCheckQuery.value('refill_number') < self.refillCheckQuery.value('refill_total'):
            self.refillActionQuery = qts.QSqlQuery()
            self.refillActionQuery.prepare("UPDATE rx SET refill_number = refill_number + 1 WHERE rx_number = :rx")
            self.refillActionQuery.bindValue(":rx", rxnumber)
            self.refillActionQuery.exec()
            msg = qtw.QMessageBox()
            msg.warning(None, "Refill Success", "Refill number successfully updated")
        else:
            msg = qtw.QMessageBox()
            msg.warning(None, "Refill Unsuccessful", "Invalid number of refills remaining")

class TopBarView(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QHBoxLayout())
        self.patientButton = qtw.QPushButton(
            "Patient\nF5",
            self,
            shortcut= qtg.QKeySequence('F5')
        )
        self.browseButton = qtw.QPushButton(
            "Browse\nF6",
            self,
            shortcut= qtg.QKeySequence('F6')
        )
        self.editButton = qtw.QPushButton(
            'Edit\nCtrl + E',
            self,
            shortcut= qtg.QKeySequence('Ctrl+E')
        )
        self.refillButton = qtw.QPushButton(
            "Refill\nCtrl + R",
            self,
            shortcut= qtg.QKeySequence('Ctrl+R')
        )
        self.scheduleButton = qtw.QPushButton(
            "Schedule\nS",
            self,
            shortcut= qtg.QKeySequence('S')
        )
        self.layout().addWidget(self.patientButton)
        self.layout().addWidget(self.browseButton)
        self.layout().addWidget(self.editButton)
        self.layout().addWidget(self.refillButton)
        self.layout().addWidget(self.scheduleButton)

class Schedule(qtw.QWidget):
    def __init__(self, rx_number):
        super().__init__()
        self.rx_number = rx_number
        self.query = qts.QSqlQuery()
        self.query.prepare("SELECT * FROM rx WHERE rx_number = :rx")
        self.query.bindValue(':rx', rx_number)
        self.query.exec()
        self.query.next()
        self.label = qtw.QLabel('Enter date in MMDDYY format, or +D')
        self.entry = qtw.QLineEdit()
        self.setLayout(qtw.QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.entry)
        self.entry.setText(self.query.value('date_filled'))
        self.entry.returnPressed.connect(self.save)

    def save(self):
        input = self.entry.text()
        if input.isdigit():
            if len(input) == 2 or len(input) == 1:
                self.saveQuery = qts.QSqlQuery()
                self.saveQuery.prepare("UPDATE rx SET date_filled = DATE(date_filled, '+' || :date || ' days') WHERE rx_number = :rx")
                self.saveQuery.bindValue(':rx', self.rx_number)
                self.saveQuery.bindValue(':date', input)
                if self.saveQuery.exec():
                    self.close()
            if len(input) == 6:
                binder = "20" + input[4:] + "-" + input[:2] + "-" + input[2:4]
                self.saveQuery = qts.QSqlQuery()
                self.saveQuery.prepare("UPDATE rx SET date_filled = :date  WHERE rx_number = :rx")
                self.saveQuery.bindValue(':rx', self.rx_number)
                self.saveQuery.bindValue(':date', binder)
                if self.saveQuery.exec():
                    self.close()

class EditWindow(qtw.QWidget):
    def __init__(self, rx_number):
        super().__init__()
        #Establish the query that will feed the entire window
        self.query = qts.QSqlQuery()
        self.query.prepare("""SELECT * FROM rx 
        LEFT JOIN prescriber ON
        rx.prescriber_id = prescriber.prescriber_id LEFT JOIN
        patients ON rx.patient_id = patients.patient_id
        LEFT JOIN drugs on rx.drug_id = drugs.drug_id              
        WHERE rx_number=:rx""")
        self.query.bindValue(':rx', rx_number)
        self.query.exec()
        self.query.next()
        #Master Layout
        self.setLayout(qtw.QVBoxLayout())
        #Top Left Patient info and Top Right Prescriber info
        self.top = qtw.QWidget()
        self.topLayout = qtw.QHBoxLayout()
        self.top.setLayout(self.topLayout)

        self.topLeftWidget = qtw.QWidget()
        self.topLeftLayout = qtw.QGridLayout()
        self.topLeftWidget.setLayout(self.topLeftLayout)
        self.topLayout.addWidget(self.topLeftWidget)

        self.topRightWidget = qtw.QWidget()
        self.topRightLayout = qtw.QGridLayout()
        self.topRightWidget.setLayout(self.topRightLayout)
        self.topLayout.addWidget(self.topRightWidget)
        #Middle is just info about the script
        self.middle = qtw.QWidget()
        self.middleLayout = qtw.QGridLayout()
        self.middle.setLayout(self.middleLayout)
        #Bottom Buttons
        self.bottomLayout = qtw.QHBoxLayout()
        self.bottom = qtw.QWidget()
        self.bottom.setLayout(self.bottomLayout)
        #Add it all together
        self.layout().addWidget(self.top)
        self.layout().addWidget(self.middle)
        self.layout().addWidget(self.bottom)

        #Top Left Logic, should be uneditable
        self.patientName = qtw.QLabel('Patient:')
        self.patientNameLine = qtw.QLineEdit()
        self.patientDOB = qtw.QLabel('DOB:')
        self.patientDOBLine = qtw.QLineEdit()
        self.patientPhone = qtw.QLabel('Phone #:')
        self.patientPhoneLine = qtw.QLineEdit()
        self.dateFilled = qtw.QLabel('Date Filled: ')
        self.dateFilledBox = qtw.QDateEdit()
        self.statusLabel = qtw.QLabel('Script Status: ')
        self.statusLine = qtw.QLineEdit()

        self.topLeftLayout.addWidget(self.patientName, 0, 0)
        self.topLeftLayout.addWidget(self.patientNameLine, 0 ,1)
        self.topLeftLayout.addWidget(self.patientDOB, 1, 0)
        self.topLeftLayout.addWidget(self.patientDOBLine, 1, 1)
        self.topLeftLayout.addWidget(self.patientPhone, 2 ,0)
        self.topLeftLayout.addWidget(self.patientPhoneLine, 2, 1)
        self.topLeftLayout.addWidget(self.dateFilled, 3, 0)
        self.topLeftLayout.addWidget(self.dateFilledBox, 3, 1)
        self.topLeftLayout.addWidget(self.statusLabel, 4, 0)
        self.topLeftLayout.addWidget(self.statusLine, 4 , 1)
        #Top Left Logic and formatting
        self.patPhoneString = list(str(self.query.value('patients.phone')))
        self.patPhoneString.insert(3, '-')
        self.patPhoneString.insert(7, '-')
        self.patPhoneFormat = ''.join(self.patPhoneString)
        self.dobString = list(str(self.query.value('patients.dob'))[4:] + str(self.query.value('patients.dob'))[:4])
        while '-' in self.dobString:
            self.dobString.remove('-')
        self.dobString.insert(2, '/')
        self.dobString.insert(5, '/')
        self.dobFormat = ''.join(self.dobString) 
        self.patientNameLine.setText(str(self.query.value('patients.fname')) + ' ' + str(self.query.value('patients.lname')))
        self.patientDOBLine.setText(self.dobFormat)
        self.patientPhoneLine.setText(self.patPhoneFormat)
        self.patientNameLine.setReadOnly(True)
        self.patientDOBLine.setReadOnly(True)
        self.patientPhoneLine.setReadOnly(True)
        self.dFilledString = str(self.query.value('rx.date_filled')).split('-')
        self.dateFilledBox.setDate(qtc.QDate(int(self.dFilledString[0]), int(self.dFilledString[1]), int(self.dFilledString[2])))
        self.statusLine.setText(self.query.value('status'))

        #Top Right (Prescriber info)
        self.docName = qtw.QLabel('Prescriber:')
        self.docNameLine = qtw.QLineEdit()
        self.npi = qtw.QLabel('NPI:')
        self.npiLine = qtw.QLineEdit()
        self.dea = qtw.QLabel('DEA:')
        self.deaLine = qtw.QLineEdit()
        self.phone = qtw.QLabel('Phone #:')
        self.phoneLine = qtw.QLineEdit()
        self.fax = qtw.QLabel('Fax #:')
        self.faxLine = qtw.QLineEdit()

        self.topRightLayout.addWidget(self.docName, 0, 0)
        self.topRightLayout.addWidget(self.docNameLine, 0, 1, 1, 3)
        self.topRightLayout.addWidget(self.npi, 1, 0)
        self.topRightLayout.addWidget(self.npiLine, 1, 1)
        self.topRightLayout.addWidget(self.dea, 2, 0)
        self.topRightLayout.addWidget(self.deaLine, 2, 1)
        self.topRightLayout.addWidget(self.phone, 1, 2)
        self.topRightLayout.addWidget(self.phoneLine, 1, 3)
        self.topRightLayout.addWidget(self.fax, 2, 2)
        self.topRightLayout.addWidget(self.faxLine, 2, 3)

        #Top Right Logic
        self.phoneString = list(str(self.query.value('phone')))
        self.faxString = list(str(self.query.value('fax')))
        self.phoneString.insert(3, '-')
        self.phoneString.insert(7, '-')
        self.faxString.insert(3, '-')
        self.faxString.insert(7, '-')
        self.phoneFormat = ''.join(self.phoneString)
        self.faxFormat = ''.join(self.faxString)
        self.docNameLine.setText(str(self.query.value('prescriber.fname') + ' ' + str(self.query.value('prescriber.lname'))))
        self.deaLine.setText(str(self.query.value('dea')))
        self.npiLine.setText(str(self.query.value('npi')))
        self.phoneLine.setText(self.phoneFormat)
        self.faxLine.setText(self.faxFormat)

        #Formatting topRightLayout
        self.deaLine.setMaximumWidth(150)
        self.npiLine.setMaximumWidth(150)
        self.phoneLine.setMaximumWidth(150)
        self.faxLine.setMaximumWidth(150)
        self.docNameLine.setMinimumWidth(300)
        self.deaLine.setReadOnly(True)
        self.npiLine.setReadOnly(True)
        self.phoneLine.setReadOnly(True)
        self.faxLine.setReadOnly(True)

        #Prescription Widgets to be added to middleLayout
        self.drugName = qtw.QLabel('Drug:')
        self.drugNameLine = qtw.QLineEdit()
        self.drugNDC = qtw.QLabel('NDC:')
        self.drugNDCLine = qtw.QLineEdit()
        self.drugQty = qtw.QLabel('Qty:')
        self.drugQtyLine = qtw.QLineEdit()
        self.daySupply = qtw.QLabel('Days:')
        self.daySupplyLine = qtw.QLineEdit()
        self.presQty = qtw.QLabel('Pres Qty:')
        self.presQtyLine = qtw.QLineEdit()
        self.presDaySupply = qtw.QLabel('Pres Days:')
        self.presDaySupplyLine = qtw.QLineEdit()

        self.middleLayout.addWidget(self.drugName, 0, 0, alignment=qtc.Qt.AlignRight)
        self.middleLayout.addWidget(self.drugNameLine, 0, 1, 1, 3)
        self.middleLayout.addWidget(self.drugNDC, 1, 0, alignment=qtc.Qt.AlignRight)
        self.middleLayout.addWidget(self.drugNDCLine, 1, 1, 1, 3)
        self.middleLayout.addWidget(self.drugQty, 2, 0, alignment=qtc.Qt.AlignRight)
        self.middleLayout.addWidget(self.drugQtyLine, 2, 1)
        self.middleLayout.addWidget(self.presQty, 2, 2, alignment=qtc.Qt.AlignRight)
        self.middleLayout.addWidget(self.presQtyLine, 2, 3)
        self.middleLayout.addWidget(self.daySupply, 3, 0, alignment=qtc.Qt.AlignRight)
        self.middleLayout.addWidget(self.daySupplyLine, 3, 1)
        self.middleLayout.addWidget(self.presDaySupply, 3, 2, alignment=qtc.Qt.AlignRight)
        self.middleLayout.addWidget(self.presDaySupplyLine, 3, 3)

        #Middle layer logic
        self.presDaySupplyLine.setText(str(self.query.value('day_supply')))
        self.presQtyLine.setText(str(self.query.value('quantity')))
        self.drugNameLine.setText(str(self.query.value('drug_name')) + ' ' + str(self.query.value('strength')))
        self.drugNDCLine.setText(str(self.query.value('ndc')))

        #Formatting the middlelayout widgets
        self.drugQtyLine.setMaximumWidth(100)
        self.daySupplyLine.setMaximumWidth(100)
        self.presQtyLine.setMaximumWidth(100)
        self.presDaySupplyLine.setMaximumWidth(100)
        self.presQtyLine.setReadOnly(True)
        self.presDaySupplyLine.setReadOnly(True)

        #Bottom buttons
        self.transmitClaimButton = qtw.QPushButton(
            'Transmit Claim\nCtrl+X',
            self,
            shortcut= qtg.QKeySequence('Ctrl+X')
            )
        self.transmitReversalButton = qtw.QPushButton(
            "Reverse Claim\nCtrl+Shift+X",
            self,
            shortcut= qtg.QKeySequence('Ctrl+Shift+X')
        )
        self.saveEditButton = qtw.QPushButton(
            'Save\nCtrl+S',
            self,
            shortcut = qtg.QKeySequence('Ctrl+S')
        )
        self.exitButton = qtw.QPushButton(
            'Exit\nEsc',
            self,
            shortcut = qtg.QKeySequence('Esc')
        )
        self.bottomLayout.addWidget(self.transmitClaimButton)
        self.bottomLayout.addWidget(self.transmitReversalButton)
        self.bottomLayout.addWidget(self.saveEditButton)
        self.bottomLayout.addWidget(self.exitButton)

        #Connecting logic
        self.drugNameLine.returnPressed.connect(self.showDrugSearch)
        self.docNameLine.returnPressed.connect(self.showDoctorSearch)
        self.exitButton.clicked.connect(self.exitPressed)
        self.saveEditButton.clicked.connect(self.savePressed)
        self.transmitClaimButton.clicked.connect(self.transmitPressed)
        self.transmitReversalButton.clicked.connect(self.reversePressed)
    #Methods
    def exitPressed(self):
        self.close()
    def transmitPressed(self):
        if self.query.value('rx.status') == 'U':
            updatequery = qts.QSqlQuery()
            updatequery.prepare("UPDATE rx SET status = 'B' WHERE rx_number = :rx_number")
            updatequery.bindValue(':rx_number', self.query.value('rx_number'))
            if updatequery.exec():
                self.statusLine.setText('B')
    def reversePressed(self):
        if self.query.value('rx.status') == 'B':
            updatequery = qts.QSqlQuery()
            updatequery.prepare("UPDATE rx SET status = 'U' WHERE rx_number = :rx_number")
            updatequery.bindValue(':rx_number', self.query.value('rx_number'))
            if updatequery.exec():
                self.statusLine.setText('U')
    #Reads the values in the lines and updates the database with them
    def savePressed(self):
        prescriber = int(self.npiLine.text())
        docquery = qts.QSqlQuery()
        docquery.prepare("SELECT * FROM prescriber WHERE npi = :npi")
        docquery.bindValue(':npi', prescriber)
        docquery.exec()
        docquery.next()
        drug = int(self.drugNDCLine.text())
        drugquery = qts.QSqlQuery()
        drugquery.prepare("SELECT * FROM drugs WHERE ndc = :ndc")
        drugquery.bindValue(':ndc', drug)
        drugquery.exec()
        drugquery.next()
        updatequery = qts.QSqlQuery()
        updatequery.prepare("UPDATE rx SET prescriber_id = :prescriber_id , drug_id = :drug_id WHERE rx_number = :rx_number")
        updatequery.bindValue(':prescriber_id', docquery.value('prescriber_id'))
        updatequery.bindValue(':drug_id', drugquery.value('drug_id'))
        updatequery.bindValue(':rx_number', self.query.value('rx_number'))
        updatequery.exec()
        self.close()
    def showDrugSearch(self):
        input = self.drugNameLine.text()
        self.drugSearch = DrugSearch(input)
        self.drugSearch.drug_selected.connect(self.drug_submit)
        self.drugSearch.show()
    def drug_submit(self, drug_id):
        query = qts.QSqlQuery()
        query.prepare("SELECT * FROM drugs WHERE drug_id=:drug_id")
        query.bindValue(':drug_id', drug_id)
        query.exec()
        query.next()
        self.drugNameLine.setText(str(query.value('drug_name')) + ' ' + str(query.value('strength')))
        self.drugNDCLine.setText(str(query.value('ndc')))
        self.drugSearch.close()
    def showDoctorSearch(self):
        input = self.docNameLine.text()
        self.docSearch = DoctorSearch(input)
        self.docSearch.doctor_selected.connect(self.doctor_submit)
        self.docSearch.show()
    def doctor_submit(self, prescriber_id):
        query = qts.QSqlQuery()
        query.prepare("SELECT * FROM prescriber WHERE prescriber_id=:prescriber_id")
        query.bindValue(':prescriber_id', prescriber_id)
        query.exec()
        query.next()
        self.phoneString = list(str(query.value('phone')))
        self.faxString = list(str(query.value('fax')))
        self.phoneString.insert(3, '-')
        self.phoneString.insert(7, '-')
        self.faxString.insert(3, '-')
        self.faxString.insert(7, '-')
        self.phoneFormat = ''.join(self.phoneString)
        self.faxFormat = ''.join(self.faxString)
        self.docNameLine.setText(str(query.value('fname') + ' ' + str(query.value('lname'))))
        self.deaLine.setText(str(query.value('dea')))
        self.npiLine.setText(str(query.value('npi')))
        self.phoneLine.setText(self.phoneFormat)
        self.faxLine.setText(self.faxFormat)
        self.docSearch.close()
        
class PatientView(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.patient_id_input = qtw.QLineEdit()
        self.view = qtw.QTableView()
        self.layout().addWidget(self.patient_id_input)
        self.layout().addWidget(self.view)

    def set_model(self, model):
        self.view.setModel(model)
        
class PatientSearch(qtw.QWidget):
    patient_selected = qtc.pyqtSignal(int)
    def __init__(self, input):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.view = qtw.QTableView()
        self.model = qts.QSqlQueryModel()
        inputstr = input.split(',')
        emptylist = ["" for x in range(3)]
        for i, value in enumerate(inputstr):
            emptylist[i] = value
        lname = emptylist[0]
        fname = emptylist[1]
        dob = emptylist[2]
        query = f"""
        SELECT *
        FROM patients
        WHERE lname LIKE '{lname}%' AND fname LIKE '{fname}%'
        AND dob LIKE '{dob}%'
        """
        self.model.setQuery(query)
        self.view.setModel(self.model)
        self.layout().addWidget(self.view)
        self.view.doubleClicked.connect(self.row_selected)
    
    def row_selected(self, index):
        patient_id = self.view.model().data(self.view.model().index(index.row(), 0))
        self.patient_selected.emit(patient_id)

class DrugSearch(qtw.QWidget):
    drug_selected = qtc.pyqtSignal(int)
    def __init__(self, input):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.view = qtw.QTableView()
        self.model = qts.QSqlQueryModel()
        drug = input
        query = f"""
        SELECT *
        FROM drugs
        WHERE drug_name LIKE '%{drug}%'
        """
        self.model.setQuery(query)
        self.view.setModel(self.model)
        self.layout().addWidget(self.view)
        self.view.doubleClicked.connect(self.row_selected)

    def row_selected(self, index):
        drug_id = self.view.model().data(self.view.model().index(index.row(), 0))
        self.drug_selected.emit(drug_id)

class DoctorSearch(qtw.QWidget):
    doctor_selected = qtc.pyqtSignal(int)
    def __init__(self, input):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.view = qtw.QTableView()
        self.model = qts.QSqlQueryModel()
        inputstr = input.split(',')
        emptylist = ["" for x in range(4)]
        for i, value in enumerate(inputstr):
            emptylist[i] = value
        lname = emptylist[0]
        fname = emptylist[1]
        npi = emptylist[2]
        dea = emptylist[3]
        query = ''
        if npi:
            emptylist[2] = int(emptylist[2])
            query = f"""
            SELECT *
            FROM prescriber
            WHERE npi = {npi}
            """
        elif dea:
            query = f"""
            SELECT *
            FROM prescriber
            WHERE dea LIKE '{dea}'
            """
        else:
            query = f"""
            SELECT *
            FROM prescriber
            WHERE lname LIKE '{lname}%' AND fname LIKE '{fname}%'
            """ 
        self.model.setQuery(query)
        self.view.setModel(self.model)
        self.layout().addWidget(self.view)
        self.view.doubleClicked.connect(self.row_selected)

    def row_selected(self, index):
        doctor_id = self.view.model().data(self.view.model().index(index.row(), 0))
        self.doctor_selected.emit(doctor_id)
        
class PatientModel:
    def __init__(self):
        self.model = qts.QSqlQueryModel()

    def update_query(self, patient_id):
        query = f"""
        SELECT rx.rx_number, rx.refill_number, rx.refill_total,
        drugs.drug_name, drugs.strength, rx.quantity, rx.day_supply, rx.date_filled, 
        prescriber.fname, prescriber.lname
        FROM patients
        LEFT JOIN rx ON patients.patient_id = rx.patient_id
        LEFT JOIN drugs ON rx.drug_id = drugs.drug_id
        LEFT JOIN prescriber ON rx.prescriber_id = prescriber.prescriber_id
        WHERE patients.patient_id = {patient_id}
        """
        self.model.setQuery(query)
        return self.model

class DatesDisplay(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QHBoxLayout())
        self.view = qtw.QTableView()
        self.model = qts.QSqlQueryModel()
        query = """
        SELECT rx.date_filled
        FROM rx
        GROUP BY rx.date_filled
        """
        self.model.setQuery(query)
        self.view.setModel(self.model)

        self.layout().addWidget(self.view)
        
class BrowseView(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QHBoxLayout())
        self.view = qtw.QTableView()
        self.layout().addWidget(self.view)

    def set_model(self, model):
        self.view.setModel(model)

class BrowseModel:
    def __init__(self):
        self.model = qts.QSqlQueryModel()

    def show_date(self, date):
        query = f"""
        SELECT rx.rx_number, rx.refill_number, rx.refill_total,
        drugs.drug_name, drugs.strength, rx.quantity, rx.day_supply, rx.date_filled, rx.prescriber
        FROM patients
        LEFT JOIN rx ON patients.patient_id = rx.patient_id
        LEFT JOIN drugs on rx.drug_id = drugs.drug_id
        WHERE rx.date_filled = "{date}"
        """
        self.model.setQuery(query)
        return self.model

class CommandLineView(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.commandLine = qtw.QLineEdit()

        self.layout().addWidget(self.commandLine)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())