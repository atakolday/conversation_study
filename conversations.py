###################################################
########### CONVERSATION STUDY EMAILS #############


### DEPENDENCIES ###

from time import sleep
import pandas as pd

from dateutil.parser import parse
from termcolor import colored

import webbrowser

import os

from tqdm import tqdm

pd.options.mode.chained_assignment = None

## Data Wrangling ##

###########################################

print('')
path = input(">>> Press ENTER for default schedule, or 'test' for testing:  ")

if path == 'test':
    df = pd.read_csv('emails_test.csv')

else:
    df = pd.read_csv('Week 7 - schedule.csv')       
###########################################

df.columns = list(df.iloc[0])
df = df.drop(0, axis=0)

## Schedule ##

schedule = df[[
    'day_week', 'date', 'time_PT',
    'RESPONDENT_ID', 'participant_id', 'participant name',
    'email', 'timezone', 'inparty',
    'topics', 'topic_code', 'zoom_main', 'confirmed?'
]]

schedule['timezone'] = schedule['timezone'].map(lambda x: int(x) - 1)

schedule = schedule.reset_index().drop('index', axis=1)

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

## Functions ##

def tzone(n):
    """
    Takes in a number (0, 1, 2, 3),
    returns the timezone (type = str).
    """
    if n == 0:
        return "Pacific"
    elif n == 1:
        return "Mountain"
    elif n == 2:
        return "Central"
    elif n == 3:
        return "Eastern"

def adj_time(df=schedule):

    """
    Adjusts the timezones of conversations
    for each participant based on the
    "timezone" column in the dataframe.
    """

    t, z = df['time_PT'].values[0], df['timezone'].values[0]

    tt = int(t.split(':')[0])
    am_pm = t.split(':')[1]
    adj = tt + z

    if adj == 12:
        adj_t = "12:00 PM"
    elif adj > 11:
        adj_t = "{}:00 PM".format(adj - 12)
    else:
        adj_t = f"{adj}:{am_pm}"

    return adj_t

def conversation():
    
    p1 = input("What is Participant 1's email? ")
    p2 = input("What is Participant 2's email? ")
    
    df_p1 = schedule.loc[schedule.email == p1].reset_index().drop('index', axis=1)
    df_p2 = schedule.loc[schedule.email == p2].reset_index().drop('index', axis=1)
    
    if df_p1.topic_code[0] != df_p2.topic_code[0]:
        print('')
        print('Uh oh! The topic codes for the participants do not match!')
        print('')
    
    else:
        mo, day = (parse(df_p1.date[0]).strftime('%b %-d')).split(' ')
        t, am_pm = df_p1.time_PT[0].split(' ') 

        path = f'conversation_notes/{mo}_{day}_{t.split(":")[0] + am_pm}.txt'

        with open(path, 'w') as f:
            f.write(f"""Conversation - {df_p1.day_week[0]}, {parse(df_p1.date[0]).strftime('%b %-d')}, at { df_p1.time_PT[0]} (Pacific Time)


Participant #1
    >> Name: {df_p1["participant name"][0]}
    >> Email: {p1}
    >> rID: {df_p1.RESPONDENT_ID[0]}
    >> pID: {df_p1.participant_id[0]}
    >> Party: {df_p1.inparty[0]}

Participant #2
    >> Name: {df_p2["participant name"][0]}
    >> Email: {p2}
    >> rID: {df_p2.RESPONDENT_ID[0]}
    >> pID: {df_p2.participant_id[0]}
    >> Party: {df_p2.inparty[0]}   

>> Topic Code: {df_p1.topic_code[0]}
>> Topics: {df_p1.topics[0]}


{(df_p1.topics[0]).split('_')[0]}:
    - 
    - 
    - 

{(df_p1.topics[0].split('_')[1])}:
    - 
    - 
    -
                    """)

    os_str = f"open /System/Applications/TextEdit.app {path}"
    os.system(os_str); 

    print('')
    zoom = input(" >> Would you like to launch the Zoom meeting now? [y/n]  ")
    if zoom == 'y':
        print('')
        sleep(.1)
        print(colored('Launching Zoom meeting...', attrs=['bold']))
        print('')
        
        webbrowser.open(f'{df_p2.zoom_main[0]}')
    
    else:
        pass

