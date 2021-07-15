import base64
import sqlalchemy as al
import cx_Oracle
import os
import ibm_db_sa
import ibm_db
import pyodbc
import json

def get_db2_db():
	json_data = None
	with open("c:/RESTconfig/settings.json") as json_file:
		json_data = json.load(json_file)
		return json_data["DATABASE"]
def return_connection(request):
	try:
		auth_header = request.META['HTTP_AUTHORIZATION']
		#print(auth_header)
		encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
		decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
		username = decoded_credentials[0]
		password = decoded_credentials[1]
		LOCATION = r"C:\clidriver\bin"
		os.environ["PATH"] = LOCATION + ";" + os.environ["PATH"]
		enginedb2 = al.create_engine(f'db2+pyodbc://{username}:{password}@{get_db2_db}')
		server='db2'
		connection = enginedb2
		con = enginedb2.connect()
		con = con.close()
		return [connection, server]
	except Exception as e:
		print(e)
		print("Connection Not Found please re try")
		return None
