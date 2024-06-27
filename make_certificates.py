#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 23:58:10 2024

@author: nadiablago
"""
import os
from astropy.table import Table
import subprocess, sys

#Copy the tex file.
#Replace the name.
#Compile.

PATH = "./certificates_attendance/CertificateAttendanceCEWorkshop"
PATH = os.path.abspath(PATH)
ATTENDANCE_FILE = os.path.join(PATH, "../attendace_poster.csv")
BODY_EMAIL_FILE = os.path.join(PATH, "../body_email.txt")

def replace_tex(input_tex, output_tex, replacements):
    '''
    The funciton copies the input_tex with a different name called output_tex.
    Then, inside this file it replaces the oldstring with newstring.

    Parameters
    ----------
    input_tex : str
        path of the input Latex tex file (tempalte).
    output_tex : str
        path of the final Latex (name with the name of the participant).
    replacements : dictionary
        Dictionary saying which words should be replaced by which.

    Returns
    -------
    None.
    Writes the new output file with the substitutions.

    '''
    
        

    with open(input_tex, "r") as infile, open(output_tex, "w") as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)
    
    
def generate_certificates():
    '''
    Generates (replaces the template and compiles) the pdf for each participant 
    with the name of the person without spaces.

    Returns
    -------
    None.
    Generates the PDF.

    '''
    
    
    participants_list = Table.read(ATTENDANCE_FILE, format="ascii.csv")
    
    os.chdir(PATH)
    
    for part in participants_list:

        name = part["Name"].strip().replace(" ", "")
        title = part["Title"].strip().replace(".", "")
        mode = part["AttMode"]
        if mode !='':
            mode = mode.strip()
        attended = part["Attended"].strip()
        poster = part["Poster"].strip()
        
        if mode =="In person":
            newtex = os.path.join(PATH, f"InPerson_{name}.tex")
        else:
            newtex = os.path.join(PATH, f"Online_{name}.tex")

        if attended =="Yes" and poster=="Yes":
            template = os.path.join(PATH, "Certificate_template_poster.tex")
        elif attended =="Yes" and poster=="No":
            template = os.path.join(PATH, "Certificate_template_attendance_only.tex")
        else:
            #Next participant.
            print (f"Participant {name} did not attend.")
            continue
            
        #Here what we replace. We replace the name and attendance type.
        replacements = { "Name Participant": "{:}. {:}".format(title, part["Name"]),
                      "Attendance Type" : "{:}".format(mode)}
        
        replace_tex(template, newtex, replacements)
        
        cmd = f"pdflatex -pdf -interaction=nonstopmode {newtex}"
        #print (cmd)
        
        subprocess.run(cmd, shell = True, executable="/bin/bash")

        
    subprocess.run("latexmk -c", shell = True, executable="/bin/bash")


def send_emails_to_list(dry_run=True):
    '''
    Reads the list of participants, selects the right PDF for each person depending if it was onlne or in person.
    Then, creates a mail command and sends it to the email address in the csv file.
    
    if dry_run is selected, the command is printed, but not executed.
    
    '''
    
    
    participants_list = Table.read(ATTENDANCE_FILE, format="ascii.csv")
    
    os.chdir(PATH)
    
    for part in participants_list:

        name = part["Name"].strip().replace(" ", "")
        mode = part["AttMode"]
        if mode !='':
            mode = mode.strip()
        attended = part["Attended"].strip()
        email = part["Email"].strip()
        
        if attended == "No":
            continue
        
        if mode =="In person":
            newtex = os.path.join(PATH, f"InPerson_{name}.tex")
        else:
            newtex = os.path.join(PATH, f"Online_{name}.tex")

        attachment = newtex.replace(".tex", ".pdf")
        
        if os.path.isfile(attachment):
            cmd = f'mail -s "Certificate of attendance: 360º Approach to Common Envelope Evolution" -A {attachment} {email} < {BODY_EMAIL_FILE}'

            print (cmd)
            if not dry_run:
                subprocess.run(cmd, shell = True, executable="/bin/bash")
                subprocess.run("sleep 3", shell = True, executable="/bin/bash")
        else:
            print (f"PDF certificate for {name} not found!")
            
def send_certificate(attachment, email, dry_run=True):
    '''
    Sends an email using the command line to a given email with an attachment.
    The body is read from a txt file.

    Parameters
    ----------
    attachment : str
        Path to the PDF.
    email : str
        email to which the email shold be sent.
    dry_run : bool, optional
        If dry_run, no emails are sent, only the command is printed. The default is True.

    Returns
    -------
    None.

    '''
    

    cmd = f'mail -s "Certificate of attendance: 360º Approach to Common Envelope Evolution" -A {attachment} {email} < {BODY_EMAIL_FILE}'

    print (cmd)
    if (not dry_run):
        subprocess.run(cmd, shell = True, executable="/bin/bash")

if __name__ == "__main__":
    
    generate_certificates()
    
    send_emails_to_list(dry_run=True)

    