def date_suffix(date):
    if date[-1] == '1':
        return 'st'
    elif date[-1] == '2':
        return 'nd'
    elif date[-1] == '3':
        return 'rd'
    else: 
        return 'th'

def filter_schedule(cond1=None, cond2=None, df=schedule):
    """
    cond1: day_week value (e.g. 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')
    cond2: confirmed? value (e.g. 'no', 'yes', 'RES')
    
    if no argument is passed, returns "schedule"
    """
        
    if cond1 is not None: df = df.loc[df.day_week == cond1] 

    if cond2 is not None: df = df.loc[df['confirmed?'] == cond2] 

    return df

###################################################

### EMAILS ###

import smtplib, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# new subclass for adding attachment
from email.mime.application import MIMEApplication

## Credentials ##

from Auth import SSNLAuth         # custom .py file with email address and app access password

email_from = SSNLAuth().EMAIL
password = SSNLAuth().PASS

## Email Functions ##

def rID_invite():

    while True:

        rID = input('What is the RESPONDENT_ID? ')

        if rID not in list(schedule.RESPONDENT_ID):
            print("This participant is not assigned to you.")
            continue

        df = schedule.loc[schedule.RESPONDENT_ID == str(rID)].reset_index().drop('index', axis=1)

        ###########################################################################

        date_string = parse(df['date'][0]).strftime('%B %-d')

        email_to = df['email'][0] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Invitation: Part II Conversation Study (1hr for $20) -- Action Required'

        # Define the HTML document
        html = f'''
            <html>
                <body>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                    <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                    <p>&nbsp;</p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{df.day_week[0]}, {date_string + date_suffix(date_string)}, at {adj_time(df)} ({tzone(df.timezone[0])} Time).</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                    <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                    <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                    <p>&nbsp;</p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study should not take more than 45 minutes, and you will be paid $20 for your participation.</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">We are very grateful for your participation, and we hope to see you soon!</span></span></p>
                    <p>&nbsp;</p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">All the best,</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">The Research Team</span></span></p>
                </body>
            </html>
            '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())

        print('')
        print('')
        print(f' >> Email to {email_to} successfully sent!')
        print('')

        ###########################################################################

        cont = input("Would you like to continue? [y/n] ")
        if cont == 'n':
            break
        continue

def rID_reminder():

    while True:

        rID = input('What is the RESPONDENT_ID? ')

        if rID not in list(schedule.RESPONDENT_ID):
            print("This participant is not assigned to you.")
            continue

        df = schedule.loc[schedule.RESPONDENT_ID == str(rID)].reset_index().drop('index', axis=1)

        ###########################################################################

        date_string = parse(df['date'][0]).strftime('%B %-d')
        
        email_to = df['email'][0] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'REMINDER: Part II Conversation Study (1hr for $20) -- Action Required'

        # Define the HTML document
        html = f'''
            <html>
                <body>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                    <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                    <p>&nbsp;</p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{df.day_week[0]}, {date_string + date_suffix(date_string)}, at {adj_time(df)} ({tzone(df.timezone[0])} Time).</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                    <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                    <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                    <p>&nbsp;</p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">We are very grateful for your participation, and we hope to see you soon!</span></span></p>
                    <p>&nbsp;</p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">All the best,</span></span></p>
                    <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">The Research Team</span></span></p>
                </body>
            </html>
            '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())

        print('')
        print(f' >> Email to {email_to} successfully sent!')
        print('')

        ###########################################################################

        cont = input("Would you like to continue? [y/n] ")
        if cont == 'n':
            break
        continue

