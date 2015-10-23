__author__ = '@awhitehatter'

'''
Module supports the main project file.
'''

import socket
import threading
import sys
import os
from time import strftime
import base64
from database import Database
db = Database()

def pfserver():
    sys.path.append("../")
    import mailoney

    print mailoney.banner
    # moving this below to see if this fixes the reconnection error
    # server set up
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((mailoney.bind_ip, mailoney.bind_port))
    server.listen(10)

    # setup the Postfix EHLO Response
    ehlo = '250-{} Hello 127.0.0.1\n250-SIZE 10240000\n250 AUTH LOGIN PLAIN\n'.format(mailoney.srvname)

    #setup the Log File
    if os.path.exists('logs/credentials.log'):
        logfile = open('logs/credentials.log', 'a')
    else:
        logfile = open('logs/credentials.log', 'w')

    print ('[*] SMTP Server listening on {}:{}'.format(mailoney.bind_ip, mailoney.bind_port))

    def handle_client(client_socket):
        # Send banner
        client_socket.send('220 {} ESMTP Postfix\n'.format(mailoney.srvname))

        while True:

            # Setup a loop to communicate with the client
            count = 0
            while count < 10:
                try:
                    request = client_socket.recv(4096).lower()
                except socket.error:
                    break

                if 'ehlo' in request:
                    client_socket.send(ehlo)
                    break
                else:
                    try:
                        client_socket.send('502 5.5.2 Error: command not recognized\n')
                        count += 1
                    except socket.error:
                        count += 1
                        break

            #kill the client for too many errors
            if count == 10:
                client_socket.send('421 4.7.0 {} Error: too many errors\n'.format(mailoney.srvname))
                client_socket.close()
                break

            #reset the counter and hope for creds
            count = 0
            while count < 10:
                request = client_socket.recv(4096)
                if 'auth plain' in request.lower():
                    #pull the base64 string and validate
                    auth = request.split()[2]
                    remote_ip = addr[0]
                    decoded_auth = base64.b64decode(auth).split('\x00')
                    db.add_creds(remote_ip, decoded_auth[1], decoded_auth[2])
                    try:
                        client_socket.send('235 2.0.0 Authentication Failed\n')
                    except socket.error:
                        client_socket.close()
                        break

                elif 'exit' in request:
                    count = 10
                    break
                else:
                    try:
                        client_socket.send('502 5.5.2 Error: command not recognized\n')
                        count += 1
                    except socket.error:
                        count += 1

            #kill the connection for too many failures
            if count == 10:
                try:
                    client_socket.send('421 4.7.0 {} Error: too many errors\n'.format(mailoney.srvname))
                    client_socket.close()
                except socket.error:
                    break
                break

            # reset the count
            count = 0

    while True:

        client,addr = server.accept()

        print "[*] Accepted connection from {}:{}".format(addr[0],addr[1])

        # now handle client data
        client_handler = threading.Thread(target=handle_client(client,))
        client_handler.start()
