import tkinter as tk
import tkinter.ttk as ttk
import math
import os
import csv
import ast # For interpreting lists as lists, not strings when reading from a CSV

# List to hold every single student
allStudents = []
# List to hold every single assignment TITLE, not object
allAssignments = []

# Weight counter to make sure total weight doesn't exceed 100%
weightTotal = 0

### Settings defined by user
regularGradeTypes = []
regularGradeWeights = []
examTypes = []
examWeights = []

# To keep track of the current assignment type
currAssignmentType = None

# For three different types of curves
curveOptions = ["Default", "Square Root", "Cube Root"]
# For four different types of quarters
quarterOptions = ["1", "2", "3", "4"] # Strings because they hold no numerical value

# Variable to hold the file name and path (everything will be added to the user's downloads folder)
filename = "reportCardGenData.csv"
filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)

# Create a student class
class Student:
    def __init__(self, name):
        self.name = name
        self.comments = '' # Comments are not added until report card is generated
        self.allGrades = [] # List to hold all of the student's grades.
        self.missing = [] # List to hold all of student's missing grades
        
        if name != "ALL STUDENTS":
            allStudents.append(self) # Add each new student to the allStudents list unless it's the ALL STUDENTS option
        
    # Function which returns a specific missing assignment from a student's list
    def findAssignment(self, assigFT, missing):
        if missing: # If missing is flagged check in the missing list and return a missing assignment
            for item in self.missing:
                if item.fullTitle == assigFT: # Assignment full title
                    return item
        else: # If missing is not flagged check in the allGrades list and return a normal assignment
            for item in self.allGrades:
                if item.fullTitle == assigFT:
                    return item # Both calls return an assignment object rather than the title as a string 
        return None # Return none if not found
    
    # Function to use with ALL STUDENTS ONLY!!! which will look for students which already have a certain assignment (by fullTitle)
    def findDuplicates(self, assigFT):
        studentsWithDupe = ""
        for stu in allStudents:
            if stu.findAssignment(assigFT, False) != None: # If this student has this assignment already
                studentsWithDupe += stu.name
                studentsWithDupe += ", "
                
        if studentsWithDupe != "": # Check if the string is still empty or not
            studentsWithDupe += " are missing "+assigFT+"."
        return studentsWithDupe # If none are found this will return ""
    
    # Function to call to check if object exists
    def nothing(self):
        return
        
    # Converts student's information into a writable/readable format (lists)
    def export(self): 
        formatted = [[self.name, self.comments]]
        if self.allGrades != []: # Check if student has no grades
            for grade in self.allGrades:
                # Using the export method per grade ensured that quarter/curve are accounted for 
                formatted.append(grade.export())
        return formatted # Returns a correctly formatted list for writing
        
# Create a grades base class
class Grade:
    # Given as title, fullTitle, weight, max, received, quarter/curve
    def __init__(self, title, fullTitle, weight, maxScore, receivedScore):
        self.title = title
        self.fullTitle = fullTitle
        self.isMissing = False # Bool to determine if assignment is missing, all assignment by default are not missing
        
        # Convert weight to a decimal if needed
        if not weight < 1:
            self.weight = float(weight) / 100
        else:
            self.weight = float(weight) # Set to integer since all entry boxes return strings
            
        self.max = float(maxScore)
        
        if receivedScore == "None": # Check if there is a score that is not zero
            self.received = 0 # Keep these to be numbers anyways because they will be calculated as zeroes if missing
            self.score = 0
        else:
            self.received = float(receivedScore)
            self.score = self.received/self.max # calculate student's actual score based on what they got over total points
            self.score = round(self.score, 2) # Round score to 2 decimal places
        
    # The export method will format the Grade's information into a CSV-friendly list.
    def export(self):
        pass
        
# Create a regularGrade class that extends the Grade base class, this will also include a quarter 
class RegularGrade(Grade):
    def __init__(self, title, fullTitle, weight, maxScore, receivedScore, quarter):
        super().__init__(title, fullTitle, weight, maxScore, receivedScore) # This adds a field list even though 'fields' is not an arg
        self.quarter = quarter
        
    # Inherited function to format all properties correctly into a list
    def export(self):
        regList = [self.title, self.fullTitle, self.weight, self.max, self.isMissing, self.received, 
                   self.score, self.quarter]
        return regList
            
# Create an exam class that extends the Grade base class, this will also include a curve
class Exam(Grade):
    def __init__(self, title, fullTitle, weight, maxScore, receivedScore, curve):
        super().__init__(title, fullTitle, weight, maxScore, receivedScore)
        self.curve = curve # Later the curve will be calculated with a method
        
    # Inherited function to format all properties correctly into a list
    def export(self):
        examList = [self.title, self.fullTitle, self.weight, self.max, self.isMissing, self.received, self.score,
                    self.curve]
        return examList
    
    # Function to calculate the curve depending on which curve is used
    def calculateCurve(self): # To get to this point there would need to be at least one student and at least one exam
        curve = self.curve
        
        if self != None:
            if curve == "Default":
                bestScore = 0 
                for stu in allStudents:
                    for grade in stu.allGrades:
                        if grade.fullTitle == self.fullTitle:
                            if float(grade.received) > float(bestScore):
                                bestScore = float(grade.received)
                curvedScore = float(self.received) / bestScore
                curvedScore = round(curvedScore, 2)
            elif curve == "Square Root":
                curvedScore = math.sqrt(self.score) # Use math library to square root the score
                curvedScore = round(curvedScore, 2)
            elif curve == "Cube Root":
                curvedScore = pow(self.score, 1/3) # Use fractional exponent to cube root the score
                curvedScore = round(curvedScore, 2)

            return float(curvedScore)
        else:
            return None
        
def handleConfigure(event):
    # Update the scroll bar's position when the canvas changes size/layout/etc
    appCanvas.configure(scrollregion = appCanvas.bbox("all"))
    
############################################## BUILDING THE GUI #######################################################
# Create a Tkinter window for the user interface:
app = tk.Tk()
app.geometry('1500x750') #set size of window
app.title('Report Card Generator') #sets title of window
app.configure(bg='lightblue') #set background color of GUI

# CANVAS AND APPFRAME WHICH HOLDS EVERYTHING SO YOU CAN SCROLL
appCanvas = tk.Canvas(app, width = 1500, height = 770, bg = "lightblue") # Create canvas object to make a scrollable space 
appScrollVert = tk.Scrollbar(app, command = appCanvas.yview) 
appScrollHorizontal = tk.Scrollbar(app, command = appCanvas.xview, orient = tk.HORIZONTAL)
appScrollVert.pack(side = "right", fill = "y")
appScrollHorizontal.pack(side = "bottom", fill = tk.X)
appCanvas.pack(side = "top", fill = "both", expand = True)
# Create vertical scrollbar

# Set canvas to be scrollable in the both directions
appCanvas.configure(yscrollcommand = appScrollVert.set) 
appCanvas.configure(xscrollcommand = appScrollHorizontal.set)
appCanvas.bind("<Configure>", handleConfigure) # Canvas calls handleConfigure() to handle events where the window is resized
appFrame = tk.Frame(appCanvas, bg = "lightblue") # Frame holds all the widgets inside rather than the 'app'
appCanvas.create_window((0, 0), window = appFrame, anchor = "nw")