def invite_slot():

    dw_t = input("Day_Week-time_PT? (e.g. Monday-7:00 AM)  ")
    dw, t = dw_t.split("-")

    df = schedule.loc[(schedule.day_week == dw) & (schedule.time_PT == t)].reset_index().drop('index', axis=1)

    if len(df.index) == 0:
        print('')
        print(' > Uh oh! Looks like your input was wrong.')
        print(' > (Tip: Check that you wrote exactly in the form of "Monday-7:00 AM"')
        print('')

        invite_slot()

    ################### SENDING THE EMAIL ######################

    for i in list(df.index):

        date_string = parse(df['date'][i]).strftime('%B %-d')

        email_to = df['email'][i] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Invitation: Part II Conversation Study (1hr for $20) -- Action Required'

        # Define the HTML document
        html = f'''
        <html>
            <body>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p>&nbsp;</p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{df.day_week[i]}, {date_string + date_suffix(date_string)}, at {adj_time(df.iloc[i:i+1])} ({tzone(df.timezone[i])} Time).</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p>&nbsp;</p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">We are very grateful for your participation, and we hope to see you soon!</span></span></p>
                <p>&nbsp;</p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">All the best,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">The Research Team</span></span></p>
            </body>
        </html>
        '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())

            print(f' >> Email to {email_to} successfully sent!')
            print('')

def mass_invite():

    day = input('For what day of the week would you like to send the invitation emails?  ')
    df = schedule.loc[schedule.day_week == str(day)].reset_index().drop('index', axis=1)

    ################### SENDING THE EMAIL ######################
    count = 0                     # counter for successful iterations of function

    for i in list(df.index):

        date_string = parse(df['date'][i]).strftime('%B %-d')

        email_to = df['email'][i] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Invitation: Part II Conversation Study (1hr for $20) -- Action Required'

        # Define the HTML document
        html = f'''
        <html>
            <body>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{df.day_week[i]}, {date_string + date_suffix(date_string)}, at {adj_time(df.iloc[i:i+1])} ({tzone(df.timezone[i])} Time).</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">We are very grateful for your participation, and we hope to see you soon!</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">All the best,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">The Research Team</span></span></p>
            </body>
        </html>
        '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_from, password)
                server.sendmail(email_from, email_to, email_message.as_string())

                print(f' - Email to {email_to} successfully sent!')
                print('')
                
                count += 1
        
        except Exception as e:
            print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))
            raise e
    
        finally:
            if count == len(df.index):
                print(colored(f">>> TASK COMPLETED WITH {count} SUCCESSFUL ITERATIONS! <<<", attrs=['bold']))
                print('')

def mass_invite_v2():

    day = input('For what day of the week would you like to send the invitation emails?  ')
    df = schedule.loc[schedule.day_week == str(day)].reset_index().drop('index', axis=1)

    ################### SENDING THE EMAIL ######################
    count = 0                     # counter for successful iterations of function

    for i in tqdm(list(df.index), desc='Sending invitation emails'):

        date_string = parse(df['date'][i]).strftime('%B %-d')

        email_to = df['email'][i] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Invitation: Part II Conversation Study (1hr for $20) -- Action Required'

        # Define the HTML document
        html = f'''
        <html>
            <body>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{df.day_week[i]}, {date_string + date_suffix(date_string)}, at {adj_time(df.iloc[i:i+1])} ({tzone(df.timezone[i])} Time).</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study should not take more than 45 minutes, and you will be paid $20 for your participation.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">We are very grateful for your participation, and we hope to see you soon!</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">All the best,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">The Research Team</span></span></p>
            </body>
        </html>
        '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_from, password)
                server.sendmail(email_from, email_to, email_message.as_string())
                
                count += 1
        
        except Exception as e:
            print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))
            raise e
    
        
    if count == len(df.index):
        print('')
        print(colored(f"  >> TASK COMPLETED WITH {count} SUCCESSFUL ITERATIONS!", attrs=['bold']))
        print('')

def reminder_24hr():

    day = input('For what day of the week would you like to send the reminder emails? ')
    df = schedule.loc[
        (schedule.day_week == day) & 
        (schedule['confirmed?'] != 'yes')
    ].reset_index().drop('index', axis=1)

    ################### SENDING THE EMAIL ######################

    for i in list(df.index):

        date_string = parse(df['date'][i]).strftime('%B %-d')

        email_to = df['email'][i] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'REMINDER: Part II Conversation Study (1hr for $20) -- Action Required'

        # Define the HTML document
        html = f'''
        <html>
            <body>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p>&nbsp;</p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{df.day_week[i]}, {date_string + date_suffix(date_string)}, at {adj_time(df.iloc[i:i+1])} ({tzone(df.timezone[i])} Time).</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                <p>&nbsp;</p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">We are very grateful for your participation, and we hope to see you soon!</span></span></p>
                <p>&nbsp;</p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">All the best,</span></span></p>
                <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">The Research Team</span></span></p>
            </body>
        </html>
        '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())

            print(f' >> Email to {email_to} successfully sent!')
            print('')

