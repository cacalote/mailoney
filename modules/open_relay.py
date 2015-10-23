__author__ = '@awhitehatter'

'''
Open relay module, will dump emails into a message log file

Thanks to:
https://djangosnippets.org/snippets/96/
https://muffinresearch.co.uk/fake-smtp-server-with-python/ (@muffinresearch)
'''

import sys
import os
import asyncore
from smtpd import SMTPServer
from database import Database

db = Database()

def or_module():

    class OpenRelay(SMTPServer):

        def process_message(self, peer, mailfrom, rcpttos, data):
            # Write to db
            db_add = db.add_email(peer[0], rcpttos[0], mailfrom, data)

    def run():
        sys.path.append("../")
        import mailoney

        honeypot = OpenRelay((mailoney.bind_ip, mailoney.bind_port), None)
        print '[*] Mail Relay listening on {}:{}'.format(mailoney.bind_ip, mailoney.bind_port)
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            print 'Detected interruption, terminating...'
    run()