# To keep track of the selected option in dropdown menus
### These must be created AFTER the main root window is defined
selectedType = tk.StringVar()
selectedCurve = tk.StringVar()
selectedCurve.set("Default")
selectedQuarter = tk.StringVar()

# Keep track of currently selected student
selectedStudent = tk.StringVar()
selectedStudent.set("None")

# Keep track of currently selected assignment to edit
selectedAssignment = tk.StringVar()
selectedAssignment.set("None")

# Keep track of the 'missing assignment' status in the checkbutton
missingChecked = tk.IntVar() # NOTE that this and isMissing are different

# Student ALL STUDENTS serves as an option to add an assignment to every student user has created
ALLSTUDENTS = Student("ALL STUDENTS")

######---------------------------Frames---------------------------------
# Frame to hold the list of created assignments
assignmentScrollFrame = tk.Frame(master = appFrame, width = 600, height = 350, bd = 5)
assignmentScrollFrame.pack(side = 'left', padx = (50, 0), pady = (10, 20))

# Frame to hold the list of student names
studentScrollFrame = tk.Frame(master = appFrame, width = 600, height = 150, bd = 5)
studentScrollFrame.pack(side = 'left', padx = 20, pady = (10, 20)) # Use a tuple to put padding on the left side only

# Padding with tuple:
# (left, right) or (top, bottom)

# Frame to hold both the Grading System and Student data interfaces so that they can stack on top of each other
holdBothFrames = tk.Frame(master = appFrame, width = 500, height = 500, bd = 5) # make it blend in w/bg
holdBothFrames.pack(side = 'right', padx = (0, 20), pady = 10)

# Frame to hold the 'Grading System' interface
gradingSysFrame = tk.Frame(master = holdBothFrames, width = 500, height = 200, bd = 5)
gradingSysFrame.pack(pady = 10) 

gradingSysEntries = tk.Frame(master = gradingSysFrame, width = 500, height = 200, bd = 5)
gradingSysEntries.grid(row = 1, column = 0)

gradingSysTop = tk.Frame(gradingSysFrame, width = 1500, height = 100, bd = 5)
gradingSysTop.grid(row = 0, column = 0, pady = (0, 10))


# Frame to hold the interface for editing student data
addAssignmentFrame = tk.Frame(master = holdBothFrames, width = 1500, height = 200, bd = 5)
addAssignmentFrame.pack(pady = 10)
#####-------------------------------------------------------------------

#"Create your grading system" goes in GRADINGSYSTOP
createSysLabel = tk.Label(master = gradingSysTop, text='Create Your Grading System', font = ('Arial bold', 14))
createSysLabel.grid(row = 0, column = 0)
#Information label to show user what to do
explainSysLabel = tk.Label(gradingSysTop, text = "Add what types of assignments\n you use when grading (such as a homework, quiz, or midterm).\n Then, you can Update your system \nand create new assignments.")
explainSysLabel.grid(row = 1, column = 0)
# Label to show the current weight total
weightTotalLabel = tk.Label(master = gradingSysTop, text = "Total weight: "+str(weightTotal), font = "Arial 10", fg = "blue")
weightTotalLabel.grid(row = 2, column = 0)

# Label above assignment creation section, --> using getter for the student StringVar()
addAssignmentLabel = tk.Label(master = addAssignmentFrame, text = 'Add an Assignment to '+selectedStudent.get(), font = ('Arial bold', 14))
addAssignmentLabel.grid(row = 0, column = 0, pady = (0, 5))

# Instructions on how to add an assignment to a student
addingInstructions = tk.Label(addAssignmentFrame, fg = "blue", text = "Please select a student from your list,\nand hit the 'Add Assignment To Student'\nbutton to edit them here!")
addingInstructions.grid(row = 1, column = 0)

assignmentTypeLabel = tk.Label(addAssignmentFrame, text = "Assignment Type: ")
assignmentTypeLabel.grid(row = 2, column = 0, pady = 2)

# Drop down menu to hold all options of assignment/exam types      Options: both lists?
assignmentDropdown = tk.OptionMenu(addAssignmentFrame, selectedType, regularGradeTypes + examTypes)
assignmentDropdown.grid(row = 2, column = 1, pady = 2)

# Labels and entries for assignment properties
assignmentNameLabel = tk.Label(addAssignmentFrame, text = "Full name: ")
assignmentNameLabel.grid(row = 3, column = 0)
assignmentNameEntry = tk.Entry(addAssignmentFrame)
assignmentNameEntry.grid(row = 3, column = 1)
assignmentMaxLabel = tk.Label(addAssignmentFrame, text = "Total points: ")
assignmentMaxLabel.grid(row = 4, column = 0)
assignmentMaxEntry = tk.Entry(addAssignmentFrame)
assignmentMaxEntry.grid(row = 4, column = 1)
assignmentScoreLabel = tk.Label(addAssignmentFrame, text = "Score "+selectedStudent.get()+" received: ")
assignmentScoreLabel.grid(row = 5, column = 0)
assignmentScoreEntry = tk.Entry(addAssignmentFrame)
assignmentScoreEntry.grid(row = 5, column = 1)
#Checkbutton if student is missing the assignment or not
assignmentMissingLabel = tk.Label(addAssignmentFrame, text = "Is "+selectedStudent.get()+" missing this assignment?")
assignmentMissingLabel.grid(row = 6, column = 0)
missingBox = tk.Checkbutton(addAssignmentFrame, variable = missingChecked, height = 2, width = 10)
missingBox.grid(row = 6, column = 1)

# FINAL BUTTON for adding an assignment
addAssignmentButton = tk.Button(addAssignmentFrame, text = "Add New\nAssignment", command = lambda: addAssignment())
addAssignmentButton.grid(row = 8, column = 0)

# Button for saving changes made to an assignment through the edit assignments dropdown
saveChangesButton = tk.Button(addAssignmentFrame, text = "Save Changes", command = lambda: saveChanges())
saveChangesButton.grid(row = 8, column = 1)

# NOTE: Quarter and curve elements will be added per assignment/exam, not when creating the system

# "Category name: " label and entry
categoryNameLabel = tk.Label(gradingSysEntries, text = "Category or Exam name: ")
categoryNameLabel.pack(pady = (0, 1))
categoryNameEntry = tk.Entry(gradingSysEntries)
categoryNameEntry.pack(pady = 1)
# "Weight (in percent): " label and entry
categoryWeightLabel = tk.Label(gradingSysEntries, text = "Weight (in percent): ")
categoryWeightLabel.pack(pady = 1)
categoryWeightEntry = tk.Entry(gradingSysEntries)
categoryWeightEntry.pack(pady = 1)

# Button to create an assignment
addCategoryButton = tk.Button(gradingSysEntries, text = "Add an Assignment Type", command = lambda: addCategory(False))
addCategoryButton.pack(pady = (5, 0), padx = (0, 5), side = "left")

# Button to create an exam
addExamButton = tk.Button(gradingSysEntries, text = "Add an Exam", command = lambda:addCategory(True))
addExamButton.pack(pady = (5, 0), padx = (0, 5), side = "left")

# Button to update the current grading system (will UPDATE DROPDOWN MENU)
updateSystemButton = tk.Button(gradingSysEntries, text = "Update Grading System", command = lambda: updateSystem())
updateSystemButton.pack(pady = (5, 0), side = "left")

