import base64
import sqlalchemy as al
import cx_Oracle
import os
import pyodbc
import json
from sqlalchemy.orm import sessionmaker, scoped_session, mapper
from sqlalchemy.exc import SQLAlchemyError
from rest_framework.authtoken.models import Token
import random
import string
from .models import *

import logging; logger = logging.getLogger(__name__); from inspect import currentframe, getframeinfo

def get_ms_db():
	json_data = None
	with open("c:/RESTconfig/settings.json") as json_file:
		json_data = json.load(json_file)
		return json_data["DATABASE"]

def return_connection(request):
	database = get_ms_db()
	try:
		auth_header = request.META['HTTP_AUTHORIZATION']
		if "Bearer" in auth_header:
			auth_header = bearer_auth(auth_header)
			if auth_header is None:
				return None, ''
			auth_header = auth_header.name
		encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
		decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
		username = decoded_credentials[0]
		password = decoded_credentials[1]
		print(username)
		enginemssql = al.create_engine(f'mssql+pyodbc://{username}:{password}@{database}')
		server='mssql'
		connection = enginemssql
		con = enginemssql.connect()
		con = con.close()
		return connection, server
	except Exception as e:
		print(e)
		frameinfo = getframeinfo(currentframe())
		template = "{} in {} line {}: ".format(type(e).__name__, frameinfo.filename[-32:], frameinfo.lineno)
		logger.error(template + "Could not connect to database".format())
		return None, ''


def new_Session_raw_connection(request):
	database = get_ms_db()
	try:
		auth_header = request.META['HTTP_AUTHORIZATION']
		if "Bearer" in auth_header:
			auth_header = bearer_auth(auth_header)
			if auth_header is None:
				return None, ''
			auth_header = auth_header.name
		encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
		decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
		username = decoded_credentials[0]
		password = decoded_credentials[1]
		engine = al.create_engine(f'mssql+pyodbc://{username}:{password}@{database}')
		connection = engine
		con = engine.connect()
		Session = sessionmaker(bind=connection)
		session = Session()
		return connection, session
	except SQLAlchemyError as e:
		frameinfo = getframeinfo(currentframe())
		template = "{} in {} line {}: ".format(type(e).__name__, frameinfo.filename[-32:], frameinfo.lineno)
		logger.error(template + "Could not connect to database".format())
		return None, ''

def new_connection(request):
	connection, _ = return_connection(request)
	if connection is not None:
		return connection.connect()
	return None

def return_session(request):
	try:
		connection, _ = return_connection(request)
		#logger.debug("Connection:", connection)
		if connection is None:
			return None
		Session = sessionmaker(bind=connection)
		session = Session()
		return session
	except SQLAlchemyError as e:
		frameinfo = getframeinfo(currentframe())
		template = "{} in {} line {}: ".format(type(e).__name__, frameinfo.filename[-32:], frameinfo.lineno)
		logger.error(template + "Binding error".format())
		return None


def convert(username, password):
	new_token = ''
	user_name_encode = str(len(username))
	new_token = new_token + user_name_encode
	for i in range(len(username)):
		lower_upper_alphabet = string.ascii_letters
		random_letter = random.choice(lower_upper_alphabet)
		new_token = new_token + random_letter + str(ord (username[i]))
	new_token = new_token + '$'
	for i in range(len(password)):
		lower_upper_alphabet = string.ascii_letters
		random_letter = random.choice(lower_upper_alphabet)
		new_token = new_token + random_letter + str(ord (password[i]))
	return new_token

def revert(new_token):
	spliting = new_token.split('$')
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
	return (re_token, get_pass)

def bearer_auth(auth_header):
	try:
		api_key = APIKey.objects.get(oid=str(auth_header).split(' ')[1])
		get_from_obj = APIKey.objects.get_from_key(api_key.oid)
		return get_from_obj
	except Exception as e:
		frameinfo = getframeinfo(currentframe())
		template = "{} in {} line {}: ".format(type(e).__name__, frameinfo.filename[-32:], frameinfo.lineno)
		logger.error(template + "Could not connect to database".format())
		return None
