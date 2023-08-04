from emails import Emails
from participants import Participant

from time import sleep
from termcolor import colored

def run():

    print(f'''
#######################################

{colored("Here is a list of available functions:", attrs=["bold"])}

{colored("Invite:", attrs=["underline"])}

   - rID_invite       >>>  send invitation email by RESPONDENT_ID
   - mass_invite      >>>  send invitation emails to each participant for a given day (e.g. Monday, Tuesday, etc.)
   - send_zoom        >>>  send Zoom link, participant_id, and calendar event after confirmation
   - confirmation     >>>  send confirmation email after participants confirm their conversation time


{colored('Reminder:', attrs=["underline"])}

   - rID_reminder     >>>  send reminder email by RESPONDENT_ID
   - reminder_1hr     >>>  send the 1-hr reminder email by RESPONDENT_ID
   - reminder_24hr    >>>  send the 24-hr reminder for confirmed participants by day_week (e.g. Monday)
   - noreply          >>>  re-send invitation as a reminder for non-confirmed participants


{colored("Other:", attrs=["underline"])}

   - reschedule       >>>  send the reschedule email template by RESPONDENT_ID
   - reschedule_day   >>>  send the reschedule emails by RESPONDENT_ID for a day (e.g. Monday)
   - reschedule_nw    >>>  send the rescheduling email for next week
   - conv_old         >>>  generate pre-conversation information (rID, pID, topic_code, topics)
   - conversation     >>>  generate pre-conversation information by slot (e.g. Monday-8:00 AM)
   - payment          >>>  send payment email to Rick with day_week as user input

#######################################
''')

    while True:

        print('')
        func = input(">>> What would you like to do?  ")
        print('')
        
        if str(func) == 'quit':
            sleep(1)
            print(colored('>>> Okay! Quitting now...', attrs=['bold']))
            print('')
            sleep(1)
            quit()

        elif str(func) == 'noreply':
            Emails.noreply()
        
        elif str(func) == 'rID_invite':
            Emails.rID_invite()

        elif str(func) == 'payment':
            Emails.payment()

        elif str(func) == 'confirmation':
            Emails.confirmation()

        elif str(func) == 'mass_invite':
            Emails.mass_invite()

        elif str(func) == 'send_zoom':
            Emails.send_zoom()

        elif str(func) == 'rID_reminder':
            Emails.rID_reminder()

        elif str(func) == 'reminder_1hr':
            Emails.reminder_1hr()

        elif str(func) == 'reminder_24hr':
            Emails.reminder_24hr()

        elif str(func) == 'reschedule':
            Emails.reschedule()

        elif str(func) == 'conversation':
            Emails.conversation()

        elif str(func) == 'conv_old':
            Emails.conv_old()

        elif str(func) == 'payment':
            Emails.payment()

        elif str(func) == 'reschedule_nw':
            Emails.reschedule_nw()

        elif str(func) == 'reschedule_day':
            Emails.reschedule_day()
            
        else: 
            print('The function you are looking for does not exist at the moment!')
            continue
        
        print('')
        print('#######################################')
        print('')
        cont = input(">>> Any other functions you would like to run? [y/n]  ")
        if cont.lower() == 'n':
            break
        
        continue

#######################################

if __name__ == "__main__":

    run()