# Title above student names listbox
studentScrollLabel = tk.Label(master = studentScrollFrame, text='Your Students', font=('Arial bold', 14))
studentScrollLabel.grid(row = 0, column = 0)

# Label "Student's name: "
addNameLabel = tk.Label(master = studentScrollFrame, text = "Student's name: ", font = ('Arial', 12))
addNameLabel.grid(row = 1, column = 0)
# Entry box for inputting a student's name
addStudentNameEntry = tk.Entry(master = studentScrollFrame)
addStudentNameEntry.grid(row = 2, column = 0)
# Button for creating a student --> ERROR if user attempts to add student with no name
# Calling the button passes whatever is in the student name entry box to the function.
# Lambda is needed to prevent the button from immediately calling itself on startup.
addStudentButton = tk.Button(studentScrollFrame, text = "Create student", command = lambda:addStudent(addStudentNameEntry.get()))
addStudentButton.grid(row = 3, column = 0)

# Button to view what assignments student currently has in a dropdown menu
editAssignmentsButton = tk.Button(studentScrollFrame, text = "Edit Assignments   --->", command = lambda: viewAssignments(studentList.get(tk.ACTIVE)))
editAssignmentsButton.grid(row = 5, column = 0)

# DROPDOWN of student's CURRENT ASSIGNMENTS
editDropdown = tk.OptionMenu(studentScrollFrame, selectedAssignment, [])
editDropdown.grid(row = 5, column = 1)

# Title above assignments listbox
assignmentScrollLabel = tk.Label(master = assignmentScrollFrame, text = 'Your Assignments', font = ('Arial bold', 14))
assignmentScrollLabel.pack(side = 'top')

# Button to show which students are missing which assignments
showAssigButton = tk.Button(assignmentScrollFrame, text = "Show Students Who\nAre Missing this \nAssignment", command = lambda: showMissingStudents(assigList.get(tk.ACTIVE)))
showAssigButton.pack(side = "top")

deleteAssigButton = tk.Button(assignmentScrollFrame, text = "Delete Selected Assignment", command = lambda: deleteAssignment(assigList.get(tk.ACTIVE)))
deleteAssigButton.pack(side = "top")

# Create a scrollbar for the student names
sBar = tk.Scrollbar(master = studentScrollFrame, orient = 'vertical')
sBar.grid(row = 6, column = 1, sticky = tk.N+tk.S)

# Create a scrollbar for the assignments
aBar = tk.Scrollbar(master = assignmentScrollFrame, orient = 'vertical')
aBar.pack(side = 'right', fill = 'y')

# Insert a listbox into the student names scroll bar
studentList = tk.Listbox(
    studentScrollFrame,
    yscrollcommand = sBar.set, # this sets the box to be scrollable
    height=10,
    width=30,
    highlightcolor='blue',
    font=('Arial',15)
) 
studentList.grid(row = 6, column = 0, sticky = tk.N+tk.S) # fill = both
sBar.config(command=studentList.yview) # this is important, keeps bar moving
# IMMEDIATELY ADD THE ALL STUDENTS OPTION!!
studentList.insert("end", ALLSTUDENTS.name)

app.rowconfigure(0, weight = 1) # Configures the whole screen to be scrollable
app.columnconfigure(0, weight = 1)

# Button for showing student's missing assignments
showMissingButton = tk.Button(studentScrollFrame, text = "Show Student's \nMissing Assignments", command = lambda: showMissingAssignments(studentList.get(tk.ACTIVE)))
showMissingButton.grid(row = 3, column = 1)

# Button for deleting a student
deleteStudentButton = tk.Button(studentScrollFrame, text = "Delete Selected Student", command = lambda: deleteStudent(studentList.get(tk.ACTIVE)))
deleteStudentButton.grid(row = 4, column = 0)

# Button for displaying student's info in a new window
showInfoButton = tk.Button(studentScrollFrame, text = "Display Student's Information", command = lambda: returnInfo(studentList.get(tk.ACTIVE)))
showInfoButton.grid(row = 4, column = 1)

# BUTTON FOR ADDING ASSIGNMENT TO STUDENT!!!!!!!!! --> pass the currently selected student as a parameter
addAssigToStuButton = tk.Button(studentScrollFrame, text = "Add Assignment\nTo Student", command = lambda: addToStudent(studentList.get(tk.ACTIVE)))
addAssigToStuButton.grid(row = 2, column = 1)

# Entry and button for client to add personal comments to student
addCommentsEntry = tk.Entry(studentScrollFrame)
addCommentsEntry.grid(row = 8, column = 0)
addCommentsButton = tk.Button(studentScrollFrame, text = "<-- Add comments to\nselected student", command = lambda: addComments(studentList.get(tk.ACTIVE)))
addCommentsButton.grid(row = 8, column = 1)

# BUTTON FOR SAVING ALL DATA!!!
writeAllButton = tk.Button(studentScrollFrame, text = "SAVE ALL DATA", command = lambda: writeData())
writeAllButton.grid(row = 9, column = 0)
# BUTTON FOR LOADING ALL DATA!!!
readAllButton = tk.Button(studentScrollFrame, text = "LOAD ALL DATA", command = lambda: readData())
readAllButton.grid(row = 9, column = 1)

# GENERATE REPORT CARD BUTTON
generateButton = tk.Button(studentScrollFrame, text = "Generate Selected\nStudent's Report Card!", command = lambda: generateReportCard(studentList.get(tk.ACTIVE)))
generateButton.grid(row = 10, column = 0)

assigList = tk.Listbox(
    assignmentScrollFrame,
    yscrollcommand = aBar.set,
    height = 15,
    width = 30,
    highlightcolor = 'blue',
    font = ('Arial', 15)
)
assigList.pack(side = 'left', fill = 'both')
aBar.config(command = assigList.yview)

#create label for a possible ERROR MESSAGE
errorMsg = tk.Label(app, text = '', font = "Arial 15", pady = 10, fg = 'darkred', bg = 'lightblue', wraplength = 1000)
errorMsg.place(relx = 0.5, rely = 0.95, anchor = 'se')

# Create a new label to display information of missing assignments or students. Set a line limit of 120 characters
missingLabel = tk.Label(appCanvas, text = "", font = "Arial 15", fg = "blue", bg = "lightblue", wraplength = 1000)
missingLabel.pack(pady = 5)

#-----------------------------------------------------------BUTTON FUNCTIONS--------------------------------------
# Creates a student object and adds the student's name to the listbox
def addStudent(name):
    if name == '':
        errorMsg.config(text = "Please enter student's name.")
    else:
        # First check for duplicates of students
        for stu in allStudents:
            if stu.name == name:
                errorMsg.config(text = "Students cannot share the exact same name.")
                return
            elif stu.name == "ALL STUDENTS":
                errorMsg.config(text = "You cannot name a student ALL STUDENTS.")
                return
        
        # Add a new student object if it passes the error checks
        newStudent = Student(name) # name does not have to be a string to work in the listbox
        studentList.insert('end', name)
        addStudentNameEntry.delete(0, "end") # Clear entry box
        
        
