###############################################
############### DEPENDENCIES ##################

import pandas as pd

from datetime import datetime, timedelta
from pytz import timezone
from ics import Calendar, Event
from time import sleep
from termcolor import colored
import os

pd.options.mode.chained_assignment = None

###############################################
print('')
path = input(">>> Press ENTER for default schedule, or 'test' for testing:  ")

if path == 'test':
    file_path = 'emails_test'
    sleep(1)
    print(colored('>>> Testing mode: ON!', attrs=['bold']))
    print('')
    sleep(1)

else:
    file_path = 'Week 14 - schedule'
    sleep(1)
    print(colored(f'>>> Operating on {file_path}...', attrs=['bold']))
    print('')
    sleep(1)
    print(colored('Schedule last updated:', attrs=['underline']))
    timestamp = os.system(f'stat -f "%SB" "{file_path}.csv"') # prints the file's timestamp to stdout
    sleep(2)

df = pd.read_csv(file_path + '.csv')

df.columns = list(df.iloc[0])
df.drop(0, axis=0, inplace=True)

us_tzs = {'1': 'US/Pacific', '2': 'US/Mountain', '3': 'US/Central', '4': 'US/Eastern'}

###############################################

class Participant:

    def __init__(self, RESPONDENT_ID):
        
        # pd.Series object containing participant information
        self.df = df.loc[df.RESPONDENT_ID == RESPONDENT_ID].iloc[0]

        # main participant information
        self.rID = RESPONDENT_ID
        self.email = self.df.email
        self.pID = self.df.participant_id
        self.name = self.df['participant name']
        self.party = self.df.inparty
        self.timezone = self.df.timezone
        self.zoom = self.df.zoom_main

        # participant's session information
        self.day_week = self.df.day_week
        self.date = self.df.date
        self.time = self.df.time_PT
        self.topics = self.df.topics
        self.topic_code = self.df.topic_code
        self.moderator = self.df.moderator
        self.adj_t = None                   # to be added later in the "construct_session" function

    def __repr__(self):
        return f"Participant(rID={self.rID}, email={self.email})"

    @staticmethod
    def get_data():
        return globals()['df']

    @staticmethod
    def filter_schedule(day=None, t=None, confirm=None):
        """
        day: day_week value (e.g. 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')
        t: time_PT value (e.g. 8:00 AM)
        confirm: confirmed? value (e.g. 'no', 'yes', 'RES')
        
        if no argument is passed, returns "schedule"
        """
        filtered_df = Participant.get_data()
            
        if day is not None: filtered_df = filtered_df.loc[df.day_week == day] 

        if t is not None: filtered_df = filtered_df.loc[df.time_PT == t]

        if confirm is not None: filtered_df = filtered_df.loc[df['confirmed?'] == confirm] 

        return filtered_df

    def salutation(self):
        if type(self.name)== float:
            return 'Hi'
        else:
            return f'Hi {self.name}'

    def construct_session(self):
        session_str = self.day_week + ' ' + self.date + ' ' + self.time
        
        read_format = "%A %m/%d/%Y %I:%M %p"
        output_format = "%A, %B %-d, at %-I:%M %p (%Z)"

        p_session = datetime.strptime(session_str, read_format)
        tz_adj = p_session.astimezone(timezone(us_tzs[self.timezone]))
        
        self.adj_t = tz_adj  # sets the 'adj_t' attribute for each participant
        
        return tz_adj.strftime(output_format)

    def create_event(self):
        calendar, event = Calendar(), Event()
        
        event.name = f'Conversation Study ({self.adj_t.strftime("%-I%p %Z")})'
        event.organizer = 'conversationstudyssnl@gmail.com'
        event.begin = self.adj_t
        event.end = event.begin + timedelta(hours=1)
        event.url = self.zoom

        event.description = f"""- Zoom link: {self.zoom}
- Your participant ID: {self.pID}
        """
        
        calendar.events.add(event)
        
        ics_format = self.adj_t.strftime("%b_%-d_%-I%p_%Z")
        with open(f'conversation_{ics_format}.ics', 'w') as invite:
            invite.writelines(calendar.serialize_iter())

        return f'conversation_{ics_format}.ics'