def send_zoom():

    while True:

        rID = input("What is the RESPONDENT_ID? ")
        if rID not in list(schedule.RESPONDENT_ID):
            print("Participant not found! Please try again.")
            continue

        df = schedule.loc[schedule.RESPONDENT_ID == str(rID)].reset_index().drop('index', axis=1)

        ####################################

        date_string = parse(df['date'][0]).strftime('%B %-d')

        email_to = df['email'][0]

        # Create the HTML Document #

        html = f'''
            <html>
                <body>
                    <p dir="ltr"><span style="font-size: medium;">Hi,</span></p>
                    <p dir="ltr"><span style="font-size: medium;">Thank you so much for confirming.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">This is just a reminder that your conversation is set to start&nbsp;<strong>{df.day_week[0]}, {date_string + date_suffix(date_string)}, at {adj_time(df)} ({tzone(df.timezone[0])} Time).</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">- This study will ask you for your participant ID. Your participant ID&nbsp;<strong>{df.participant_id[0]}</strong>.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp;</span></p>
                    <p dir="ltr"><span style="text-decoration: underline; font-size: medium;"><strong>Instructions</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">This part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">On your appointment day, <strong>click on the Zoom link below two minutes before your scheduled time.</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">You don't need to install any extra software to join a Zoom meeting. You can do it all through a web browser. You just need to:</span></p>
                    <p dir="ltr"><span style="font-size: medium;"><strong>Click on the meeting link</strong>: {df.zoom_main[0]};</span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; A new tab will open on your web browser. If you don't have the Zoom desktop app installed, the page will urge you to download the app. <strong>You can ignore that message and click on:"Join from your Browser" (as shown below)</strong></span></p>
                    <p><span style="font-size: medium;">&nbsp;</span></p>
                    <img src='cid:myimageid' width="700">
                    <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; A pop-up window will appear asking you to give Zoom permission to access your camera and microphone. <strong>Click on &ldquo;allow&rdquo;.</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; You will be asked for your name. <strong>Please only provide your first (or preferred) name. Do not type your last name.</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">A moderator will be in the Zoom room to greet you. They will explain the study in more detail, guide you and your conversation partner through the conversation and share a survey link with you.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">We are very grateful for your participation, and we hope to see you soon!</span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp;</span></p>
                    <p dir="ltr"><span style="font-size: medium;">All the best,</span></p>
                    <p dir="ltr"><span style="font-size: medium;">The Research Team</span></p>
                    <p><span style="font-size: medium;">&nbsp;</span></p>
                </body>
            </html>
            '''

        ####################################

        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Information: Part II Conversation Study (1hr for $20)'

        ####################################
        def attach_file_to_email(email_message, filename, extra_headers=None):

            # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
            with open(filename, "rb") as f:
                file_attachment = MIMEApplication(f.read())

            # Add header/name to the attachments
            file_attachment.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Set up the input extra_headers for img
              ## Default is None: since for regular file attachments, it's not needed
              ## When given a value: the following code will run
                 ### Used to set the cid for image
            if extra_headers is not None:

                for name, value in extra_headers.items():
                    file_attachment.add_header(name, value)

            # Attach the file to the message
            email_message.attach(file_attachment)
        ####################################

        # Attach HTML
        email_message.attach(MIMEText(html, "html"))

        # Attach image
        attach_file_to_email(email_message, 'zoom.png', {'Content-ID': '<myimageid>'})

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())
            
            print('')
            print(f' >> Email to {email_to} successfully sent!')
            print('')

        ################

        cont = input("Would you like to send another email? [y/n] ")
        if cont == 'n':
            break
        continue