def deleteStudent(name):
    if name == "":
        errorMsg.config(text = "Try adding a student before you delete one!")
    elif name == "ALL STUDENTS" and allStudents == []: # Check if user has attempted to delete all students without any students added
        errorMsg.config(text = "Try adding some students before deleting them all!")
    elif name == "ALL STUDENTS" and allStudents != []: # If we are deleting all the students
        missingLabel.config(text = "Deleting all your students..")
        allStudents.clear() # Clear the whole list
        studentList.delete(1, "end") # Clear listbox
        #missingLabel.config(text = "")
        selectedStudent.set("None")
        updateLabels()
    else: # If we are deleting a single student
        missingLabel.config(text = "deleted "+name)
        for stu in allStudents: # Delete by comparing objects to name
            if stu.name == name:
                allStudents.remove(stu)
        studentList.delete(studentList.curselection()) # Remove item from selected index
        selectedStudent.set("None")
        updateLabels()
        
# Function to return all of a student's information, including grades, in a separate window
def returnInfo(name):
    # Function to handle scrolling within the infoWin Toplevel -- this must be inside returnInfo()
    def infoHandleConfigure(event):
        infoCanvas.configure(scrollregion = infoCanvas.bbox("all"))
    
    student = findStudent(name) # Use function from above to return the student object
    
    try: student.nothing()
    except:
        errorMsg.config(text = "Please select (or add) a student before\ntrying to view their information!")
        return

    header = f"{student.name}" # Text to be shown on a bigger label -- the only thing that does not need \n
    if student.comments == "": # Check for empty comments:
        toReturn = f"{student.name} has no comments."
    else:
        toReturn = f"Comments: {student.comments}"

    # Save indexes of current assignment/exams
    r = 1
    e = 1
    for grade in student.allGrades:
        if isinstance(grade, RegularGrade): # If a regular assignment
            toReturn += f"\nRegular Grade {r}: {grade.title}"
            r += 1
        else: # If an exam
            toReturn += f"\nExam {e}: {grade.title}"
            e += 1
        toReturn += f"\n\t{grade.fullTitle}\n\tWeight: {grade.weight}\n\tMaximum points: {grade.max}"
        # Check if assignment is missing
        if grade.isMissing:
            toReturn += f"\n\t{student.name} is missing this assignment."
        else:
            toReturn += f"\n\tScore {student.name} received: {grade.received}\n\tCalculated score: {grade.score}"
        # Distinguish again between regular / exam for quarter / curve
        if isinstance(grade, RegularGrade):
            toReturn += f"\n\tQuarter: {grade.quarter}"
        elif isinstance(grade, Exam) and not grade.isMissing: # Also check if missing before trying to calculate curve
            if checkForMultiple(grade.fullTitle) == None: # If there are one or less students with this exam
                toReturn += f"\n\t Curve: {grade.curve}"
                toReturn += f"\nThere are not enough students with this\nexam to calculate a default curve.\nPlease account for this before trying to\ngenerate a report card for this student."
            else:
                toReturn += f"\n\tCurve: {grade.curve}\n\tScore calculated with curve: {grade.calculateCurve()}"
        else: # If the exam is missing, don't calculate anything
            toReturn += f"\n\tCurve: {grade.curve}"
        toReturn += f"\n" # Add an extra space between grades

    # Now put this information onto some labels in a new window
    infoWin = tk.Toplevel(app, bg = "lightblue")
    infoWin.title(f"{name}")
    infoWin.geometry("500x500")
    # Create a canvas and a scrollbar, set the bar to scroll the canvas
    infoCanvas = tk.Canvas(infoWin, borderwidth = 5, bg = "lightblue")
    infoScroll = tk.Scrollbar(infoWin, orient = "vertical", command = infoCanvas.yview)
    infoCanvas.configure(yscrollcommand = infoScroll.set)
    infoCanvas.pack(side = "left", fill = "both", expand = True)
    infoScroll.pack(side = "right", fill = "y")
    # Create a frame to contain all other widgets (the labels below) and bind it to the canvas so it can be scrolled
    infoFrame = tk.Frame(infoCanvas, bg = "lightblue")
    infoFrame.bind("<Configure>", infoHandleConfigure)
    infoCanvas.create_window((0, 0), window = infoFrame, anchor = "nw") # Expand canvas to fit the window
    
    headerLabel = tk.Label(infoFrame, text = header, font = "Arial 15 bold", bg = "lightblue")
    headerLabel.pack(side = "top")
    infoLabel = tk.Label(infoFrame, text = toReturn, font = "Arial 12", bg = "lightblue")
    infoLabel.pack(side = "top", pady = (0, 50))

    infoWin.mainloop()
        
def deleteAssignment(fullTitle):
    if fullTitle == "":
        errorMsg.config(text = "Try adding an assignment before you delete one!")
    else:
        allAssignments.remove(fullTitle) # Remove from general list -- this list contains titles (strings)
        assigList.delete(assigList.curselection()) # Remove assignment from selected index
        for stu in allStudents: # Check in student's allGrades to remove assignment
            for grade in stu.allGrades:
                if grade.fullTitle == fullTitle:
                    stu.allGrades.remove(grade) # Remove grade here not the title
            for grade in stu.missing: # Check in student's missing to remove assignment
                if grade.fullTitle == fullTitle:
                    stu.missing.remove(grade)
                    
        missingLabel.config(text = "Deleted "+fullTitle+" from your assignments.")
        
# Called when "Edit assignments -->" is pressed, to generate the options of assignments for editing
def viewAssignments(studentName):
    student = findStudent(studentName)
            
    try: student.nothing()
    except: 
        errorMsg.config(text = "Cannot edit the assignments of ALL STUDENTS.")
        return
    
    editDropdown["menu"].delete(0, editDropdown["menu"].index("end")) # Clear dropdown menu
    # Check if user has attempted to edit the grades of ALL STUDENTS
    if len(student.allGrades) == 0: # Check first if student has no grades
        errorMsg.config(text = "Please add assignments to your student first.")
    else:
        for grade in student.allGrades: # Pass fullTitle to be displayed, but pass whole object to selectToEdit()
            editDropdown["menu"].add_command(label = grade.fullTitle, command = lambda value = grade: selectToEdit(value, student))
            
def findStudent(stuName):
    for stu in allStudents:
        if stu.name == stuName:
            return stu
            
# Function to check for how many students actually have an assignment
def checkForMultiple(assigFT):
    totalAssigs = 0
    for stu in allStudents:
        for grade in stu.allGrades:
            if isinstance(grade, Exam):
                if grade.curve == "Default" and grade.fullTitle == assigFT:
                    totalAssigs += 1
                
    if totalAssigs == 1: # If there's only one student with this assignment (Default curve would not work with too few students)
        return None
    else:
        return totalAssigs

# Shows all the missing assignments PER student after a student is selected from the list
def showMissingAssignments(studentName):
    student = findStudent(studentName) # Use function to return student object
    errorMsg.config(text = "") # Clear error message so it doesn't get in the way
    
    try: student.nothing()
    except: 
        errorMsg.config(text = "Cannot show the missing assignments of ALL STUDENTS.")
        return
    
    if student.missing == []:
        missingLabel.config(text = student.name+" has no missing assignments.")
    else:
        # Display student's missing assignments at the bottom of the screen
        display = student.name+" is missing: "
        for assig in student.missing:
            if assig == student.missing[-1] and len(student.missing) != 1: # if we've reached the last item
                display += " and "
                display += assig.fullTitle
                display += "."
            elif len(student.missing) == 1:
                display += assig.fullTitle
                display += "."
            else:
                display += assig.fullTitle # Use full title, not referencing the object (error) or the basic title
                display += ", "
        
        missingLabel.config(text = display)

