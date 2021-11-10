# -*- coding: utf-8 -*-
"""
Created on Fri May  7 15:53:20 2021
"""

from flask import Flask, render_template, request, flash
import pymongo
import pika

app = Flask(__name__)

# MongoDB instance
db = pymongo.MongoClient().COVIDTracker

#connecting to the channel
username = 'root'
password = 'toor'
host = 'localhost' #should be localhost
port = 5672 #should be 5672

#establish channel
credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host, port, '/', credentials))
channel = connection.channel()

@app.route('/consume', methods=['GET', 'POST'])
def consume():
    if request.method == 'GET':
    
        #consume message
        response = channel.basic_get(queue='track', auto_ack=False)

        basicGetOk, basicProperties, message = response

        if message is not None and basicGetOk is not None:
            msg = message.decode("utf-8").split(':')
            db.tracker.insert_one({'name': msg[0], 'location': msg[1], 'status': msg[2], 'passport': msg[3]})
            flash('Consumed message: %s is %s %s, and %s' % (msg[0], msg[2], msg[1], 'has a passport.' if msg[3] == 'yes' else 'does not have a passport.'))
        else:
            flash('No messages!')
        #connection.close()
    return render_template('controller.html')

@app.route('/findone', methods=['GET', 'POST'])
def findone():
    if request.method == 'GET':
        findone = str(request.args.get('findone'))
        name = db.tracker.find({'name': {'$in': [f'{findone}']}})
        location = db.tracker.find({'location': {'$in': [f'{findone}']}})
        status = db.tracker.find({'status': {'$in': [f'{findone}']}})
        
        if name.count() != 0:
            flash('Name:           Location:     Status:         Passport:')
            for item in name:
                flash('%-16s %-14s %-16s %s' % (item['name'], item['location'], item['status'], item['passport']))
        elif location.count() != 0:
            flash('Name:           Location:     Status:         Passport:')
            for item in location:
                flash('%-16s %-14s %-16s %s' % (item['name'], item['location'], item['status'], item['passport']))
        elif status.count() != 0:
            flash('Name:           Location:     Status:         Passport:')
            for item in status:
                flash('%-16s %-14s %-16s %s' % (item['name'], item['location'], item['status'], item['passport']))
        else:
            flash(f'{findone} not found!') 
    return render_template('controller.html') 

@app.route('/', methods=['GET','POST'])
def homepage():
    return render_template('controller.html')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='localhost', port=9000, debug=False)