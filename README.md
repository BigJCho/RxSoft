# RxSoft

A first attempt at a "larger" project

## To the Reader:

#### Purpose of Project

This project serves to replicate popular functionality that I would use on a daily basis at my job as a Retail Pharmacist. It is heavily based on the PrimeRx Software and the default Qt styling is similar to older versions of the software. The functions include:
 - Patient profile searching and display
 - Altering and saving prescription data
 - Displaying prescriptions based on date filled
 - Quick changing date of fill and refill

The project was completed using PyQt5 and SQLite3.

#### Skillset Developed

Completion of the project in its current state involved developing in these areas:
 - Database design, querying, updating, filtering, joining
 - Object based approach to problems, including using the View-Model methodology that Qt offers
 - Interconnecting signals, slots, methods, classes, global and local variables
 - Designing based on user readability and ease of use, especially with consideration to the Edit functionality
 - Debugging and iterative development

## To the Developer:

### Functionality

#### Patient F5
 - Press F5, or click the button, for the central stacked widget to switch to the "PatientView"
 - Accepts a string and searches a patient upon pressing Return
 - Splits the string using ","
 - Last Name, First Name, Date of Birth format
 - Upon double-click in the opened search window the "PatientView" will have it's model updated with all prescription associated with the selected patient

#### Browse F6
 - Press F6, or click the button, for the central stacked widget to switch to the "BrowseView"
 - On the left of the window all dates where a prescription has been filled will be displayed
 - Upon clicking a date the right of the window will populate with all prescriptions filled on the associated date

#### Edit Ctrl+E
 - Press Ctrl + E, or click the button, with an entire row selected to open a new window that displays all relational values or the associated prescription
 - The line with the doctor's name accepts a string that splits on "," and will open up a search window
 - Last Name, First Name, NPI, DEA is the format
 - The line with the drug name accepts a string and will open a search window based on drug name
 - Qty and day supply accept integers
 - Transmit Claim changes the status from U to B or does nothing if not applicable
 - Reverse Claim changes the status from B to U or does nothing if not applicable
 - Exit closes the window
 - Save updates the table "rx" with the fields that currently populate the window

#### Refill Ctrl+R
 - Press Ctrl + R, or click the button, with an entire row selected in the "PatientView" to increment the "refill_number" in the table "rx"
 - Checks if this function is valid (if there are refills remaining) and displays a message box with the outcome

#### Schedule Ctrl+S
 - Press Ctrl + S, or click the button, with an entire row selected in the "PatientView" to open a small window
 - The new window displays the current date of fill with the associated prescription
 - The text line accepts a positive integer or a date in the MMDDYY format
 - Entering a positive integer: X will increment the date filled by X days
 - Entering a date will set the date_filled to that date 

### Further development
I decided to leave the project at this current state as I felt comfortable with the practice gained Creating, Reading, Updating, and Deleting data from a database file. And the practice gained displaying all the information to a user in a readable way.

Further development would include error-handling all the NULL values that could happen during operation, the addition of a function to create a brand new prescription, and the addition of a function to create new patients and doctors.