# Show missing students per assignment
def showMissingStudents(assignment):
    display = "Students missing "+assignment+" are: "
    for stu in allStudents:
        if stu.findAssignment(assignment, True) != None:
            display += stu.name
            display += ", "
    if display == "Students missing "+assignment+" are: ": # if display is not changed i.e. no students missing
        display = "There are no students missing this assignment."
            
    missingLabel.config(text = display)

# To quickly update all labels which include the student's name
def updateLabels():
    addAssignmentLabel.config(text = "Add an Assignment to "+selectedStudent.get()) 
    assignmentScoreLabel.config(text = "Score "+selectedStudent.get()+" received: ")
    assignmentMissingLabel.config(text = "Is "+selectedStudent.get()+" missing this assignment?")

currRow = 3 # counter for the row to create more rows of assignment type + button
        
# Takes info from categoryName, categoryWeight, categoryQuarter entry boxes to create a new Regular Grade
# isExam is passed through parameters to differentiate between regular grades (test, quiz, etc.) and exam grades
def addCategory(isExam):
    global regularGradeTypes
    global examTypes
    global weightTotal
    global currRow
    
    numWeight = None
    cName = categoryNameEntry.get()
    
    try:
        numWeight = float(categoryWeightEntry.get()) # convert entry box to a float -- we want decimals
    except:
        errorMsg.config(text = "Please enter a number as a weight.")
        return
    
    if cName == "": # Check for no entry in name box
        errorMsg.config(text = "Please enter a name for your assignment type.")
    elif cName in regularGradeTypes or cName in examTypes: # Check for duplicate category name
        errorMsg.config(text = "You already have a category called "+cName+"!")
    elif categoryWeightEntry.get() == None: # Check for no entry in weight box
        errorMsg.config(text = "Please enter a weight for your assignment type.\nWeights should add up to 100%,\nincluding exams.")
    elif numWeight > 100: # Check for one weight over 100
        errorMsg.config(text = "Your weight of "+categoryWeightEntry.get()+"\nexceeds 100%, please adjust it.")
        return
    elif weightTotal + numWeight > 100: # check for total weight exceeding 100
        errorMsg.config(text = "Your weight of "+categoryWeightEntry.get()+" makes your\nweight total exceed 100%, please adjust it.")
        return
    else:
        if isExam: # For Exam types
            examTypes.append(cName)
            examWeights.append(numWeight)
            
        else:
            regularGradeTypes.append(cName)
            regularGradeWeights.append(numWeight) # Add grade and weight to a list
        
        # Add a label and button to delete the assignment type if necessary
        newGradeType = tk.Label(gradingSysTop, text = cName+" : "+str(numWeight), font = "Arial 15", bg = "white")
        newGradeType.grid(row = currRow, column = 0)
        newGradeDel = tk.Button(gradingSysTop, text = "Delete", bg = "white", command = lambda: delCategory(cName, isExam)) # Pass again
        newGradeDel.grid(row = currRow, column = 1)
        
        weightTotal += numWeight # increment weight counter
        weightTotalLabel.config(text = "Total weight: "+str(weightTotal)) # Update GUI to show new weight total
        
        currRow += 1

# Function called whenever a 'Delete' button is pressed to remove that category
def delCategory(name, isExam):
    global weightTotal
    
    if isExam:
        for eTyp in examTypes:
            if name == eTyp:
                i = examTypes.index(eTyp)
                currType = examTypes[i]
                currWeight = examWeights[i]
                currText = currType+" : "+str(currWeight)
                # Remove name and weight from exam lists
                examTypes.pop(i)
                examWeights.pop(i)
    elif not isExam:
        for typ in regularGradeTypes:
            if name == typ:
                i = regularGradeTypes.index(typ)
                currType = regularGradeTypes[i] # Save name, weight in a variable for later reference
                currWeight = regularGradeWeights[i]
                currText = currType+" : "+str(currWeight) # have to check for the full text
                # Remove the grade type name and weight from their respective lists
                regularGradeTypes.pop(i)
                regularGradeWeights.pop(i)
        
                
    # Reset the weight counter
    weightTotal -= currWeight # currWeight should already be an int
    weightTotalLabel.config(text = "Total weight: "+str(weightTotal))

    # Remove name and delete button from the screen
    for widget in gradingSysTop.winfo_children():
        if isinstance(widget, tk.Label) and widget.cget("text") == currText: # If we found the label with same name
            cRow = widget.grid_info()["row"] #Save row
            widget.destroy()

        # now check for buttons in the same row (cRow) as the deleted label
        if isinstance(widget, tk.Button):
            try: # Use try/except as some labels will not match, so we can't delete their buttons with cRow
                if widget.grid_info()["row"] == cRow and widget.grid_info()["column"] == 1:
                    widget.destroy()
            except:
                pass
            
# Updates grading system, saving it to a few lists, after it has met the requirements of 100% weight 
def updateSystem():
    global regularGradeTypes
    global examTypes
    global weightTotal
    
    if len(regularGradeTypes) == 0 and len(examTypes) == 0: # Check if there are no categories
        errorMsg.config(text = "Please add some assignment types and / or\nexams before creating assignments!")
    elif weightTotal != 100: # Check if categories' weights do not add up
        errorMsg.config(text = "Your categories' weights (in percents)\ndo not add up to 100%.")
    else:
        # Clear menu from start to end -- current items inside the menu
        assigEnd = assignmentDropdown["menu"].index("end")
        if assigEnd - 0 == 0:
            pass
        else:
            assignmentDropdown["menu"].delete(0, assigEnd)
            
        # Now add new items from regularGradeTypes and examTypes
        merged = regularGradeTypes + examTypes
        for typ in merged:
            # Pass the type as a command through the menu (I assume each option is technically a button)
            assignmentDropdown["menu"].add_command(label = typ, command = lambda value = typ: selectType(value))

# Select the type out of user-created assignment types, add the respective quarter/curve dropdown menu for customization
def selectType(Type): # note the uppercase T
    global examTypes
    global curveOptions
    global selectedType
    currAssignmentType = Type
    
    # Display selected name in the dropdown menu
    selectedType.set(Type) 
    
    # First clear whatever was in that row 7
    for widget in addAssignmentFrame.winfo_children():
        if widget.grid_info()["row"] == 7:
            widget.destroy()
    
    # Change GUI of assignment creator based on whether or not an exam is selected
    if Type in examTypes:
        curveLabel = tk.Label(addAssignmentFrame, text = "Curve: ")
        curveLabel.grid(row = 7, column = 0)
        curveDropdown = tk.OptionMenu(addAssignmentFrame, selectedCurve, curveOptions)
        # Add each curve option manually with a loop, since the Tkinter dropdown menu requires a command
        curveDropdown["menu"].delete(0, curveDropdown["menu"].index("end")) # Clear dropdown then add values
        for item in curveOptions:
            curveDropdown["menu"].add_command(label = item, command = lambda value = item: selectCurve(value))#pass selected value
        curveDropdown.grid(row = 7, column = 1)
    else:
        quarterLabel = tk.Label(addAssignmentFrame, text = "Quarter: ")
        quarterLabel.grid(row = 7, column = 0)
        
        # Add a dropdown menu to select the quarter as well
        quarterDropdown = tk.OptionMenu(addAssignmentFrame, selectedQuarter, quarterOptions)
        quarterDropdown["menu"].delete(0, quarterDropdown["menu"].index("end")) # Clear dropdown then add values in a loop
        for item in quarterOptions:
            quarterDropdown["menu"].add_command(label = item, command = lambda value=item: selectQuarter(value))
        quarterDropdown.grid(row = 7, column = 1)

