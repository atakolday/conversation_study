#######################################
########### DEPENDENCIES ##############

from tqdm import tqdm
from termcolor import colored
import os
from dateutil.parser import parse
from time import sleep
import webbrowser
import pandas as pd

############### Emails ################

import smtplib, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#######################################

from Auth import SSNLAuth  # custom .py file with email address and app access password

from participants import Participant  # participants.py containing the parent 'Participants' class.


########################################

class Emails(Participant):
    email_from = SSNLAuth().EMAIL
    password = SSNLAuth().PASS

    @staticmethod
    def payment():

        print('')
        complete_check = input("Did you download the latest schedule .csv file? [y/n]  ")
        reschedule_check = input("Did you download the latest reschedules sheet? [y/n]  ")
        if (reschedule_check == 'n') or (complete_check == 'n'):
            print('')
            print('>>> Sounds like you definitely should! Download the most recent file(s) and come back.')
            sleep(1)
            print(colored('>>> Quitting now...', attrs=['bold']))
            print('')
            sleep(1)
            quit()

        ####################################
        print('')
        day = input("Alright then! For what day of the week would you like to send the payment email? (e.g. Monday)  ")

        df = Participant.filter_schedule(day=day)
        complete_df = df.loc[df.pair.notnull()]

        if len(df.index) != 0:

            complete_rID = list(complete_df.RESPONDENT_ID)
            complete_str = ""
            for s in complete_rID:
                complete_str += '<p dir="ltr"> - ' + s + '</p>'

            complete = '<p dir="ltr"><u>Participants who need to be paid $20</u>:</p>' + complete_str

        else:

            complete = ''

        ####################################

        res = pd.read_csv('Reschedules - Sheet1.csv')
        w_ix = res.loc[res.RESPONDENT_ID == 'WEEK 14'].index[0]  # index of the row that contains the WEEK 10 header

        res_week = res.loc[w_ix + 1:]  # splice the DataFrame to only show the rows for the designated week
        res_df = res_week.loc[
            res_week['original session day'] == day]  # reschedule sheet rows for the designated day (user input)

        if len(res_df.index) != 0:

            res_rID = list(res_df.RESPONDENT_ID)
            res_str = ""
            for rid in res_rID:
                res_str += '<p dir="ltr"> - ' + rid + '</p>'

            reschedule = '<p dir="ltr"><u>Participants who need to be paid $3</u>:</p>' + res_str

        else:

            reschedule = ''

        ####################################

        email_to = 'rkonopka@bovitzinc.com'

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()

        email_message['From'] = Emails.email_from
        email_message['To'] = email_to
        email_message['Subject'] = f'Participant Payments ({(df.date.iloc[0])[:-5]})'

        # Define the HTML document
        html = f'''
            <html>
                <body>
                    <p dir="ltr">Hi Rick, <br>
                                &nbsp;</p> 
                    <p dir="ltr">Hope you are doing well. </p>
                    <p dir="ltr">Below, are the RESPONDENT_IDs from {(df.date.iloc[0])[:-5]}.</p>
                    <p dir="ltr">&nbsp;</p>                        
                    {complete}
                    <p dir="ltr">&nbsp;</p> 
                    {reschedule}
                    <p dir="ltr">&nbsp;</p>
                    <p dir="ltr">Best,</p>
                    <p dir="ltr">Ata</p>
                </body>
            </html>
            '''
        ####################################

        # Attach HTML
        email_message.attach(MIMEText(html, "html"))

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(Emails.email_from, Emails.password)
            server.sendmail(Emails.email_from, email_to, email_message.as_string())

        print('')
        print(colored(f'>>> Payment email for {day} has been successfully sent.', attrs=['bold']))
        sleep(1)
        print('')

    @staticmethod
    def confirmation():
        """
        Send confirmation email after the participants confirm their session allocation.
        """

        df = Participant.filter_schedule(confirm='yes')  # main df for this function

        print('')
        check = input(colored(
            f" > Will be sending {len(df.index)} emails. Do you wish to proceed? [y/n]  ",
            attrs=['bold']))

        if check == 'n':
            print('')
            print(colored('>>> Alright, quitting now. Hope to see you soon!', attrs=['bold']))
            sleep(1)
            quit()

        else:

            count = 0
            for i in tqdm(list(df.RESPONDENT_ID), desc=' > Sending invitation emails'):
                # for i in list(df.RESPONDENT_ID):

                p = Participant(i)

                email_to = p.email  # email recipient

                # Create a MIMEMultipart class, and set up the From, To, Subject fields
                email_message = MIMEMultipart()
                email_message['From'] = Emails.email_from
                email_message['To'] = email_to
                email_message['Subject'] = 'Confirmation: Part II Conversation Study (45min for $20)'

                # Define the HTML document
                html = f'''
                    <html>
                        <body>
                            <p dir="ltr">{p.salutation()},</p>
                            <p dir="ltr">&nbsp;</p>                        
                            <p dir="ltr">Thank you so much for confirming!&nbsp;</p>
                            <p dir="ltr">Your conversation is set for <strong>{p.construct_session()}</strong>.&nbsp;</p>
                            <p dir="ltr">&nbsp;</p>
                            <p dir="ltr">You will receive further instructions, including your participant ID number and the Zoom link for your session, approximately one hour before your session's start time.&nbsp;</p>
                            <p dir="ltr"><strong>Please plan to arrive two minutes early.</strong> This study should take no more than 45 minutes to complete and you will be paid $20 dollars for your participation.&nbsp;</p>
                            <p dir="ltr">&nbsp;</p>
                            <p dir="ltr">Looking forward to seeing you soon!</p>
                            <p dir="ltr">-- The Research Team</p>
                        </body>
                    </html>
                    '''
                ####################################

                # Attach HTML
                email_message.attach(MIMEText(html, "html"))

                # Connect to the Gmail SMTP server and Send Email
                try:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(Emails.email_from, Emails.password)
                        server.sendmail(Emails.email_from, email_to, email_message.as_string())

                    count += 1

                except Exception as e:
                    print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))
                    print('')
                    raise e

            if count == len(df.index):
                print(colored(f" > TASK COMPLETED WITH {count} SUCCESSFUL ITERATIONS!", attrs=['bold']))
                print('')

    @staticmethod
    def conversation(time_PT=None):

        if time_PT is None:
            slot = input("For which time slot would you like to launch the conversation? (e.g. Monday-8:00 AM)  ")
            dw, t = slot.split('-')

        else:
            dw, t = time_PT.split('-')

        data = Participant.filter_schedule(str(dw), str(t), 'yes')  # main df for this function

        mod = input("For which moderator?  ")
        if mod == "":
            df = data.loc[data.moderator == 'Ata'].reset_index(drop=True)

        else:
            if str(mod) not in list(data.groupby('moderator').size().index):
                print(colored("  >> This is not the moderator you're looking for. Move along.", attrs=['bold']))

            else:
                df = data.loc[data.moderator == str(mod)].reset_index(drop=True)

        if len(df.index) != 2:
            print('There is no distinct pair for you in this slot, check again!')

        else:
            p1 = Participant(df.iloc[0].RESPONDENT_ID)
            p2 = Participant(df.iloc[1].RESPONDENT_ID)

            if p1.topic_code != p2.topic_code:
                print('')
                print('Uh oh! The topic codes for the participants do not match!')
                print('')

            else:
                mo, day = (parse(p1.date).strftime('%b %-d')).split(' ')
                t, am_pm = p1.time.split(' ')

                path = f'conversation_notes/{mo}_{day}_{t.split(":")[0] + am_pm}.txt'

                with open(path, 'w') as f:
                    f.write(f"""Conversation - {p1.day_week}, {parse(p1.date).strftime('%b %-d')}, at {p1.time} (Pacific Time)


Participant #1
    >> Name: {p1.name}
    >> Email: {p1.email}
    >> rID: {p1.rID}
    >> pID: {p1.pID}
    >> Party: {p1.party}

Participant #2
    >> Name: {p2.name}
    >> Email: {p2.email}
    >> rID: {p2.rID}
    >> pID: {p2.pID}
    >> Party: {p2.party}   

>> Topic Code: {p1.topic_code}
>> Topics: {p1.topics}


{(p1.topics).split('_')[0]}:
    - 
    - 
    - 

{(p1.topics).split('_')[1]}:
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
                    sleep(1)
                    print(colored('  > Launching the conversation script...', attrs=['bold']))
                    sleep(1)
                    webbrowser.open_new(
                        'https://docs.google.com/document/d/1y_D4BBU_1-v-zBCijy0jSVi4advDEP9t2n2TyD8Ca0A/edit')

                    print('')
                    sleep(1)
                    print(colored('  > Launching Zoom meeting...', attrs=['bold']))
                    sleep(1)
                    print('')
                    webbrowser.open(f'{p1.zoom}')

                    sleep(1)
                    print(colored('  > Launching the timer...', attrs=['bold']))
                    print('')
                    sleep(1)
                    os.system("open /System/Applications/Clock.app")

                finished = input(" >> Was the study successfully completed? [y/n]  ")
                if finished == 'n':
                    pass

                elif finished == 'y':
                    print('')
                    sleep(1)
                    print(colored('  > Creating the completed sesssion rows...', attrs=['bold']))
                    print('')
                    sleep(1)
                    conv_df = pd.DataFrame({
                        'participant_id': [p1.pID, p2.pID],
                        'emails': [p1.email, p2.email],
                        'pair': "",
                        'topics': p1.topics,
                        'code': p1.topic_code,
                        'name': [p1.name, p2.name],
                        'RESPONDENT_ID': [p1.rID, p2.rID],
                        'topic1': "",
                        'topic2': ""
                    })

                    path = f'conversation_notes/{mo}_{day}_{t.split(":")[0] + am_pm}.csv'

                    conv_df.to_csv(path, index=False)

                    os_str = f"open /Applications/Numbers.app {path}"

                    os.system(os_str);

                    survey = input(' >> Would you like to launch the post-completion survey? [y/n]  ')
                    if survey == 'y':

                        webbrowser.open('https://stanforduniversity.qualtrics.com/jfe/form/SV_2h0cqfvzxTlg01U')

                    else:
                        pass

    @staticmethod
    def conv_old():

        p1_input = input("What is Participant 1's RESPONDENT_ID? ")
        p2_input = input("What is Participant 2's RESPONDENT_ID? ")

        p1 = Participant(p1_input)
        p2 = Participant(p2_input)

        if p1.topic_code != p2.topic_code:
            print('')
            print('Uh oh! The topic codes for the participants do not match!')
            print('')

        else:
            mo, day = (parse(p1.date).strftime('%b %-d')).split(' ')
            t, am_pm = p1.time.split(' ')

            path = f'conversation_notes/{mo}_{day}_{t.split(":")[0] + am_pm}.txt'

            with open(path, 'w') as f:
                f.write(f"""Conversation - {p1.day_week}, {parse(p1.date).strftime('%b %-d')}, at {p1.time} (Pacific Time)


Participant #1
    >> Name: {p1.name}
    >> Email: {p1.email}
    >> rID: {p1.rID}
    >> pID: {p1.pID}
    >> Party: {p1.party}

Participant #2
    >> Name: {p2.name}
    >> Email: {p2.email}
    >> rID: {p2.rID}
    >> pID: {p2.pID}
    >> Party: {p2.party}   

>> Topic Code: {p1.topic_code}
>> Topics: {p1.topics}


{(p1.topics).split('_')[0]}:
    - 
    - 
    - 

{(p1.topics).split('_')[1]}:
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
                sleep(1)
                print(colored('Launching Zoom meeting...', attrs=['bold']))
                print('')

                webbrowser.open(f'{p1.zoom}')

            finished = input(" >> Was the study successfully completed? [y/n]  ")
            if finished == 'n':
                pass

            elif finished == 'y':
                conv_df = pd.DataFrame({
                    'participant_id': [p1.pID, p2.pID],
                    'emails': [p1.email, p2.email],
                    'pair': "",
                    'topics': p1.topics,
                    'code': p1.topic_code,
                    'name': [p1.name, p2.name],
                    'RESPONDENT_ID': [p1.rID, p2.rID],
                    'topic1': "",
                    'topic2': ""
                })

                path = f'conversation_notes/{mo}_{day}_{t.split(":")[0] + am_pm}.csv'

                conv_df.to_csv(path, index=False)

                os_str = f"open /Applications/Numbers.app {path}"

                os.system(os_str);

                survey = input(' >> Would you like to launch the post-completion survey? [y/n]  ')
                if survey == 'y':

                    webbrowser.open('https://stanforduniversity.qualtrics.com/jfe/form/SV_2h0cqfvzxTlg01U')

                else:
                    pass

    @staticmethod
    def rID_invite():

        while True:

            id = input("What is the RESPONDENT_ID?  ")

            p = Participant(id)

            # Create a MIMEMultipart class, set up the From, To, and Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = Emails.email_from
            email_message['To'] = p.email
            email_message['Subject'] = 'Invitation: Part II Conversation Study (45min for $20) -- Action Required'

            # Define the HTML document
            html = f'''
                <html>
                    <body>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                        <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                        <p>&nbsp;</p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{p.construct_session()}.</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><strong><span style="font-family: arial, sans-serif; color: #ff0000;"><span style="font-family: arial, sans-serif;">It is very important that you confirm at least 24hrs before your appointment to prevent your time slot from being canceled.</span></span></strong><span style="font-family: arial, sans-serif;">&nbsp;This study involves coordination with multiple participants. We want to be respectful of everyone&rsquo;s time.</span></span></p>
                        <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">After you confirm your appointment, we will follow up with instructions with how to join the study at your set day and time.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                        <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">As mentioned in the survey, this part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                        <p>&nbsp;</p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Reminder: this part of the study should not take more than 45 minutes, and you will be paid $20 dollars for your participation.</span></span></p>
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
                server.login(Emails.email_from, Emails.password)
                server.sendmail(Emails.email_from, p.email, email_message.as_string())

            print('')
            print(f' >> Email to {p.email} successfully sent!')
            print('')

            ###########################################################################

            cont = input("Would you like to continue? [y/n] ")
            if cont == 'n':
                break
            continue

    @staticmethod
    def noreply():

        day = input('For what day of the week would you like to send the invitation reminders?  ')

        data = Participant.get_data()
        df = data.loc[data.day_week == str(day)]
        df = df.loc[df['confirmed?'].isna()].reset_index(drop=True)

        print('')
        check = input(colored(
            f" > Will be sending {len(df.index)} invitation reminders for {day}. Do you wish to proceed? [y/n]  ",
            attrs=['bold']))

        if check == 'n':
            print('')
            print(colored('>>> Alright, quitting now. Hope to see you soon!', attrs=['bold']))
            sleep(1)
            quit()

        else:
            ################### Sending the emails ######################
            count = 0  # counter for successful iterations of function

            print('')
            for i in tqdm(list(df.RESPONDENT_ID), desc=' > Sending invitation emails'):

                # Create a Participant object
                p = Participant(i)

                email_to = p.email  # email recipient

                # Create a MIMEMultipart class, and set up the From, To, Subject fields
                email_message = MIMEMultipart()
                email_message['From'] = Emails.email_from
                email_message['To'] = email_to
                email_message['Subject'] = 'REMINDER: Part II Conversation Study (45min for $20) -- Action Required'

                # Define the HTML document
                html = f'''
                <html>
                    <body>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                        <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{p.construct_session()}.</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
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
                        server.login(Emails.email_from, Emails.password)
                        server.sendmail(Emails.email_from, email_to, email_message.as_string())

                        count += 1

                except Exception as e:
                    print(colored(f'>>> ERROR! <<<', attrs=['bold']))
                    print(colored(f'>>> {count} OUT OF {len(df.index)} EMAILS SENT! <<<', attrs=['bold']))

            if count == len(df.index):
                print(colored(f" > ALL {count} EMAILS SUCCESSFULLY SENT!", attrs=['bold']))
                print('')
                sleep(1)
                print(colored(f">>> Quitting now to avoid the SMTP disconnect...", attrs=['bold']))
                print('')
                sleep(1)
                quit()

    @staticmethod
    def mass_invite():

        day = input('For what day of the week would you like to send the invitation emails?  ')

        data = Participant.get_data()
        df = data.loc[data.day_week == str(day)].reset_index(drop=True)

        if len(df.index) == 0:
            print('')
            print(colored(f'>>> There are no conversations scheduled for {day}!', attrs=['bold']))
            sleep(1)
            print(colored('>>> Check again and come back. Quitting now...', attrs=['bold']))
            print('')
            sleep(1)
            quit()


        print('')
        check = input(colored(
            f" > Will be sending {len(df.index)} emails for {day}'s participants. Do you wish to proceed? [y/n]  ",
            attrs=['bold']))

        if check == 'n':
            print('')
            print(colored('>>> Alright, quitting now. Hope to see you soon!', attrs=['bold']))
            sleep(1)
            quit()

        else:
            ################### Sending the emails ######################
            count = 0  # counter for successful iterations of function

            print('')
            for i in tqdm(list(df.RESPONDENT_ID), desc=' > Sending invitation emails'):

                # Create a Participant object
                p = Participant(i)

                email_to = p.email  # email recipient

                # Create a MIMEMultipart class, and set up the From, To, Subject fields
                email_message = MIMEMultipart()
                email_message['From'] = Emails.email_from
                email_message['To'] = email_to
                email_message['Subject'] = 'Invitation: Part II Conversation Study (45min for $20) -- Action Required'

                # Define the HTML document
                html = f'''
                <html>
                    <body>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                        <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{p.construct_session()}.</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
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
                        server.login(Emails.email_from, Emails.password)
                        server.sendmail(Emails.email_from, email_to, email_message.as_string())

                        count += 1

                except Exception as e:
                    print(colored(f'>>> ERROR! <<<', attrs=['bold']))
                    print(f'>>> EMAIL TO {p.__repr__()} COULD NOT BE SENT.')
                    print('')
                    print(colored(f'>>> {count} OUT OF {len(df.index)} EMAILS SENT! <<<', attrs=['bold']))

            if count == len(df.index):
                print(colored(f" > ALL {count} EMAILS SUCCESSFULLY SENT!", attrs=['bold']))
                print('')
                sleep(1)
                print(colored(f">>> Quitting now to avoid the SMTP disconnect...", attrs=['bold']))
                print('')
                sleep(1)
                quit()

    @staticmethod
    def send_zoom():

        print('')

        slot = input("For what slot would you like to send the Zoom links? (e.g. Monday-8:00 AM)  ")

        dw, t = slot.split('-')
        df = Participant.filter_schedule(str(dw), str(t), 'yes').reset_index(drop=True)

        print('')

        count = 0
        for i in tqdm(list(df.RESPONDENT_ID), desc=' > Sending invitation emails'):
            # for i in list(df.RESPONDENT_ID):

            p = Participant(i)

            email_to = p.email  # email recipient

            # Create a MIMEMultipart class, and set up the From, To, Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = Emails.email_from
            email_message['To'] = email_to
            email_message['Subject'] = 'Session Information: Part II Conversation Study (45min for $20)'

            # Create the HTML document
            html = f'''
                <html>
                    <body>
                        <p dir="ltr"><span style="font-size: medium;">{p.salutation()},</span></p>
                        <p dir="ltr"><span style="font-size: medium;">Thank you so much for confirming.</span></p>
                        <p dir="ltr"><span style="font-size: medium;">This is just a reminder that your conversation is set to start on&nbsp;<strong>{p.construct_session()}.</strong></span></p>
                        <p dir="ltr"><span style="font-size: medium;">  - During the conversation, you will need your participant ID. Your participant ID is&nbsp;<strong>{p.pID}</strong>.</span></p>
                        <p dir="ltr"><span style="font-size: medium;">  - <strong>Attached, we are also sending you a calendar invitation for your convenience.</strong> If you choose to do so, you can click on this attachment (ending in .ics) and your conversation date and time will be automatically added to your default calendar application (e.g. Apple iCal, Google Calendar, etc.) as a calendar event.</span></p>
                        <p dir="ltr"><span style="font-size: medium;">&nbsp;</span></p>
                        <p dir="ltr"><span style="text-decoration: underline; font-size: medium;"><strong>Instructions</strong></span></p>
                        <p dir="ltr"><span style="font-size: medium;">This part of the study will involve reading an article, talking to another participant over Zoom, and answering some survey questions. In preparation for the conversation part of this study, <strong>make sure your computer camera and your microphone are working before your meeting day.</strong> You will need a quiet room with few distractions for the duration of this study.</span></p>
                        <p dir="ltr"><span style="font-size: medium;">On your appointment day, <strong>click on the Zoom link below two minutes before your scheduled time.</strong></span></p>
                        <p dir="ltr"><span style="font-size: medium;">You don't need to install any extra software to join a Zoom meeting. You can do it all through a web browser. You just need to:</span></p>
                        <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp;<strong>Click on the meeting link</strong>: {p.zoom}</span></p>
                        <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; A new tab will open on your web browser. If you don't have the Zoom desktop app installed, the page will urge you to download the app. <strong>You can ignore that message and click on:"Join from your Browser" (as shown below)</strong></span></p>
                        <p><span style="font-size: medium;">&nbsp;</span></p>
                        <img src='cid:myimageid' width="700">
                        <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; A pop-up window will appear asking you to give Zoom permission to access your camera and microphone. <strong>Click on &ldquo;allow&rdquo;.</strong></span></p>
                        <p dir="ltr"><span style="font-size: medium;">&nbsp; &nbsp; &nbsp;- &nbsp; You will be asked for your name. <strong>Please only provide your first (or preferred) name. Do not type your last name.</strong></span></p>
                        <p dir="ltr"><span style="font-size: medium;">A moderator will be in the Zoom room to greet you. They will explain the study in more detail, guide you and your conversation partner through the conversation and share a survey link with you.</span></p>
                        <p dir="ltr"><span style="font-size: medium;">Reminder: this part of the study should not take more than <strong>45 minutes</strong> and you will be paid $20 dollars for your participation.</span></p>
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
            def attach_file_to_email(email_message, filename, extra_headers=None):

                # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
                with open(filename, "rb") as f:
                    file_attachment = MIMEApplication(f.read())

                # Add header/name to the attachments
                file_attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}", )

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

            # Attach .ics file
            cal_event = p.create_event()
            attach_file_to_email(email_message, cal_event)

            # Connect to the Gmail SMTP server and Send Email
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(Emails.email_from, Emails.password)
                    server.sendmail(Emails.email_from, email_to, email_message.as_string())

                    # print('')
                    # print(f'Email to {email_to} successfully sent!')
                    # print('')

                os.remove(cal_event)

                count += 1

            except Exception as e:
                print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))

        if count == len(df.index):
            print(colored(f" > TASK COMPLETED WITH {count} SUCCESSFUL ITERATIONS!", attrs=['bold']))
            print('')

    @staticmethod
    def reschedule():

        while True:

            rID = input('What is the RESPONDENT_ID? ')

            if rID not in list(Participant.get_data().RESPONDENT_ID):
                print("This participant does not exist!")
                continue

            p = Participant(rID)

            ###########################################################################

            email_to = p.email  # email recipient

            # Create a MIMEMultipart class, and set up the From, To, Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = Emails.email_from
            email_message['To'] = email_to
            email_message['Subject'] = 'Reschedule: Part II Conversation Study (45min for $20)'

            # Define the HTML document
            html = f'''
                <html>
                    <body>
                        <p dir="ltr">{p.salutation()},</p>
                        <p dir="ltr">&nbsp;</p>
                        <p dir="ltr">Unfortunately, your conversation partner can no longer attend your scheduled session. There may be other available time slots for later in the week. Would you be willing to reschedule?&nbsp;</p>
                        <p dir="ltr">If you are willing to reschedule, please let us know and we can share our availability with you.&nbsp;</p>
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
                server.login(Emails.email_from, Emails.password)
                server.sendmail(Emails.email_from, email_to, email_message.as_string())

            print('')
            print(f' >> Email to {email_to} successfully sent!')
            print('')

            ###########################################################################

            cont = input("Any more rescheduling emails to send? [y/n] ")
            if cont == 'n':
                break
            continue

    @staticmethod
    def reschedule_nw():

        while True:

            rID = input('What is the RESPONDENT_ID? ')

            if rID not in list(Participant.get_data().RESPONDENT_ID):
                print("This participant does not exist!")
                continue

            p = Participant(rID)

            ###########################################################################

            email_to = p.email  # email recipient

            # Create a MIMEMultipart class, and set up the From, To, Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = Emails.email_from
            email_message['To'] = email_to
            email_message['Subject'] = 'Reschedule: Part II Conversation Study (45min for $20)'

            # Define the HTML document
            html = f'''
                <html>
                    <body>
                        <p dir="ltr">{p.salutation()},&nbsp;</p>
                        <p dir="ltr">Unfortunately, your conversation partner can no longer attend your scheduled session. There may be other available time slots for next week. Would you be willing to reschedule?&nbsp;</p>
                        <p dir="ltr">If you are willing to reschedule, please let us know.&nbsp;</p>
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
                server.login(Emails.email_from, Emails.password)
                server.sendmail(Emails.email_from, email_to, email_message.as_string())

            print('')
            print(f' >> Email to {email_to} successfully sent!')
            print('')

            ###########################################################################

            cont = input("Any more rescheduling emails to send? [y/n] ")
            if cont == 'n':
                break
            continue

    @staticmethod
    def reschedule_day():

        day = input("For what day of the week would you like to send rescheduling emails?  ")
        data = Participant.get_data()
        df = data.loc[(data.day_week == day) & (data['confirmed?'] == 'RES')]

        print('')
        check = input(colored(
            f" > Will be sending {len(df.index)} rescheduling emails for {day}'s participants. Do you wish to proceed? [y/n]  ",
            attrs=['bold']))
        print('')

        if check == 'n':

            print('')
            print(colored('>>> Alright, quitting now. Hope to see you soon!', attrs=['bold']))
            sleep(1)
            quit()

        else:

            count = 0
            for i in tqdm(list(df.RESPONDENT_ID), f'Sending rescheduling emails for {day}'):

                p = Participant(i)

                ###########################################################################

                email_to = p.email  # email recipient

                # Create a MIMEMultipart class, and set up the From, To, Subject fields
                email_message = MIMEMultipart()
                email_message['From'] = Emails.email_from
                email_message['To'] = email_to
                email_message['Subject'] = 'Reschedule: Part II Conversation Study (45min for $20)'

                # Define the HTML document
                html = f'''
                    <html>
                        <body>
                            <p dir="ltr">{p.salutation()},&nbsp;</p>
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
                try:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(Emails.email_from, Emails.password)
                        server.sendmail(Emails.email_from, email_to, email_message.as_string())

                    count += 1

                except Exception as e:
                    print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))
                    print(f'>>> EMAIL TO {p.__repr__()} COULD NOT BE SENT.')
                    raise e

            if count == len(df.index):
                print(colored(f"  > All {count} rescheduling emails for {day} successfully sent!", attrs=['bold']))
                print('')

    @staticmethod
    def reminder_24hr():

        day = input('For what day of the week would you like to send the reminder emails?  ')

        df = Participant.filter_schedule(str(day), confirm='yes')

        ################### SENDING THE EMAIL ######################

        print('')
        check = input(colored(
            f" > Will be sending {len(df.index)} emails for {day}'s participants. Do you wish to proceed? [y/n]  ",
            attrs=['bold']))

        if check == 'n':
            print('')
            print(colored('>>> Alright, quitting now. Hope to see you soon!', attrs=['bold']))
            sleep(1)
            quit()

        else:

            count = 0  # counter for successful iterations of function

            print('')
            for i in tqdm(list(df.RESPONDENT_ID), desc='Sending invitation emails'):

                p = Participant(i)

                email_to = p.email  # email recipient

                # Create a MIMEMultipart class, and set up the From, To, Subject fields
                email_message = MIMEMultipart()
                email_message['From'] = Emails.email_from
                email_message['To'] = email_to
                email_message['Subject'] = 'REMINDER: Part II Conversation Study (45min for $20)'

                # Define the HTML document
                html = f'''
                    <html>
                        <body>
                            <p dir="ltr">{p.salutation()},<br>
                                         &nbsp;</p> 
                            <p dir="ltr">This is a reminder that your conversation is coming up tomorrow!&nbsp;</p>
                            <p dir="ltr">Your conversation is set for <strong>{p.construct_session()}</strong>.&nbsp;</p>
                            <p dir="ltr">&nbsp;</p>
                            <p dir="ltr">You will receive further instructions, including your participant ID number and the Zoom link for your session, approximately one hour before your session's start time.&nbsp;</p>
                            <p dir="ltr"><strong>Please plan to arrive two minutes early.</strong> This study should take no more than 45 minutes to complete and you will be paid $20 dollars for your participation.&nbsp;</p>
                            <p dir="ltr">&nbsp;</p>
                            <p dir="ltr">Looking forward to seeing you soon!</p>
                            <p dir="ltr">-- The Research Team</p>
                        </body>
                    </html>
                    '''
                # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
                email_message.attach(MIMEText(html, "html"))

                # Connect to the Gmail SMTP server and Send Email
                try:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(Emails.email_from, Emails.password)
                        server.sendmail(Emails.email_from, email_to, email_message.as_string())

                        count += 1

                except Exception as e:
                    print(colored(f'>>> ERROR! FUNCTION QUIT AFTER {count} ITERATIONS! <<<', attrs=['bold']))
                    print(f'>>> EMAIL TO {p.__repr__()} COULD NOT BE SENT.')
                    print('')

            if count == len(df.index):
                print(colored(f"  >> ALL {count} EMAILS SUCCESSFULLY SENT!", attrs=['bold']))
                print('')

    @staticmethod
    def reminder_1hr():

        slot = input("For which conversation slot would you like to send the 1-hr reminder? (e.g. Monday-8:00 AM)  ")
        dw, t = slot.split('-')

        df = Participant.filter_schedule(str(dw), str(t), 'yes').reset_index(drop=True)

        dem_count, rep_count = len(df.loc[df.inparty == 'Democrat'].index), len(df.loc[df.inparty == 'Republican'].index)

        if dem_count != rep_count:
            print('')
            cont = str(input(f'{colored(">> WARNING!!", attrs=["bold"])} The number of Dems ({dem_count}) and Reps ({rep_count}) in this slot do not match. Would you like to continue anyways? [y/n]  '))
            if cont == 'n':
                print('')
                print(f">>> Okay, quitting now!")
                sleep(1)
                quit()

        print('')  # console padding

        count = 0
        for i in tqdm(list(df.RESPONDENT_ID), desc=' > Sending 1-hr reminders'):
            p = Participant(i)
            p_session = p.construct_session()

            email_to = p.email  # email recipient

            # Create a MIMEMultipart class, and set up the From, To, Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = Emails.email_from
            email_message['To'] = email_to
            email_message['Subject'] = 'Reminder: Part II Conversation Study (45min for $20)'

            # Define the HTML document
            html = f'''
                <html>
                    <body>
                        <p dir="ltr">{p.salutation()},&nbsp;</p>
                        <p dir="ltr">Your conversation is set to start approximately one hour from now,{p_session.split(',')[2]} .&nbsp;</p>
                        <p dir="ltr">&nbsp;</p>
                        <p dir="ltr">Here are some reminders:&nbsp;</p>
                        <p dir="ltr">   - Your participant ID is <strong>{p.pID}</strong></p>
                        <p dir="ltr">   - Zoom link:</p>
                        <p dir="ltr"><strong>{p.zoom}</strong></p>
                        <p dir="ltr">&nbsp;</p>
                        <p dir="ltr">Please plan to arrive two minutes early. This study should take no more than 45 minutes to complete and you will be paid $20 dollars for your participation.&nbsp;</p>
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
                server.login(Emails.email_from, Emails.password)
                server.sendmail(Emails.email_from, email_to, email_message.as_string())

            count += 1

        if count == len(df.index):
            print(colored(f" > ALL {count} 1-HR REMINDERS SUCCESSFULLY SENT!", attrs=['bold']))
            print('')

        conv = input(">>> Would you like to initiate the conversation for this slot? [y/n]  ")
        if conv == 'y':
            Emails.conversation(time_PT=slot)

    @staticmethod
    def rID_reminder():

        while True:

            rID = input('What is the RESPONDENT_ID? ')

            if rID not in list(Participant.get_data().RESPONDENT_ID):
                print("This participant does not exist.")
                continue

            ###########################################################################

            p = Participant(rID)

            email_to = p.email  # email recipient

            # Create a MIMEMultipart class, and set up the From, To, Subject fields
            email_message = MIMEMultipart()
            email_message['From'] = Emails.email_from
            email_message['To'] = email_to
            email_message['Subject'] = 'REMINDER: Part II Conversation Study (45min for $20) -- Action Required'

            # Define the HTML document
            html = f'''
                <html>
                    <body>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Dear participant,</span></span></p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Thank you so much for agreeing to participate in the Conversation Study!</span></span></p>
                        <p><span style="font-size: medium;"><span style="font-family: arial, sans-serif;"><span style="font-family: arial, sans-serif;">Recently, you completed a survey (Part I) in which you shared your opinions on a variety of topics and provided your availability for the second part of this study. Congrats, now you are eligible to complete Part II of this study!</span></span><span style="font-family: arial, sans-serif;">&nbsp;</span></span></p>
                        <p>&nbsp;</p>
                        <p><span style="font-family: arial, sans-serif; font-size: medium;"><span style="font-family: arial, sans-serif;">Given your availability, your Part II is set to occur on&nbsp;<strong>{p.construct_session()}.</strong></span><span style="font-family: arial, sans-serif;"><strong>&nbsp;<span style="font-family: arial, sans-serif; color: #993300;">Please respond to this email with just the word &ldquo;CONFIRM&rdquo; to confirm your appointment. </span></strong>If you can no longer make this time, <strong>let us know as soon as possible </strong>by replying to this email<strong>.</strong></span></span></p>
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
                server.login(Emails.email_from, Emails.password)
                server.sendmail(Emails.email_from, email_to, email_message.as_string())

            print('')
            print(f' >> Email to {email_to} successfully sent!')
            print('')

            ###########################################################################

            cont = input("Would you like to continue? [y/n] ")
            if cont == 'n':
                break
            continue
