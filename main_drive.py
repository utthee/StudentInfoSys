import sys
import csv
import re

from mainUI import Ui_MainWindow
from updateStudent import Ui_StudentDialog
from updateProgram import Ui_ProgramDialog
from updateCollege  import Ui_CollegeDialog

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui

STUDENT_CSV = "STUDENT.csv"
PROGRAM_CSV = "PROGRAM.csv"
COLLEGE_CSV = "COLLEGE.csv"

class MainClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.file_paths = [STUDENT_CSV, PROGRAM_CSV, COLLEGE_CSV]
        self.headers = [[], [], []]  # Store CSV headers
        self.current_table_index = self.displayComboBox.currentIndex()  # Track the current table being displayed
        self.data = [[], [], []]  # Store CSV data for each table
        self.loadCSVFiles()

        self.addStudentButton.clicked.connect(self.addStudentEntry)
        self.addProgramButton.clicked.connect(self.addProgramEntry)
        self.addCollegeButton.clicked.connect(self.addCollegeEntry)       

        self.pushButton.clicked.connect(self.deleteEntry)
        self.pushButton_2.clicked.connect(self.updateEntry)
        self.refreshButton.clicked.connect(self.displayTable)

        self.sortComboBox.currentIndexChanged.connect(self.sortLayout)
        self.searchButton.clicked.connect(self.searchEntry)

        self.displayComboBox.currentIndexChanged.connect(self.displayTable)

#------------------------------------------------------------------------------      MAJOR FUNCTIONS     ------------------------------------------------------------------------------------