# Change the selectedCurve StringVar()
def selectCurve(curve):
    global selectedCurve
    selectedCurve.set(curve)# Change text of the dropdown menu to display what is currently selected

# Change the selectedQuarter StringVar()
def selectQuarter(quarter): 
    global selectedQuarter
    selectedQuarter.set(quarter)
    
# Handles pressing of a menu item from the edit assignments dropdown menu
def selectToEdit(assignment, student): # Change the selectedAssignment StringVar()
    global selectedAssignment
    selectedAssignment.set(assignment.fullTitle) 
    selectedStudent.set(student.name)
    
    # Update label texts
    updateLabels()
    
    assignmentNameEntry.delete(0, "end")
    assignmentNameEntry.insert(0, assignment.fullTitle) # Clear and populate entry boxes with correct text
    assignmentMaxEntry.delete(0, "end")
    assignmentMaxEntry.insert(0, assignment.max)
    
    # Set the assignment type so that the curve / quarter dropdown menus are added accordingly
    selectType(assignment.title)
    
    if isinstance(assignment, RegularGrade):
        selectQuarter(assignment.quarter) # Set respective quarter or curve depending on the class
    elif isinstance(assignment, Exam):
        selectCurve(assignment.curve)
    
    if not assignment.isMissing: # if student was not missing the assignment
        assignmentScoreEntry.delete(0, "end") # Reset user's score entry and replace with score received, not calculated
        assignmentScoreEntry.insert(0, str(assignment.received))
        missingBox.deselect()
    elif assignment.isMissing: # if student was missing the assignment
        assignmentScoreEntry.delete(0, "end")
        missingBox.select()
        
    selectedType.set(assignment.title) # set the type to object's title

# Takes student chosen from the student listbox and adds them to the editor (if an assignment is created it will be added
# to their object)
def addToStudent(student):
    # Display student's name on respective labels
    if student == "": # student here references a string, not an object
        errorMsg.config(text = "Student to add has no name.")
    else:
        selectedStudent.set(student)
        updateLabels()
        
        # Clear entry boxes !
        selectedType.set("")
        assignmentNameEntry.delete(0, "end")
        assignmentMaxEntry.delete(0, "end")
        assignmentScoreEntry.delete(0, "end")
        missingBox.deselect()
        for widget in addAssignmentFrame.winfo_children(): # Delete quarter/curve entries and dropdowns
            if widget.grid_info()["row"] == 7:
                widget.destroy()
    
# Add an assignment object after passing a bunch of error checks, take values from entry boxes and dropdowns
def addAssignment():
    global regularGradeTypes
    global examTypes
    
    # Define some variables
    category = selectedType.get()
    stuName = selectedStudent.get() # Student's name (a string)
    if stuName == "ALL STUDENTS":
        student = ALLSTUDENTS # Set student as ALL STUDENTS object instead
    else:
        # Get the student OBJECT to manipulate
        student = findStudent(stuName)
            
    if missingChecked.get() == 1: 
        studentScore = 0 # Set a missing grade to be ZERO
    elif missingChecked.get() == 0 and assignmentScoreEntry.get() == "": # Check if no score, not missing
        errorMsg.config(text = "Please enter the score your student recieved\n(If you don't know, you can\nmark as missing).")
        return
    else: # if missing is not checked and the entry box is not empty
        studentScore = assignmentScoreEntry.get()
    
    if category in examTypes:
        curve = selectedCurve.get() # save curve in a variable
        c = examTypes.index(category) # Save index so we can access the weight in that same index
        catWeight = examWeights[c]
    elif category in regularGradeTypes:
        quarter = selectedQuarter.get()
        c = regularGradeTypes.index(category)
        catWeight = regularGradeWeights[c] # Save weight using c as an index
        
    if selectedStudent.get() == "None": # If no student has been selected
        errorMsg.config(text = "Please select a student from your list,\nand press the 'Add Assignment To Student' button\nto edit them here.")
        return
    elif category == "":
        errorMsg.config(text = "Please select an assignment type!")
        return
    elif assignmentNameEntry.get() == "":
        errorMsg.config(text = "Please enter a full name for your assignment!")
        return
    # Check if student already has this assignment
    elif student.name == "ALL STUDENTS" and allStudents == []:
        errorMsg.config(text = "Cannot use the ALL STUDENTS option\nif there are no students.")
        return
    elif student.name != "ALL STUDENTS" and student.findAssignment(assignmentNameEntry.get(), False) != None:
        errorMsg.config(text = student.name+" already has this assignment.")
        return
    # Check if one or more students already have this assignment, when using the ALL STUDENTS option
    elif student.name == "ALL STUDENTS" and student.findDuplicates(assignmentNameEntry.get()) != "":
        errorMsg.config(text = f"Duplicate error: {student.findDuplicates(assignmentNameEntry.get())}") # Set error message to be whatever students are collected using the method
        return
    elif assignmentMaxEntry.get() == "":
        errorMsg.config(text = "Please enter the maximum points\nthat can be earned on your assignment!")
        return
    elif category in regularGradeTypes and quarter == "":
        errorMsg.config(text = "Please enter a quarter for your assignment!")
        return
    # Use findGradeObject to return the grade object, then calculate curve to check if a default curve is possible
    # Use earlier studentScore variable to check missing status
    # Check if score > max as INTS, not STRINGS
    elif studentScore != 0 and float(studentScore) > float(assignmentMaxEntry.get()): 
        errorMsg.config(text = "Students cannot receive a score \nexceeding the maximum points.")
        return
    else: # If we pass all the error checks add a new assignment to the selected student
        if student.name == "ALL STUDENTS": # if we are adding to allStudents, create a new assignment for each student
            if category in regularGradeTypes: # If it's a regular grade -- ALLSTUDENTS
                for stu in allStudents:
                    newAssignment = RegularGrade(category, assignmentNameEntry.get(), catWeight, assignmentMaxEntry.get(), 0, quarter)
                    newAssignment.isMissing = True # Set to missing by default
                    stu.missing.append(newAssignment)
                    stu.allGrades.append(newAssignment)
            else: # If it's an exam -- ALLSTUDENTS
                for stu in allStudents:
                    newAssignment = Exam(category, assignmentNameEntry.get(), catWeight, assignmentMaxEntry.get(), 0, curve)
                    newAssignment.isMissing = True
                    stu.missing.append(newAssignment)
                    stu.allGrades.append(newAssignment)
            # Update GUI with a confirmation message
            missingLabel.config(text = "New assignment "+newAssignment.fullTitle+" added to all of your students.")
        else: # If we are adding assignment to a single student
            if category in regularGradeTypes:
                newAssignment = RegularGrade(category, assignmentNameEntry.get(), catWeight,
                                             assignmentMaxEntry.get(), studentScore, quarter)
                selectedQuarter.set("") # Reset selected quarter
            else:
                newAssignment = Exam(category, assignmentNameEntry.get(), catWeight,
                                     assignmentMaxEntry.get(), studentScore, curve)
                selectedCurve.set("Default")
            if missingChecked.get() == 1: # If assignment was marked missing:
                newAssignment.isMissing = True
                student.missing.append(newAssignment)
            # Update GUI with a confirmation message
            missingLabel.config(text = "New assignment "+newAssignment.fullTitle+" added to "+student.name+".") 
                
            student.allGrades.append(newAssignment) # Add assignment to the student's allGrades list
            
        # Add assignment to the assigList interface (if it's not in there already)
        if newAssignment.fullTitle not in assigList.get(0, "end"):
            assigList.insert("end", newAssignment.fullTitle)
        allAssignments.append(newAssignment.fullTitle) # add fullTitle, not object
            
        # Clear all the entry boxes and reset dropdown menus
        assignmentNameEntry.delete(0, tk.END)
        assignmentMaxEntry.delete(0, tk.END)
        assignmentScoreEntry.delete(0, tk.END)
        missingBox.deselect()
        selectedType.set("")

