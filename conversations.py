##### IMPROVEMENT IDEAS #####

# - Asking who is accessing the program to filter out the schedule by moderator
#


##### ######

import pandas as pd
import numpy as np

from dateutil.parser import parse
from termcolor import colored

import webbrowser

### DEPENDENCIES AND WRANGLING ###

# Load Schedule Data

df = pd.read_csv('W4_schedule.csv')

# Reformat DataFrame

# df.reset_index().drop('index', axis=1)
#
# df.drop(79, axis=0, inplace=True) # DUPLICATE ROW
# My schedule

schedule = df.loc[df['moderator1'].str.contains("Ata", na=False)][[
    'day_week', 'date', 'time_PT',
    'RESPONDENT_ID', 'participant_id',
    'email', 'timezone', 'inparty',
    'topics', 'topic_code', 'zoom_main'
]]

# Convert timezone

# schedule = schedule.replace({'timezone': {
#     '1': 'Pacific',
#     '2': 'Mountain',
#     '3': 'Central',
#     '4': 'Eastern'
# }})

schedule['timezone'] = schedule['timezone'].map(lambda x: int(x) - 1)

schedule = schedule.reset_index().drop('index', axis=1)

### FUNCTIONS ###

def tzone(n):
    if n == 0:
        return "Pacific"
    elif n == 1:
        return "Mountain"
    elif n == 2:
        return "Central"
    elif n == 3:
        return "Eastern"

def adj_time(df=schedule):

    t, z = df['time_PT'][0], df['timezone'][0]

    time = int(t.split(':')[0])
    adj = time + z

    if adj == 12:
        adj_t = "12:00 PM"

    elif adj > 11:
        adj_t = "{}:00 PM".format(adj - 12)
    else:
        adj_t = "{}:00 AM".format(adj)

    return adj_t


def invite():

    while True:

        rID = input('What is the RESPONDENT_ID? ')

        if rID not in list(schedule.RESPONDENT_ID):
            print("This participant is not assigned to you. Please enter a valid RESPONDENT_ID!")
            continue

        else:
            pass

        df = schedule.loc[schedule.RESPONDENT_ID == str(rID)].reset_index().drop('index', axis=1)

        print('')
        print(colored(f'{df.email[0]}', attrs=['bold']))
        print('')
        print(colored('Invitation: Part II Conversation Study (1hr for $20) -- Action Required', attrs=['bold']))
        print(f'''
Dear participant,

Thank you so much for agreeing to participate in the Conversation Study!

Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!
''')
        print("Given your availability, your Part II is set to occur on " + colored(f"{df.day_week[0]}, {parse(df['date'][0]).strftime('%B %d')}, at {adj_time(df)} ({tzone(df.timezone[0])} Time).", attrs=['bold']) + colored(' Please respond to this email with just the word “CONFIRM” to confirm your appointment. If you can no longer make this time, let us know as soon as possible by replying to this email.', 'red', attrs=['bold']))

        print('')
        print(colored('It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.', 'red') + ' This study involves coordination with multiple participants. We want to be respectful of everyone’s time.')

        print('''
After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.

As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, make sure your computer camera and your microphone are working before your meeting day. You will need a quiet room with few distractions for the duration of this study.

Reminder: this part of the study will take 1-hour and you will be paid $20 dollars for your participation.

If you show up and, after 6 minutes, your conversation partner doesn’t, you will be paid $3 for your time and will be given the chance to reschedule.

We are very grateful for your participation, and we hope to see you soon!
    ''')

        print('''
All the best,
The Research Team
    ''')

        cont = input("Would you like to continue? [y/n] ")
        if cont == 'n':
            break
        else:
            continue

def confirmed():

    e_mail = input('What is the participant email? ')

    df = schedule.loc[schedule.email == str(e_mail)].reset_index().drop('index', axis=1)

    print(f'''
Hi,


Thank you so much for confirming.

This is just a reminder that your conversation is set to start ''' + colored(f"{df.day_week[0]}, {parse(df['date'][0]).strftime('%B %d')}, at {adj_time(df)} ({tzone(df.timezone[0])} Time).", attrs=['bold']))

    print('- This study will ask you for your participant ID. Your participant ID is ' + colored(f"{df.participant_id[0]}", attrs=['bold']))


def conversation(df):
    # Participant 1 INFO
    p1 = input("What is Participant 1's email? ")

    df_p1 = df.loc[df.email == p1].reset_index().drop('index', axis=1)
    print(colored('Participant #1', attrs=['bold', 'underline']))
    print(f'- rID: {df_p1.RESPONDENT_ID[0]}')
    print(f'- pID: {df_p1.participant_id[0]}')
    print(f'- Party: {df_p1.inparty[0]}')
    print('')

    # Participant 2 INFO
    p2 = input("What is Participant 2's email? ")

    df_p2 = df.loc[df.email == p2].reset_index().drop('index', axis=1)
    print(colored('Participant #2', attrs=['bold', 'underline']))
    print(f'- rID: {df_p2.RESPONDENT_ID[0]}')
    print(f'- pID: {df_p2.participant_id[0]}')
    print(f'- Party: {df_p2.inparty[0]}')

    print('')
    print('Launching Zoom meeting...')
    print('')
    webbrowser.open(f'{df_p2.zoom_main[0]}')

### CONSOLE ###

print('''

Available functions to generate emails:

- invite()          use for the initial invitation email.
- confirmed()       use after the participation is confirmed.
- conversation()    use for conversations.

''')