#------------------------------------------------------------------------------      MAJOR FUNCTIONS     ------------------------------------------------------------------------------------

    def loadCSVFiles(self):
        for i, file_path in enumerate(self.file_paths):
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    self.headers[i] = next(reader)
                    self.data[i] = [row for row in reader]
            except FileNotFoundError:
                print(f"Error: {file_path} not found.")
        
        self.displayTable()

    def displayTable(self):
        # Populate items to the combo boxes
        self.programChoices()
        self.collegeChoices()

        # Reset hidden rows
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHidden(row, False)

        # Reset selected row after every operation
        self.tableWidget.clearSelection()
        self.tableWidget.setCurrentItem(None)

        if self.displayComboBox.currentIndex() == 0:      
            self.readStudentCSV()
            self.showTable()
            return

        elif self.displayComboBox.currentIndex() == 1:  
            self.readProgramCSV()
            self.showTable()
            return

        elif self.displayComboBox.currentIndex() == 2:
            self.readCollegeCSV()
            self.showTable()
            return
    
    def clearHeaderBox(self):
        # Resets header items whenever a different table is shown
        self.sortComboBox.clear()
        self.sortComboBox.addItems(self.headers[self.current_table_index])
        
        self.searchBox.clear()
        self.searchComboBox.clear()
        self.searchComboBox.addItem("")
        self.searchComboBox.addItems(self.headers[self.current_table_index])

    def showTable(self):
        self.current_table_index = self.displayComboBox.currentIndex()
        self.clearHeaderBox()

        self.tableWidget.setColumnCount(len(self.headers[self.current_table_index]))
        self.tableWidget.setHorizontalHeaderLabels(self.headers[self.current_table_index])
        self.tableWidget.setRowCount(len(self.data[self.current_table_index]))

        # Populate table
        for row_idx, row in enumerate(self.data[self.current_table_index]):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)

        # Fits the columns to the length of the table
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def searchEntry(self):
        searched_item = self.searchBox.text().lower()
        search_filter = self.searchComboBox.currentText()

        if not searched_item:
            self.searchInputError()
            return

        if not search_filter:
            self.searchFilterError()
            return

        header_labels = self.headers[self.current_table_index]
        filter_col_index = header_labels.index(search_filter)

        # Tracks matched entries
        match_counter = 0

        # Iterate through table rows and hide/show based on search match
        for row in range(self.tableWidget.rowCount()):
            cell_item = self.tableWidget.item(row, filter_col_index)
            cell_text = cell_item.text().lower() if cell_item else ""
            
            match = searched_item in cell_text
            self.tableWidget.setRowHidden(row, not match)

            if match:
                match_counter += 1

        # If no matched entries, display error message
        if match_counter == 0:
            self.displayTable()
            self.searchError()
            return
    
    def searchError(self):
        searchErrorMsg = QtWidgets.QMessageBox(self)
        searchErrorMsg.setWindowTitle("No Results")
        searchErrorMsg.setText("The item you are trying to search does not exist.")
        searchErrorMsg.setIcon(QtWidgets.QMessageBox.Warning)
        searchErrorMsg.exec_()

    def searchFilterError(self):
        searchFilterErrorMsg = QtWidgets.QMessageBox(self)
        searchFilterErrorMsg.setWindowTitle("Input Mismatch")
        searchFilterErrorMsg.setText("Please select a search filter.")
        searchFilterErrorMsg.setIcon(QtWidgets.QMessageBox.Warning)
        searchFilterErrorMsg.exec_()

    def searchInputError(self):
        searchInputErrorMsg = QtWidgets.QMessageBox(self)
        searchInputErrorMsg.setWindowTitle("Input Error")
        searchInputErrorMsg.setText("Please input on the search box.")
        searchInputErrorMsg.setIcon(QtWidgets.QMessageBox.Warning)
        searchInputErrorMsg.exec_()


    def deleteEntry(self):
        if self.tableWidget.currentRow() >= 0:
            if self.displayComboBox.currentIndex() == 0:
                self.deleteStudentConfirmation()
                return
            
            elif self.displayComboBox.currentIndex() == 1:
                self.deleteProgramConfirmation()
                return
            
            elif self.displayComboBox.currentIndex() == 2:
                self.deleteCollegeConfirmation()
                return
        else:
            self.deleteError()

    def deleteStudentConfirmation(self):
        deleteStudentMsg = QtWidgets.QMessageBox(self)
        deleteStudentMsg.setWindowTitle("Delete Confirmation")
        deleteStudentMsg.setText("Are you sure you want to delete this student entry?")
        deleteStudentMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteStudentMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        deleteStudentMsg.setDefaultButton(QMessageBox.Cancel)
        
        confirm = deleteStudentMsg.exec_()

        if confirm == QMessageBox.Yes:
            self.deleteStudentEntry()

    def deleteStudentSuccess(self):
        deleteStudentSuccessMsg = QtWidgets.QMessageBox(self)
        deleteStudentSuccessMsg.setWindowTitle("Delete Success")
        deleteStudentSuccessMsg.setText("The student entry has been successfully deleted.")
        deleteStudentSuccessMsg.setIcon(QtWidgets.QMessageBox.Information)
        deleteStudentSuccessMsg.exec_()

    def deleteProgramConfirmation(self):
        deleteProgramMsg = QtWidgets.QMessageBox(self)
        deleteProgramMsg.setWindowTitle("Delete Confirmation")
        deleteProgramMsg.setText("Are you sure you want to delete this program entry? Students enrolled in this program will be affected.")
        deleteProgramMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteProgramMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        deleteProgramMsg.setDefaultButton(QMessageBox.Cancel)
        
        confirm = deleteProgramMsg.exec_()

        if confirm == QMessageBox.Yes:
            self.deleteProgramEntry()

    def deleteProgramSuccess(self):
        deleteProgramSuccessMsg = QtWidgets.QMessageBox(self)
        deleteProgramSuccessMsg.setWindowTitle("Delete Success")
        deleteProgramSuccessMsg.setText("The program has been successfully deleted.")
        deleteProgramSuccessMsg.setIcon(QtWidgets.QMessageBox.Information)
        deleteProgramSuccessMsg.exec_()

    def deleteCollegeConfirmation(self):
        deleteCollegeMsg = QtWidgets.QMessageBox(self)
        deleteCollegeMsg.setWindowTitle("Delete Confirmation")
        deleteCollegeMsg.setText("Are you sure you want to delete this college entry? All programs under this college will also be deleted.")
        deleteCollegeMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteCollegeMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        deleteCollegeMsg.setDefaultButton(QMessageBox.Cancel)

        confirm = deleteCollegeMsg.exec_()

        if confirm == QMessageBox.Yes:
            self.deleteCollegeEntry()

    def deleteCollegeSuccess(self):
        deleteCollegeSuccessMsg = QtWidgets.QMessageBox(self)
        deleteCollegeSuccessMsg.setWindowTitle("Delete Success")
        deleteCollegeSuccessMsg.setText("The college has been successfully deleted.")
        deleteCollegeSuccessMsg.setIcon(QtWidgets.QMessageBox.Information)
        deleteCollegeSuccessMsg.exec_()

    def deleteError(self):
        deleteErrorMsg = QtWidgets.QMessageBox(self)
        deleteErrorMsg.setWindowTitle("Delete Error")
        deleteErrorMsg.setText("Please select a row to delete.")
        deleteErrorMsg.setIcon(QtWidgets.QMessageBox.Warning)
        deleteErrorMsg.exec_()

    def addStudentSuccess(self):
        addStudentMsg = QtWidgets.QMessageBox(self)
        addStudentMsg.setWindowTitle("Input Added")
        addStudentMsg.setText("Student entry has been successfully added")
        addStudentMsg.setIcon(QtWidgets.QMessageBox.Information)
        addStudentMsg.exec_()

    def addProgramSuccess(self):
        addProgramMsg = QtWidgets.QMessageBox(self)
        addProgramMsg.setWindowTitle("Input Added")
        addProgramMsg.setText("Program entry has been successfully added")
        addProgramMsg.setIcon(QtWidgets.QMessageBox.Information)
        addProgramMsg.exec_()

    def addCollegeSuccess(self):
        addCollegeMsg = QtWidgets.QMessageBox(self)
        addCollegeMsg.setWindowTitle("Input Added")
        addCollegeMsg.setText("Program entry has been successfully added")
        addCollegeMsg.setIcon(QtWidgets.QMessageBox.Information)
        addCollegeMsg.exec_()
        
    def updateEntry(self):
        if self.tableWidget.currentRow() >= 0:
            if self.displayComboBox.currentIndex() == 0:
                self.updateStudentEntry()
                return
            elif self.displayComboBox.currentIndex() == 1:
                self.updateProgramEntry()
                return
            elif self.displayComboBox.currentIndex() == 2:
                self.updateCollegeEntry()
                return
        else:
            self.updateError()

    def updateStudentSuccess(self):
        updateStudentMsg = QtWidgets.QMessageBox(self)
        updateStudentMsg.setWindowTitle("Input Updated")
        updateStudentMsg.setText("Student entry has been successfully updated")
        updateStudentMsg.setIcon(QtWidgets.QMessageBox.Information)
        updateStudentMsg.exec_()

    def updateProgramSuccess(self):
        updateProgramMsg = QtWidgets.QMessageBox(self)
        updateProgramMsg.setWindowTitle("Input Updated")
        updateProgramMsg.setText("Program entry has been successfully updated")
        updateProgramMsg.setIcon(QtWidgets.QMessageBox.Information)
        updateProgramMsg.exec_()

    def updateCollegeSuccess(self):
        updateCollegeMsg = QtWidgets.QMessageBox(self)
        updateCollegeMsg.setWindowTitle("Input Updated")
        updateCollegeMsg.setText("College entry has been successfully updated")
        updateCollegeMsg.setIcon(QtWidgets.QMessageBox.Information)
        updateCollegeMsg.exec_()

    def updateError(self):
        updateErrorMsg = QtWidgets.QMessageBox(self)
        updateErrorMsg.setWindowTitle("Update Error")
        updateErrorMsg.setText("Please select a row to update.")
        updateErrorMsg.setIcon(QtWidgets.QMessageBox.Warning)
        updateErrorMsg.exec_()
        
    def updateStudentEntry(self):
        self.readStudentCSV()
        selected_row = self.tableWidget.currentRow()
        
        data = self.data[0]
                
        if 0 <= selected_row < len(data):
            updateIDNumber = self.tableWidget.item(selected_row, 0).text()
            updateFirstName = self.tableWidget.item(selected_row, 1).text()
            updateLastName = self.tableWidget.item(selected_row, 2).text()
            updateYearLevel = self.tableWidget.item(selected_row, 3).text()
            updateGender = self.tableWidget.item(selected_row, 4).text()
            updateProgramCode = self.tableWidget.item(selected_row, 5).text()

            studentEditor = StudentDialog(updateIDNumber, updateFirstName, updateLastName, updateYearLevel, updateGender, updateProgramCode)
            if studentEditor.exec_():
                updated_values = studentEditor.updatedStudentData()

                if updated_values != [updateIDNumber, updateFirstName, updateLastName, updateYearLevel, updateGender, updateProgramCode]:
                    data[selected_row] = updated_values
                
                    self.saveStudentCSV(data)
                    self.displayTable()
                    self.updateStudentSuccess()

    def updateProgramEntry(self):
        self.readProgramCSV()
        selected_row = self.tableWidget.currentRow()

        data = self.data[1]

        if 0 <= selected_row < len(data):
            updateProgramCode = self.tableWidget.item(selected_row, 0).text()
            updateProgramName = self.tableWidget.item(selected_row, 1).text()
            updateCollegeCode = self.tableWidget.item(selected_row, 2).text()

            programEditor = ProgramDialog(updateProgramCode, updateProgramName, updateCollegeCode)
            if programEditor.exec_():
                updated_values = programEditor.updatedProgramData()
                
                if updated_values != [updateProgramCode, updateProgramName, updateCollegeCode]:
                    data[selected_row] = updated_values

                    for row in self.data[0]:
                        if row[5] == updateProgramCode:
                            row[5] = updated_values[0]

                    self.saveProgramCSV(data)
                    self.saveStudentCSV(self.data[0])
                    self.displayTable()
                    self.updateProgramSuccess()

    def updateCollegeEntry(self):
        self.readCollegeCSV()
        selected_row = self.tableWidget.currentRow()

        data = self.data[2]

        if 0 <= selected_row < len(data):
            updateCollegeCode = self.tableWidget.item(selected_row, 0).text()
            updateCollegeName = self.tableWidget.item(selected_row, 1).text()

            collegeEditor = CollegeDialog(updateCollegeCode, updateCollegeName)
            if collegeEditor.exec_():
                updated_values = collegeEditor.updatedCollegeData()
                
                if updated_values != [updateCollegeCode, updateCollegeName]:
                    data[selected_row] = updated_values

                    for row in self.data[1]:
                        if row[2] == updateCollegeCode:
                            row[2] = updated_values[0]

                    self.saveCollegeCSV(data)
                    self.saveProgramCSV(self.data[1])
                    self.displayTable()
                    self.updateCollegeSuccess()
    
    def sortLayout(self):
        column_index = self.sortComboBox.currentIndex()
        if column_index >= 0:
            self.tableWidget.sortItems(column_index)