# Save changes made to an assignment through the edit dropdown menu -- even if editing 
def saveChanges():
    # First find the student object using the function findStudent() and the respective assignment object
    student = findStudent(selectedStudent.get()) 
    
    # Throw error message if user attempts to save changes to an assignment WITHOUT selecting a student first
    try: student.nothing()  
    except: 
        errorMsg.config(text = "Please select a student from your list,\nand press the 'Add Assignment To Student' button\nto edit them here.")
        return # Exit function to prevent error from attempting to use new student variable
            
    if len(student.allGrades) == 0:
        errorMsg.config(text = "This assignment has not been added\nto your student yet. Press Add instead!")
        return
    elif student.findAssignment(selectedAssignment.get(), False) == None: # Check if this assignment is not already given to the student i.e. a new assignment
        errorMsg.config(text = "This assignment has not been added\nto your student yet. Press Add instead!")
        return
    elif missingChecked.get() == 0 and assignmentScoreEntry.get() == "": # If not missing, but there is no score
        errorMsg.config(text = "Please enter a score for your student's assignment\n(If you don't know, you can mark it missing!)")
        return
    elif missingChecked.get() == 1 and assignmentScoreEntry.get() != "": # If missing, and there IS a score
        errorMsg.config(text = "Please uncheck the missing box if you\nhave entered a score for this assignment.")
        return
    elif assignmentScoreEntry.get() != "" and float(assignmentScoreEntry.get()) > float(assignmentMaxEntry.get()):
        errorMsg.config(text = "Student cannot receive a score\nthat exceeds the maximum points.")
        return
    else:
        assignment = student.findAssignment(selectedAssignment.get(), False) # Retrieve assignment object from student method
        assignment.title = selectedType.get() # Save any changes made in entry boxes and dropdowns through StringVar's
        assignment.fullTitle = assignmentNameEntry.get()
        assignment.max = assignmentMaxEntry.get()
        
        if missingChecked.get() == 1: # If assignment was marked missing
            assignment.isMissing = True 
            # Add assignment to student's missing list if it's not already in there
            if assignment not in student.missing:
                student.missing.append(assignment) # missing list contains assignment objects, not names        
        elif missingChecked.get() == 0: # If not missing and a score was entered
            assignment.received = assignmentScoreEntry.get()
            assignment.score = float(assignment.received)/float(assignment.max) # Recalculate and round score
            assignment.score = round(assignment.score, 2)
            assignment.isMissing = False # Change status of assignment based on the new setting of the box
            # REMOVE (first instance of) assignment from student's missing list
            if assignment in student.missing:
                student.missing.remove(assignment) 
            
        # Update quarter and curve
        if selectedType.get() in regularGradeTypes:
            assignment.quarter = selectedQuarter.get()
        elif selectedType.get() in examTypes:
            assignment.curve = selectedCurve.get()
            
        missingLabel.config(text = "Changes saved to "+assignment.fullTitle+".")
    
# Adds comments to a student or to all students
def addComments(name):
    comments = addCommentsEntry.get()
    if comments == "":
        errorMsg.config(text = "No comments to add.")
    elif name == "":
        errorMsg.config(text = "A student has not been selected to add comments to!")
    elif allStudents == []: # Check for attempt to add comments without any students
        errorMsg.config(text = "No students have been added to add comments to!")
    elif name == "ALL STUDENTS":
        for stu in allStudents:
            stu.comments = comments
    else:
        for stu in allStudents:
            if stu.name == name:
                stu.comments = comments
                missingLabel.config(text = f"Comment added to {name}")
        
# For saving ALL data -- every separate item is stored IN A LIST
def writeData():
    # Save fields to make csv file understandable
    fields = ["Name","Comments","Title","Full Title","Weight","Maximum Score",
              "Missing Status""Received Score","Overall Score", "Quarter/Curve"]
    # Save other information as a SINGLE list
    everything = [[weightTotal, regularGradeTypes, regularGradeWeights, examTypes, examWeights], fields]
    if allStudents == []: # If no students have been added we can still save the grading system
        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(everything) # write list items as rows
    else: # If there are students to save as well as the grading system
        for stu in allStudents:
            everything.append(stu.export())
        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(everything)
            