def send_zoom_v2():
    
    dw = input('For what day of the week would like to send the Zoom links? ')
    
    df = filter_schedule(str(dw), 'yes').reset_index(drop=True)
    
    print('')
    count = 0 
    for i in tqdm(list(df.index), desc='Sending invitation emails'):
        
        date_string = parse(df['date'][i]).strftime('%B %-d')

        email_to = df['email'][i]

        # Create the HTML Document #

        html = f'''
            <html>
                <body>
                    <p dir="ltr"><span style="font-size: medium;">Hi,</span></p>
                    <p dir="ltr"><span style="font-size: medium;">Thank you so much for confirming.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">This is just a reminder that your conversation is set to start&nbsp;<strong>{df.day_week[i]}, {date_string + date_suffix(date_string)}, at {adj_time(df.loc[[i]])} ({tzone(df.timezone[i])} Time).</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">- This study will ask you for your participant ID. Your participant ID&nbsp;<strong>{df.participant_id[i]}</strong>.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp;</span></p>
                    <p dir="ltr"><span style="text-decoration: underline; font-size: medium;"><strong>Instructions</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">This part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">On your appointment day, <strong>click on the Zoom link below two minutes before your scheduled time.</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">You don't need to install any extra software to join a Zoom meeting. You can do it all through a web browser. You just need to:</span></p>
                    <p dir="ltr"><span style="font-size: medium;"><strong>Click on the meeting link</strong>: {df.zoom_main[i]};</span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; A new tab will open on your web browser. If you don't have the Zoom desktop app installed, the page will urge you to download the app. <strong>You can ignore that message and click on:"Join from your Browser" (as shown below)</strong></span></p>
                    <p><span style="font-size: medium;">&nbsp;</span></p>
                    <img src='cid:myimageid' width="700">
                    <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; A pop-up window will appear asking you to give Zoom permission to access your camera and microphone. <strong>Click on &ldquo;allow&rdquo;.</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; You will be asked for your name. <strong>Please only provide your first (or preferred) name. Do not type your last name.</strong></span></p>
                    <p dir="ltr"><span style="font-size: medium;">A moderator will be in the Zoom room to greet you. They will explain the study in more detail, guide you and your conversation partner through the conversation and share a survey link with you.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">If you show up and, after 6 minutes, your conversation partner doesn&rsquo;t, you will be paid $3 for your time and will be given the chance to reschedule.</span></p>
                    <p dir="ltr"><span style="font-size: medium;">We are very grateful for your participation, and we hope to see you soon!</span></p>
                    <p dir="ltr"><span style="font-size: medium;">&nbsp;</span></p>
                    <p dir="ltr"><span style="font-size: medium;">All the best,</span></p>
                    <p dir="ltr"><span style="font-size: medium;">The Research Team</span></p>
                    <p><span style="font-size: medium;">&nbsp;</span></p>
                </body>
            </html>
            '''

        ####################################

        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Information: Part II Conversation Study (1hr for $20)'

        ####################################
        def attach_file_to_email(email_message, filename, extra_headers=None):

            # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
            with open(filename, "rb") as f:
                file_attachment = MIMEApplication(f.read())

            # Add header/name to the attachments
            file_attachment.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Set up the input extra_headers for img
              ## Default is None: since for regular file attachments, it's not needed
              ## When given a value: the following code will run
                 ### Used to set the cid for image
            if extra_headers is not None:

                for name, value in extra_headers.items():
                    file_attachment.add_header(name, value)

            # Attach the file to the message
            email_message.attach(file_attachment)
        ####################################

        # Attach HTML
        email_message.attach(MIMEText(html, "html"))

        # Attach image
        attach_file_to_email(email_message, 'zoom.png', {'Content-ID': '<myimageid>'})

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_from, password)
                server.sendmail(email_from, email_to, email_message.as_string())
                
                count += 1
        
        except Exception as e:
            print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))
            raise e 
            
        finally:
            if len(df.index) == count:
                print(colored(f">>> TASK COMPLETED WITH {count} SUCCESSFUL ITERATIONS! <<<", attrs=['bold']))
                print('')

