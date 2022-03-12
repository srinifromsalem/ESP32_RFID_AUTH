#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import sqlite3
import json
from types import SimpleNamespace
from datetime import datetime

sqliteConnection  = sqlite3.connect('useraccess.db')

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        #Things to do
        #1. Define a Boolean Flag to check If User Token ID is valid (i.e RFID) or Google Auth Code is Valid
        #2. Define a String to send Data Back saying Token Invalid or Auth Code Invalid
        #3. Based on Boolean Flag populate String and send response code and JSON back
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

        processRequest(post_data.decode('utf-8'))

def processRequest(json_data):
    cur = sqliteConnection.cursor()
    db_check(cur)
    database_business_process(cur,post_data.decode('utf-8'))

def database_business_process(cur, json_data):

    print("Method database_business_process")
    print("Received JSON Data : - ")
    print(json_data)

    token_dictionary = json.loads(json_data, object_hook=lambda d: SimpleNamespace(**d))

    # datetime object containing current date and time
    now = datetime.now()

    sql = ''' INSERT INTO useraccessdetails (tokenid,receiveddatetime,authcode,isauthcodevalid,datetime)
                  VALUES(?,?,?,?,?) '''
    project = (token_dictionary.tokenid,token_dictionary.datetime,token_dictionary.googleauth, True, now);
    cur.execute(sql, project)
    #useraccessdetails     (tokenid text, datetime text, authcode text, valid text)
    sqliteConnection.commit()

    print("Data persisted")
    for row in cur.execute('SELECT * FROM useraccessdetails'):
        print(row)

def db_check(cur):
    # get the count of tables with the name
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='user' ''')

    # if the count is 1, then table exists
    if cur.fetchone()[0] == 1:
        print("Regular, No DB Setup Needed : ---------------\n")
        for row in cur.execute('SELECT * FROM user ORDER BY name'):
            print(row)

    else: #If not then no table exist then create a new one
        print("First Time DB Setup : ---------------\n")
        # Create table
        print("Creating user Table")
        cur.execute('''CREATE TABLE user
                               (tokenid text, name text, enabledstatus boolean, datetime TEXT)''')

        # datetime object containing current date and time
        now = datetime.now()

        print("Inserting into user Table")
        # Insert sample rows of data
        sql = ''' INSERT INTO user (tokenid,name,enabledstatus,datetime)
                          VALUES(?,?,?,?) '''
        sample1 = ('12345678','Srini', True, now);
        cur.execute(sql, sample1)
        sample2 = ('12345677', 'Supri', True, now);
        cur.execute(sql, sample2)
        sample3 = ('12345676', 'Bhuvi', True, now);
        cur.execute(sql, sample3)

        print("Creating useraccessdetails Table")
        cur.execute('''CREATE TABLE useraccessdetails
                                       (tokenid INTEGER, receiveddatetime TEXT, authcode TEXT, isauthcodevalid Boolean, datetime TEXT)''')

        # Save (commit) the changes
        sqliteConnection.commit()

        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='user' ''')
        if cur.fetchone()[0] == 1:
            print('user table exists')

        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='useraccessdetails' ''')
        if cur.fetchone()[0] == 1:
            print('useraccessdetails table exists')

    print("Exiting db_check method")

def run(server_class=HTTPServer, handler_class=S, port=8050):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    sqliteConnection.close()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
