# Reportcard-Generator
App made with Tkinter to manage multiple students assignments and grades. User can recreate their grading system, edit students' grades and information, and generate a report card with GPA and personal comments.


Sorry for the global variables. I made this a while ago for school.

***TUTORIAL:***
1. Go to Create Your Grading System section and type in a category name and weight. The 'Category' represents a type of assignment you would use in real life (Test, Quiz, Assignment, Midterm, Finals, Participation etc.) If you want your assignment to be curved, press "Add an Exam". If not, press "Add an Assignment type". Your weights **MUST ADD TO 100% TOTAL** before you can create any assignments. When you're done press "Update Grading System".
2. Go to Student's name and type in your student's name. Create all your students.
3. If you want to add an assignment to a specific student, click on their name from the list and hit "Add assignment to student". If you want to add an assignment to ALL of your students, click on ALL STUDENTS (first in the list) and hit "Add assignment to student". If you create more students after you add an assignment to ALL STUDENTS, they will not have the assignment. I will fix it later.
4. Now focus on the Add an Assignment to ___ area. Pick what type of assignment you want from the dropdown list (you created the categories earlier). Fill in the information and if you are creating an exam, pick a curve. Default curve is based on the highest scoring student's score. Square root is more generous and cube root is most generous. If your specific student is missing the assignment check the missing box. If you selected ALL STUDENTS check the missing box unless you want to give them all the same grade. Hit "Add new assignment".
5. To edit a student's score on an assignment, click on their name from the list and hit "Edit Assignment", THEN **look over to the right** and pick the assignment you want to edit from the dropdown menu. Now you can uncheck the missing box and change the score. Make sure to hit the "Save Changes" button.
6. Add your comments for the student in the little text box underneath the list of students. Select the student's name from the list, and hit the button to the right of the text box to submit.
7. Save your data with the SAVE ALL button and LOAD it next time you use the program. Your data can be found in a CSV file created in your Downloads folder. Please don't move the CSV file.
8. Hit the "Generate Report Card" button.