def reminder_1hr():

    while True:

        rID = input('What is the RESPONDENT_ID? ')

        if rID not in list(schedule.RESPONDENT_ID):
            print("Participant with this RESPONDENT_ID does not exist.")
            continue

        df = schedule.loc[schedule.RESPONDENT_ID == str(rID)].reset_index().drop('index', axis=1)

        if f'{df["participant name"][0]}' in ['nan', '-']:
            salute = 'Hi,'
        else:
            salute = f'Hi {df["participant name"][0]},' 

        ###########################################################################

        email_to = df['email'][0] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Reminder: Part II Conversation Study (1hr for $20)'

        # Define the HTML document
        html = f'''
            <html>
                <body>
                    <p dir="ltr">{salute}&nbsp;</p>
                    <p dir="ltr">Your conversation is set to start approximately one hour from now, at {adj_time(df)} ({tzone(df.timezone[0])} Time) .&nbsp;</p>
                    <p dir="ltr">&nbsp;</p>
                    <p dir="ltr">Here are some reminders:&nbsp;</p>
                    <p dir="ltr">   - Your participant ID is <strong>{df.participant_id[0]}</strong></p>
                    <p dir="ltr">   - Zoom link:</p>
                    <p dir="ltr"><strong>   {df.zoom_main[0]}</strong></p>
                    <p dir="ltr">&nbsp;</p>
                    <p dir="ltr">Please plan to arrive two minutes early. This study will take about 1 hour to complete and you will be paid $20 dollars for your participation.&nbsp;</p>
                    <p dir="ltr">&nbsp;</p>
                    <p dir="ltr">Looking forward to seeing you soon!</p>
                    <p dir="ltr">&nbsp;</p>
                    <p dir="ltr">-- The Research Team</p>
                </body>
            </html>
            '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())

        print('')
        print(f' >> Email to {email_to} successfully sent!')
        print('')

        ###########################################################################

        cont = input("Would you like to continue? [y/n] ")
        if cont == 'n':
            break
        continue

def reschedule():

    while True:

        rID = input('What is the RESPONDENT_ID? ')

        if rID not in list(schedule.RESPONDENT_ID):
            print("This participant is not assigned to you.")
            continue

        df = schedule.loc[schedule.RESPONDENT_ID == str(rID)].reset_index().drop('index', axis=1)

        if f'{df["participant name"][0]}' == 'nan':
            salute = 'Hi,'
        else:
            salute = f'Hi {df["participant name"][0]},' 

        ###########################################################################

        email_to = df['email'][0] # email recipient

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = 'Reschedule: Part II Conversation Study (1hr for $20)'

        # Define the HTML document
        html = f'''
            <html>
                <body>
                    <p dir="ltr">{salute}&nbsp;</p>
                    <p dir="ltr">Unfortunately, your conversation partner can no longer attend your scheduled session. There may be other available time slots for later in the week. Would you be willing to reschedule?&nbsp;</p>
                    <p dir="ltr">If you are willing to reschedule, please let us know and we can share with you our availability for sometime later in the week.&nbsp;</p>
                    <p dir="ltr">We apologize for the inconvenience this may have caused, and we look forward to hearing from you soon!</p>
                    <p dir="ltr">&nbsp;</p>
                    <p dir="ltr">-- The Research Team</p>
                </body>
            </html>
            '''
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_message.as_string())

        print('')
        print(f' >> Email to {email_to} successfully sent!')
        print('')

        ###########################################################################

        cont = input("Would you like to continue? [y/n] ")
        if cont == 'n':
            break
        continue


#########################################
################ CONSOLE ################
#########################################

print(f'''
#######################################

{colored("Available functions to generate emails:", attrs=["bold"])}

{colored("Invite:", attrs=["underline"])}

   - rID_invite()      >>>  send invitation email by RESPONDENT_ID
   - invite_slot()     >>>  send invitation emails to each participant in a session (day_week, time_PT)
   - mass_invite()     >>>  send invitation emails to each participant for a given day (e.g. Monday, Tuesday, etc.)
   - mass_invite_v2()  >>>  updated mass_invite, added tqdm progress bar functionality

{colored('Reminder:', attrs=["underline"])}

   - rID_reminder()    >>>  send reminder email by RESPONDENT_ID
   - reminder_1hr()    >>>  send the 1-hr reminder email by RESPONDENT_ID
   - reminder_24hr()   >>>  send 24-hour reminder for participants who haven't confirmed by day_week
   - send_zoom()       >>>  send Zoom link and participant_id after confirmation
   - send_zoom_v2()    >>>  updated send_zoom, input 'day_week' and send zoom links to all confirmed participants 


{colored("Other:", attrs=["underline"])}

   - reschedule()      >>>  send the initial reschedule email template by RESPONDENT_ID
   - conversation()    >>>  generate pre-conversation information (rID, pID, topic_code, topics)

#######################################

''')
