# -*- coding: utf-8 -*-
"""
Created on Thu May  6 18:40:44 2021
"""

from flask import Flask, render_template, request, flash
import pika

app = Flask(__name__)

#connecting to the channel
username = 'root'
password = 'toor'
host = 'localhost' #should be localhost
port = 5672 #should be 5672

credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host, port, '/', credentials))
channel = connection.channel()

places = ['Squires', 'Goodwin', 'Library', 'Surge', 'Torgerson']
for place in places:
        channel.exchange_declare(exchange=place, exchange_type='fanout')
        
channel.queue_declare(queue='track')

channel.queue_bind(exchange=places[0], queue='track', routing_key='track')
channel.queue_bind(exchange=places[1], queue='track', routing_key='track')
channel.queue_bind(exchange=places[2], queue='track', routing_key='track')
channel.queue_bind(exchange=places[3], queue='track', routing_key='track')
channel.queue_bind(exchange=places[4], queue='track', routing_key='track')

#connection.close()

@app.route('/track', methods=['GET','POST'])
def track():
    if request.method == 'GET':
        name = str(request.args.get('name'))
        location = str(request.args.get('location'))
        status = str(request.args.get('status'))
        passport = str(request.args.get('psp'))
        
        if not name:
            flash('Name is required!')
        elif location not in places:
            flash('Please enter valid location!')
        elif not status:
            flash('Please enter your entry/exit!')
        elif not passport:
            flash('Please enter your passport!')
        else:
            #establish channel
            #credentials = pika.PlainCredentials(username, password)
            #connection = pika.BlockingConnection(pika.ConnectionParameters(host, port, '/', credentials))
            #channel = connection.channel()
            #produce message
            channel.exchange_declare(exchange=location, exchange_type='fanout') #to ensure
            channel.basic_publish(exchange=location,routing_key=location,body=f'{name}:{location}:{status}:{passport}')
            #return redirect(url_for('index'))
            #connection.close()
            
            flash('Passport succesfully received!')
        
    return render_template('track.html')

@app.route('/', methods=['GET','POST'])
def homepage():
    return render_template('track.html')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='localhost', debug=False)