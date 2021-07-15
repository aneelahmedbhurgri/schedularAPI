import base64
import sqlalchemy as al
import cx_Oracle
import os
import ibm_db_sa
import ibm_db
import pyodbc
import json
from sqlalchemy.orm import sessionmaker, scoped_session, mapper
from rest_framework.authtoken.models import Token
import random
import string

def custome_encode(username, password):
	encrypt_data = (username + password)
	print(encrypt_data)

def cutome_decode(username, password):
	pass
def get_oracle_db():
	json_data = None
	with open("c:/RESTconfig/settings.json") as json_file:
		json_data = json.load(json_file)
		return json_data["DATABASE"]
def return_connection(request):
	try:
		auth_header = request.META['HTTP_AUTHORIZATION']
		encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
		decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
		username = decoded_credentials[0]
		password = decoded_credentials[1]
		engine = al.create_engine(f"oracle+cx_oracle://{username}:{password}@{get_oracle_db()}")
		custome_encode(username,password)
		server='oracle'
		connection = engine
		con = engine.connect()
		con = con.close()
		return [connection, server]
	except Exception as e:
		token = request.GET.get('token')
		try:
			if token is not None:
				username, password = revert(token)
				engine = al.create_engine(f"oracle+cx_oracle://{username}:{password}@{get_oracle_db()}")
				custome_encode(username,password)
				server='oracle'
				connection = engine
				con = engine.connect()
				con = con.close()
				return [connection, server]
			else:
				None
		except:
			print(e)
			print("Connection Not Found please re try")
			return None

def new_Session_raw_connection(request):
	try:
		auth_header = request.META['HTTP_AUTHORIZATION']
		#print(auth_header)
		encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
		decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
		username = decoded_credentials[0]
		password = decoded_credentials[1]
		engine = al.create_engine(f"oracle+cx_oracle://{username}:{password}@{get_oracle_db()}")
		connection = engine
		con = engine.connect()
		con = con.close()
		Session = sessionmaker(bind=connection)
		session = Session()
		connect = connection.raw_connection()
		return [session, connect]
	except:
		token = request.GET.get('token')
		try:
			if token is not None:
				username, password = revert(token)
				engine = al.create_engine(f"oracle+cx_oracle://{username}:{password}@{get_oracle_db()}")
				custome_encode(username,password)
				server='oracle'
				connection = engine
				con = engine.connect()
				con = con.close()
				return [connection, server]
			else:
				return None
		except:
			return None

def current_user(request):
	try:
		auth_header = request.META['HTTP_AUTHORIZATION']
		#print(auth_header)
		encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
		decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
		username = decoded_credentials[0]
		return username
	except:
		token = request.GET.get('token')
		try:
			if token is not None:
				username, password = revert(token)
				return username
			else:
				return None
		except:
			return None

def new_connection(request):
	connection = return_connection(request)
	if connection is not None:
		return connection[0].raw_connection()
	return None

def return_session(request):
	try:
		connection = return_connection(request)[0]
		Session = sessionmaker(bind=connection)
		session = Session()
		return session
	except:
		return None


def convert(username, password):
	new_token = ''
	user_name_encode = str(len(username))
	new_token = new_token + user_name_encode
	for i in range(len(username)):
		lower_upper_alphabet = string.ascii_letters
		random_letter = random.choice(lower_upper_alphabet)
		new_token = new_token + random_letter + str(ord (username[i]))
	new_token = new_token + '%'
	for i in range(len(password)):
		lower_upper_alphabet = string.ascii_letters
		random_letter = random.choice(lower_upper_alphabet)
		new_token = new_token + random_letter + str(ord (password[i]))
	return new_token

def revert(new_token):
	spliting = new_token.split('%')
	name = str(spliting[0])
	password = str(spliting[1])
	get_pass =  ''
	re_token = ''
	counter = 0
	for i in range(len(name)):
		if name[i].isalpha():
			name = name.replace(name[i],',')
	name = name.split(',')
	for i in range (len(name)-1):
		number = int(name[i+1])
		re_token = re_token + chr(number)

	for i in range(len(password)):
		if password[i].isalpha():
			password = password.replace(password[i],',')
	password = password.split(',')
	for i in range (len(password)-1):
		number = int(password[i+1])
		get_pass = get_pass + chr(number)
	return(re_token, get_pass)
