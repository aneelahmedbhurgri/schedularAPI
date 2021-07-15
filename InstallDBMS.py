
import json
import os
import time
print("Installation Started...This might take a few seconds.....")
with open('C:/RESTconfig/settings.json') as f:
  data = json.load(f)

sql_server = False
oracle = False
db2 = False
try:
	for file in os.listdir("apxapp"):
		if file == "app_Functions.py":
			for files in os.listdir("apxapp"):
				if files == "sqlServerFunctions.py":
					sql_server = True
				if files == "OracleFunctions.py":
					oracle = True
				if files == "Db2Functions.py":
					db2 = True


	if sql_server == False:
		try:
			os.rename('apxapp/app_Functions.py','apxapp/sqlServerFunctions.py')
			os.rename('apxapp/Authentication.py','apxapp/sqlServerConnectionAuth.py' )
		except Exception as e:
			print(e)
			pass

	if oracle == False:
		try:
			os.rename('apxapp/app_Functions.py','apxapp/OracleFunctions.py')
			os.rename('apxapp/Authentication.py','apxapp/OracleConnectionAuth.py' )
			print("Name changing")
		except Exception as e:
			print(e)
			pass

	if db2 == False:
		try:
			os.rename('apxapp/app_Functions.py','apxapp/Db2Functions.py')
			os.rename('apxapp/Authentication.py','apxapp/Db2ConnectionAuth.py' )
		except Exception as e:
			print(e)
			pass
except:
	pass
time.sleep(2)
print("..............")
if data["DBMS"] == "sql server":
	try:
		os.rename('apxapp\sqlServerFunctions.py', 'apxapp\\app_Functions.py')
		os.rename('apxapp\sqlServerConnectionAuth.py', 'apxapp\\Authentication.py')
	except Exception as e:
		print(e)
		pass
elif data["DBMS"] == "oracle":
	try:
		os.rename('apxapp\OracleFunctions.py', 'apxapp\\app_Functions.py')
		os.rename('apxapp\OracleConnectionAuth.py', 'apxapp\\Authentication.py')
	except Exception as e:
		print(e)
		pass

elif data["DBMS"] == "db2":
	try:
		os.rename('apxapp\Db2Functions.py', 'apxapp\\app_Functions.py')
		os.rename('apxapp\Db2ConnectionAuth.py', 'apxapp\\Authentication.py')
	except Exception as e:
		print(e)
		pass
print("Installation Finished.....")
time.sleep(1)