# For loading ALL data
def readData():
    global weightTotal
    global regularGradeTypes
    global regularGradeWeights
    global examTypes
    global examWeights
    global currRow
    global curveOptions
    global allStudents
    global allAssignments
    
    # Reset allStudents, allAssignments, listboxes to make sure we can't load over old data
    allStudents = []
    allAssignments = []
    assigList.delete(0, tk.END)
    studentList.delete(1, tk.END)
    
    with open(filepath, "r", newline = "") as file:
        reader = csv.reader(file) 
        r = list(reader) # convert the CSV reader into a list
        
        if r[0] == ['0', '[]', '[]', '[]', '[]'] and 2 >= len(r): # Check if the first row is empty i.e. no grading system
            errorMsg.config(text = "There is no data to load!")
            return
        else:
            # Going through the first few rows manually that are not student or grade values
            # Using ast here to convert to lists, rather than having [ and ] be strings
            weightTotal = r[0][0] # convert to a float
            regularGradeTypes = ast.literal_eval(r[0][1])
            regularGradeWeights = ast.literal_eval(r[0][2]) # use indexing here because there is now an extra list
            examTypes = ast.literal_eval(r[0][3])
            examWeights = ast.literal_eval(r[0][4])

            # r[0] are the weights/types info
            # r[1] are the fields
            # r[2], 3, 4 ... are the students
            for line in r:
                if line == r[0] or line == r[1]: # line = lines in the reader
                    pass
                elif len(r) < 2: # If there are no students
                    pass
                else:
                    for item in line:
                        if item == line[0]: # Handling first part
                            item = ast.literal_eval(item) # Evaluate it so it actually works as a list and is iterable
                            loadStudent = Student(item[0]) # Load in student's name and comments
                            loadStudent.comments = item[1]
                            if loadStudent not in allStudents:
                                allStudents.append(loadStudent) # Add new student to allStudents
                        else: # creating objects from the grade lists
                            item = ast.literal_eval(item)
                            # Handle regular grades and exams separately
                            if item[7] not in curveOptions: # If item is a regular grade
                                loadGrade = RegularGrade(item[0], item[1], float(item[2]), float(item[3]), float(item[5]),
                                                         item[7])
                            else:
                                loadGrade = Exam(item[0], item[1], float(item[2]), float(item[3]), float(item[5]), item[7])
                            # Set grade to missing if isMissing is True
                            if item[4]:
                                loadGrade.isMissing = True
                                loadStudent.missing.append(loadGrade) # Append grade to student's missing list if missing
                            # Add grade to student's allGrades list
                            loadStudent.allGrades.append(loadGrade)
                            if loadGrade.fullTitle not in allAssignments:
                                allAssignments.append(loadGrade.fullTitle) # Add TITLE to general allAssignments list

        # Convert weights to int's to prevent errors
        weightTotal = float(weightTotal)

        # Update GUI with new information
        weightTotalLabel.config(text = "Total weight: "+str(weightTotal))
        rRow = 3 # Variables which replace currRow per assignment type
        eRow = 3
        if regularGradeTypes != []: # Create labels and 'Delete' buttons for each category saved in data
            for typ in regularGradeTypes: # Redraw old labels
                c = regularGradeTypes.index(typ)
                newGradeType = tk.Label(gradingSysTop, text = typ+" : "+str(regularGradeWeights[c]), font = "Arial 15", bg = "white")
                newGradeType.grid(row = rRow, column = 0)
                # NOTE: USE LAMBDA x = y: delCategory(x, isExam) TO CAPTURE THE CURRENT VALUE OF TYP/ETYP IN THE LOOP!!!
                newGradeDel = tk.Button(gradingSysTop, text = "Delete", bg = "white", command = lambda t = typ: delCategory(t, False)) # Pass as a regular grade
                newGradeDel.grid(row = rRow, column = 1)
                rRow += 1 # Increment rRow
            eRow = rRow + 1 # set eRow to be below rRow 
            currRow = rRow + 1
        if examTypes != []:
            for eTyp in examTypes:
                c = examTypes.index(eTyp)
                newGradeType = tk.Label(gradingSysTop, text = eTyp+" : "+str(examWeights[c]), font = "Arial 15", bg = "white")
                newGradeType.grid(row = eRow, column = 0)
                newGradeDel = tk.Button(gradingSysTop, text = "Delete", bg = "white", command = lambda e = eTyp: delCategory(e, True)) # Pass as an Exam
                newGradeDel.grid(row = eRow, column = 1)
                eRow += 1 # Increment eRow
            currRow = eRow + 1 # set currRow to be below eRow

        updateSystem() # Update the system automatically

        # Now display everything student-related on the GUI
        for assigFT in allAssignments:
            assigList.insert("end", assigFT)
        for stu in allStudents:
            studentList.insert("end", stu.name)
        
# Function to calculate a student's grade taking into account all their assignments/exams, and return their report card in a new window
def generateReportCard(name):
    if name == "":
        errorMsg.config(text = "Please select a student to generate their report card.")
    elif name == "ALL STUDENTS":
        errorMsg.config(text = "Cannot generate the report cards\nof all your students at once.")
    else:
        missingAssigs = []
        student = findStudent(name)
        final = 0
        done = [] # To collect categories that have already been considered
        wTotal = 0 # to collect weights so we can take the weighted average with zeroes
        
        if len(student.allGrades) == 0: # Check for student with no grades
            errorMsg.config(text = "Cannot generate the report card of a student\nwith no grades.")
            return
        else:
            for grade in student.allGrades:
                currTitle = grade.title # save current title to be checked against
                currWeight = grade.weight
                startingPoint = grade.fullTitle # Save the fullTitle so we can check if we've found everything
                runningTotal = 0 

                if grade.isMissing: # Collect missing assignments to be added to comment
                    missingAssigs.append(grade.fullTitle)

                if isinstance(grade, Exam): # If an exam (missing assignments will also be calculated into the final grade)
                    if checkForMultiple(grade.fullTitle) == None:
                        errorMsg.config(text = f"There are not enough students assigned {grade.fullTitle}\nto use the Default curve! Please adjust this exam.")
                        return # Exit the function
                    elif grade.isMissing: # if the grade is missing consider it a zero
                        runningTotal += 0
                    elif grade.title in done:
                        pass
                    else: # Collect and add all grades for a certain category, then weight them and add to the final
                        for e in student.allGrades: # Use a different variable e for exam
                            if e.title == currTitle:
                                runningTotal += e.calculateCurve() # add the curved grade
                # Collect and add all grades for a certain category, then weight them and add to the final
                elif isinstance(grade, RegularGrade):
                    if grade.isMissing:
                        runningTotal += 0 # if the grade is missing consider it a zero
                    elif grade.title in done:
                        pass
                    else:
                        for r in student.allGrades: # Use a different variable r for regular
                            if r.title == currTitle:
                                runningTotal += r.score
                final += runningTotal * currWeight # Weight the grade total for this Title and add to the final
                done.append(grade.title)
                wTotal += grade.weight # We want to divide by ALL the weights, so a score of zero has meaning

        final = final / wTotal # Divide by all weights to get the weighted total
        final = round(final, 2) # Round final grade to two decimal points and then multiply by 100 to get a percent
        final = final*100

        # Create a separate window to display results
        reportcard = tk.Toplevel(app, bg = "lightblue")
        reportcard.geometry("500x200")
        reportcard.title("Report Card for "+name)

        #Labels for name, grade, comments
        nameLabel = tk.Label(reportcard, text = name, font = "Arial 15 bold", borderwidth=1, relief = "solid")
        nameLabel.pack(side = "top", pady = (20, 0))
        # Add on missing assignments to comments if applicable
        if missingAssigs == []:
            if student.comments == "": # Check if no personal comment
                finalComments = f"{student.name} is not missing any assignments. Good work!" # Can add on to an empty string without error
            else:
                finalComments = student.comments + f" {student.name} is not missing any assignments. Good work!"
        else: # if there are no comments but there are missing assignments, list them
            if student.comments == "":
                finalComments = f"{student.name} is missing "
            else:
                finalComments = student.comments + f" {student.name} is missing "
            for item in missingAssigs:
                if len(missingAssigs) == 1: # if there's only one item in the list
                    finalComments += item
                elif item != missingAssigs[-1]: # If it's not the last item in the list
                    finalComments += item
                    finalComments += ", "
                else:
                    finalComments += "and "
                    finalComments += item
                    finalComments += "." # Fix grammar for prsaveofessional appearance

        gradeLabel = tk.Label(reportcard, text = f"Final weighted grade:\n{final}%", font = "Arial 15", borderwidth=1, relief = "solid")
        gradeLabel.pack(side = "top", padx = 20, pady = 2)
        commentsLabel = tk.Label(reportcard, text = finalComments, font = "Arial 12", borderwidth=1, relief = "solid")
        commentsLabel.pack(side = "top", padx = 20, pady = (0, 20))


        reportcard.mainloop()
    
####### CURRENT ISSUES:
            
#-----------------------------------------------------------------------------------------------------------------

app.mainloop() 