#--------------------------------------------------------------------------------     STUDENT     ----------------------------------------------------------------------

#--------------------------------------------------------------------------------     STUDENT     ----------------------------------------------------------------------

    def addStudentEntry(self):
        self.readStudentCSV()
        
        idNumber = self.idNumberEdit.text()
        firstName = self.firstNameEdit.text().strip().title()
        lastName = self.lastNameEdit.text().strip().title()
        yearLevel = self.yearLevelComboBox.currentText()
        gender = self.genderComboBox.currentText()
        programCode = self.programCodeBox.currentText()

        # Check whether the displayed table is the correct one.
        if self.current_table_index != 0:
            QMessageBox.warning(self, "Table Mismatch", "Must be on student table to add.")
            return

        if not (idNumber and firstName and lastName and programCode):
            QMessageBox.warning(self, "Input Error", "All required fields must be field up.")
            return

        if not re.fullmatch(r'20\d{2}-\d{4}', idNumber):
            QMessageBox.warning(self, "Input Error", "Input a valid ID Number.")
            return
        
        if any(student[0] == idNumber for student in self.data[0]):  
            QMessageBox.warning(self, "Input Error", "The ID Number you're trying to enter already exists.")
            return
        
        # Validates first name and last name, should not contain any numbers
        if not all(char.isalpha() or char.isspace() for char in firstName and lastName):
            QMessageBox.warning(self, "Input Error", "Input a valid name.")
            return
        
        if idNumber and firstName and lastName and yearLevel and gender and programCode:
            studentData = [idNumber, firstName, lastName, yearLevel, gender, programCode]
            self.data[0].append(studentData)

            self.saveStudentCSV(self.data[0])
            self.clearStudentInput()
            self.displayTable()
            self.addStudentSuccess()

    def clearStudentInput(self):
        self.idNumberEdit.clear()
        self.firstNameEdit.clear()
        self.lastNameEdit.clear()
        self.yearLevelComboBox.setCurrentIndex(0)
        self.yearLevelComboBox.setCurrentIndex(0)
        self.programCodeBox.setCurrentIndex(0)

    def readStudentCSV(self):
        with open(STUDENT_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[0] = next(reader)
            data = [row for row in reader]
            self.data[0] = data
    
    def saveStudentCSV(self, data):
        with open(STUDENT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[0])
            writer.writerows(data)
    
    def deleteStudentEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readStudentCSV()
        
        data = self.data[0]
                
        # Remove selected row from data list
        if 0 <= selected_row < len(data):
            del data[selected_row]

        self.saveStudentCSV(data)
        self.displayTable()
        self.deleteStudentSuccess()

    
#--------------------------------------------------------------------------------     PROGRAM     ----------------------------------------------------------------------

#--------------------------------------------------------------------------------     PROGRAM     ----------------------------------------------------------------------


    def addProgramEntry(self):
        self.readProgramCSV()
        
        programCode = self.programCodeEdit2.text().strip().replace(" ","").upper()
        programName = self.programNameEdit.text().strip().title()
        collegeCode = self.collegeCodeBox.currentText()

        # Check whether the displayed table is the correct one.
        if self.current_table_index != 1:
            QMessageBox.warning(self, "Table Mismatch", "Must be on program table to add.")
            return
        
        if not (programCode and programName and collegeCode):
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in programCode and programName):
            QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
            return
        
        for row in self.data[1]:
            existingProgramCode = row[0].strip().upper()
            existingProgramName = row[1].strip().replace(" ", "").upper()

            # Check if the program code already exists
            if existingProgramCode == programCode:
                QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
                return

            # Check if the program name already exists
            if existingProgramName == programName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
                return 

        if programCode and programName and collegeCode:
            programData = [programCode, programName, collegeCode]
            self.data[1].append(programData)

            self.saveProgramCSV(self.data[1])
            self.clearProgramInput()
            self.displayTable()
            self.addProgramSuccess()
    
    def clearProgramInput(self):
        self.programCodeEdit2.clear()
        self.programNameEdit.clear()
        self.collegeCodeBox.setCurrentIndex(0)

    def readProgramCSV(self):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[1] = next(reader)
            data = [row for row in reader]
            self.data[1] = data

    def saveProgramCSV(self, data):
        with open(PROGRAM_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[1])
            writer.writerows(data)
    
    def deleteProgramEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readProgramCSV()

        program_code_to_replace = self.tableWidget.item(selected_row, 0).text()

        data = self.data[1]
        if 0 <= selected_row < len(data):
            del data[selected_row]

        for row in self.data[0]:
            if row[5] == program_code_to_replace:
                row[5] = "UNENROLLED"
            
        self.saveProgramCSV(data)
        self.saveStudentCSV(self.data[0])
        self.displayTable()
        self.deleteProgramSuccess()

    def programChoices(self):
        with open(PROGRAM_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.programCodeBox.clear()
            self.programCodeBox.addItem("")
            self.programCodeBox.addItems(program_codes)

#--------------------------------------------------------------------------------     COLLEGE     ----------------------------------------------------------------------

#--------------------------------------------------------------------------------     COLLEGE     ----------------------------------------------------------------------

    def addCollegeEntry(self):
        self.readCollegeCSV()
        collegeCode = self.collegeCodeEdit2.text().strip().replace(" ","").upper()
        collegeName = self.collegeNameEdit.text().strip().title()

        # Check whether the displayed table is the correct one.
        if self.current_table_index != 2:
            QMessageBox.warning(self, "Incorrect displayed table", "Must be on college table to add.")
            return

        if not collegeCode or not collegeName:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in collegeCode and collegeName):
            QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
            return

        for row in self.data[2]:
            existingCollegeCode = row[0].strip().upper()
            existingCollegeName = row[1].strip().replace(" ", "").upper()

            # Check if the college code already exists
            if existingCollegeCode == collegeCode:
                QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
                return

            # Check if the college name already exists
            if existingCollegeName == collegeName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
                return 

        if collegeCode and collegeName:
            collegeData = [collegeCode, collegeName]
            self.data[2].append(collegeData)

            self.saveCollegeCSV(self.data[2])
            self.clearCollegeInput()
            self.displayTable()
            self.addCollegeSuccess()
    
    def clearCollegeInput(self):
        self.collegeCodeEdit2.clear()
        self.collegeNameEdit.clear()
    
    def readCollegeCSV(self):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[2] = next(reader)
            data = [row for row in reader]
            self.data[2] = data

    def saveCollegeCSV(self, data):
        with open(COLLEGE_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[2])
            writer.writerows(data)
    
    def deleteCollegeEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readProgramCSV()
        self.readCollegeCSV()

        college_code = self.tableWidget.item(selected_row, 0).text()
        
        # Remove from college data
        for row_idx in reversed(range(len(self.data[2]))):  
            if self.data[2][row_idx][0] == college_code:
                del self.data[2][row_idx]

        # Find programs linked to the deleted college
        program_codes_to_remove = set()
        for row in self.data[1]:
            if row[2] == college_code:
                program_codes_to_remove.add(row[0])

        # Delete related programs
        for row_idx in reversed(range(len(self.data[1]))):  
            if self.data[1][row_idx][0] in program_codes_to_remove:
                del self.data[1][row_idx]

        # Update related students to be 'UNENROLLED'
        for row in self.data[0]:
            if row[5] in program_codes_to_remove:
                row[5] = "UNENROLLED"
        
        self.saveCollegeCSV(self.data[2])
        self.saveProgramCSV(self.data[1])
        self.saveStudentCSV(self.data[0])
        self.displayTable()
        self.deleteCollegeSuccess()

    def collegeChoices(self):
        with open(COLLEGE_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.collegeCodeBox.clear()
            self.collegeCodeBox.addItem("")
            self.collegeCodeBox.addItems(college_codes)

#----------------------------------------------------------------------- EDIT STUDENT ----------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT STUDENT ------------------------------------------------------------------

class StudentDialog(QDialog, Ui_StudentDialog):
    def __init__(self, idNumber, firstName, lastName, yearLevel, gender, programCode):
        super().__init__()
        self.setupUi(self)

        self.programChoices()

        self.updateIDNumber.setText(idNumber)
        self.updateFirstName.setText(firstName)
        self.updateLastName.setText(lastName)
        self.updateYearLevelComboBox.setCurrentText(yearLevel)
        self.updateGender.setText(gender)
        self.updateProgramCodeComboBox.setCurrentText(programCode)
        
        self.updateFirstName.setReadOnly(True)
        self.updateLastName.setReadOnly(True)
        self.updateIDNumber.setReadOnly(True)
        self.updateGender.setReadOnly(True)

        self.pushButton.clicked.connect(self.accept)       
        self.pushButton_2.clicked.connect(self.reject)

    def programChoices(self):
        with open(PROGRAM_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.updateProgramCodeComboBox.clear()
            self.updateProgramCodeComboBox.addItems(program_codes)

    def updatedStudentData(self):
        return [
            self.updateIDNumber.text(),
            self.updateFirstName.text(),
            self.updateLastName.text(),
            self.updateYearLevelComboBox.currentText(),
            self.updateGender.text(),
            self.updateProgramCodeComboBox.currentText(),
        ]
#----------------------------------------------------------------------- EDIT PROGRAM ----------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT PROGRAM ------------------------------------------------------------------
             
class ProgramDialog(QDialog, Ui_ProgramDialog):
    def __init__(self, programCode, programName, collegeCode):
        super().__init__()
        self.setupUi(self)
        self.collegeChoices()

        # Store the original values for comparison
        self.originalProgramCode = programCode
        self.originalProgramName = programName
        self.originalCollegeCode = collegeCode

        # Input current data on to the line edits.
        self.programCodeEdit.setText(programCode)
        self.programNameEdit.setText(programName)
        self.collegeCodeBox.setCurrentText(collegeCode)

        # Validates if input is not empty
        self.confirmButton.clicked.connect(self.validateProgramData)       
        self.cancelButton.clicked.connect(self.reject)

    def collegeChoices(self):
        with open(COLLEGE_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.collegeCodeBox.clear()
            self.collegeCodeBox.addItems(college_codes)
    
    def readProgramCSV(self):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.programData = data

    def updatedProgramData(self):
        self.readProgramCSV()

        newProgramCode = self.programCodeEdit.text().strip().replace(" ", "").upper()
        newProgramName = self.programNameEdit.text().strip().title()
        newCollegeCode = self.collegeCodeBox.currentText()

        # If no changes are made, return the original values
        if (newProgramCode == self.originalProgramCode and
            newProgramName == self.originalProgramName and
            newCollegeCode == self.originalCollegeCode):
            return [self.originalProgramCode, self.originalProgramName, self.originalCollegeCode]

        if not (newProgramCode and newProgramName and newCollegeCode):
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return None
        
        # Validates if program code and name contains digits
        if not all(char.isalpha() or char.isspace() for char in newProgramCode and newProgramName):
            QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
            return None

        for row in self.programData:
            existingProgramCode = row[0].strip().upper()
            existingProgramName = row[1].strip().replace(" ", "").upper()

            if existingProgramCode == self.originalProgramCode:
                continue  

            # Check if the program code already exists
            if existingProgramCode == newProgramCode:
                QMessageBox.warning(self, "Input Error", "The program code you are trying to add already exists.")
                return None

            # Check if the program name already exists
            if existingProgramName == newProgramName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The program name you are trying to enter already exists.")
                return None

        return [newProgramCode, newProgramName, newCollegeCode]
    
    def validateProgramData(self):
        updated_data = self.updatedProgramData()
        if updated_data:
            self.accept()
    
#----------------------------------------------------------------------- EDIT COLLEGE -----------------------------------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT COLLEGE -----------------------------------------------------------------------------------------------

class CollegeDialog(QDialog, Ui_CollegeDialog):
    def __init__(self, collegeCode, collegeName):
        super().__init__()
        self.setupUi(self)

        self.originalCollegeCode = collegeCode
        self.originalCollegeName = collegeName
        
        # Input current data on to the line edits.
        self.collegeCodeEdit.setText(collegeCode)
        self.collegeNameEdit.setText(collegeName)

        self.confirmButton.clicked.connect(self.validateCollegeData)       
        self.cancelButton.clicked.connect(self.reject)

    def readCollegeCSV(self):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            data = [row for row in reader]
            self.collegeData = data

    def updatedCollegeData(self):
        self.readCollegeCSV()

        newCollegeCode = self.collegeCodeEdit.text().strip().replace(" ","").upper()
        newCollegeName = self.collegeNameEdit.text().strip().title()

        # If no changes were made, return the original values
        if (newCollegeCode == self.originalCollegeCode and newCollegeName == self.originalCollegeName):
            return [self.originalCollegeCode, self.originalCollegeName]
        
        if not newCollegeCode or not newCollegeName:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return None
        
        # Validates if the input contains numbers
        if not all(char.isalpha() or char.isspace() for char in newCollegeCode and newCollegeName):
            QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
            return None

        for row in self.collegeData:
            existingCollegeCode = row[0].strip().upper()
            existingCollegeName = row[1].strip().replace(" ","").upper()

            if existingCollegeCode == self.originalCollegeCode:
                continue  

            # Check if the college code already exists
            if existingCollegeCode == newCollegeCode:
                QMessageBox.warning(self, "Input Error", "The college code you are trying to add already exists.")
                return None

            # Check if the college name already exists
            if existingCollegeName == newCollegeName.replace(" ", "").upper():
                QMessageBox.warning(self, "Input Error", "The college name you are trying to enter already exists.")
                return None

        return [newCollegeCode, newCollegeName]
    
    def validateCollegeData(self):
        updated_data = self.updatedCollegeData()
        if updated_data:
            self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainClass()
    main.show()
    app.exec_()