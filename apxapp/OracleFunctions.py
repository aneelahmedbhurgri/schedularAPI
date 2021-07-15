from datetime import timezone
from APX.authentication import ApxPermission, ApxAuthentication
from sqlalchemy.orm import sessionmaker, scoped_session, mapper
import base64
import sqlalchemy as al
import cx_Oracle
import os
import ibm_db_sa
import ibm_db
import pyodbc
from sqlalchemy import func
import xmltodict
import collections
from.Authentication import *

# this function is callled to delete a job from db.
def delete_object(connect,oid):
	try:
		connection = connect
		cursor = connection.cursor()
		return_value = cursor.var(cx_Oracle.NUMBER)
		cursor.callfunc("PCCDBA.REST_DELETE_OBJECT", return_value, (oid,))
		return "Object Deleted."
	except SQLAlchemyError as e:
		return "Could Not Delete Object."

def p_profile_detail(arg, connect): # not oracle yet
	try:
		connection = connect
		cursor = connection.cursor()
		return_value = cursor.var(cx_Oracle.NCHAR)
		cursor.callfunc("PCCDBA.REST_P_PROFILE_AS_JSON", return_value, (arg,))
		return [[return_value.getvalue()]]
	except Exception as e:
		print(e)
		return "No JOB FOUND"

def convert_permission_name_into_oid(sample_json,raw_connection):
	connection = raw_connection
	cursor = connection.cursor()
	outcur = cursor.var(cx_Oracle.CURSOR)
	return_value = cursor.var(cx_Oracle.NUMBER)
	for i in range(len(sample_json)):
		if "ACCOUNT_OID" not in sample_json[i]:
			val=cursor.callfunc("PCCDBA.REST_FIND_USER", return_value, (sample_json[i]["ACCOUNT_NAME"],outcur,))
			outcur = outcur.getvalue()
			column_names_list = [x[0] for x in outcur.description]
			# construct a list of dict objects (<one table row>=<one dict>)
			result_dicts = [dict(zip(column_names_list, row)) for row in outcur.fetchall()]
			sample_json[i]["ACCOUNT_OID"] = result_dicts[0]["PARAM0"]
	return sample_json

def get_job_history_detail(jobkey, run_num, raw_connection):# not oracle yet
	connection = raw_connection
	cursor = connection.cursor()
	return_value = cursor.var(cx_Oracle.NCHAR)
	cursor.callfunc("PCCDBA.REST_H_PROFILE_AS_JSON", return_value, (jobkey,run_num))
	return [[return_value.getvalue()]]

def get_object_view(oid,connect):# not oracle yet
	get_oid = str(oid).upper()
	sql = """
		SELECT sec.OID, sec.OID_NAME, t.TYPE
		FROM PCCDBA.SECURITY_OBJECT sec
		join PCCDBA.HIERARCHY h on h.MEMBER_OID=sec.OID
		join PCCDBA.REST_OBJECT_TYPE t on sec.OID=t.OID
		WHERE FOLDER_OID = '{0}'
		""".format(get_oid)
	print(sql)
	cursor = connect.cursor()
	result = cursor.execute(sql).fetchall()
	print(result)
	return result

def convert_dependency_name_into_oid(sample_json,raw_connection):# not oracle yet
	new_json = sample_json
	for i in range(len(new_json["JOB"])):
		if 'PATH' in new_json["JOB"][i]:
			get_name_oid = get_name(new_json["JOB"][i]['PATH'])
			#stmt = "OID FROM PCCDBA.FIND_OBJECTS('{0}', '{1}')".format(get_name_oid[0], get_name_oid[1]) # query to search for the given object inside database
			newoid = get_object_oid(get_name_oid[0], get_name_oid[1],raw_connection)
			#newoid = sess.query(stmt).first()
			new_json["JOB"][i]['DEPENDENCY'] =  newoid[0].hex()
	return new_json

def delete_all_dependency(connects, oid):# not oracle yet
	try:
		connection = connects
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val = cursor.callfunc("PCCDBA.REST_DELETE_ALL_DEPENDENCIES", return_value, (oid,outcur,))
		return_value = return_value.getvalue()
		print(return_value)
		if int(return_value) is not 0:
			return return_value
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		print(e)
		return "Unknown Error Occured"

def get_profile_view_json(oid, raw_connection): # converting to oracle procedure
	try:
		connection = raw_connection
		cursor = connection.cursor()
		return_value = cursor.var(cx_Oracle.NCHAR)
		cursor.callfunc("PCCDBA.REST_I_PROFILE_AS_JSON", return_value, (oid,))
		return [return_value.getvalue()]
	except SQLAlchemyError as e:
		print(e)
		return "Nothing Found"

def get_object_oid(parent, child, raw_connection):
	try:
		connection = raw_connection
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_FIND_OBJECTS", return_value, (parent,child, outcur,))
		outcur = outcur.getvalue()
		column_names_list = [x[0] for x in outcur.description]
		# construct a list of dict objects (<one table row>=<one dict>)
		result_dicts = [dict(zip(column_names_list, row)) for row in outcur.fetchall()]
		return [result_dicts[0]["OID"],None]
	except SQLAlchemyError as e:
		print(e)
		return None

def job_dependency(connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		oid = str(args[0]).upper()
		print(args)
		val=cursor.callfunc("PCCDBA.REST_ADD_DEPENDENCIES", return_value, (oid,args[1],outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		print(e)
		return "Unknown Error Occured"

def get_oracle_dbs(username, password):
	host='packardbell'
	port='1521'
	sid='TESTDBs'
	sid = cx_Oracle.makedsn(host, port, sid=sid)
	#sql_server ='\SQLEXPRESS/APXDB?driver=ODBC+Driver+13+for+SQL+Server'
	return_st = 'oracle://{username}:{password}@{sid}'.format(
		username=username,
		password=password,
		sid=sid
	)
	return return_st

def get_mssql_db():
	sql_server ='\SQLEXPRESS/APXDB32?driver=ODBC+Driver+13+for+SQL+Server'
	return sql_server

def get_db2_db(username, password,db):
	LOCATION = r"C:\clidriver\bin"
	os.environ["PATH"] = LOCATION + ";" + os.environ["PATH"]
	port = 50002
	#return_statement = f"db2+pyodbc://{username}:{password}@DB2TESTDB_32"
	return_statement = (db, f"{username}", f"{password}")
	return return_statement

def split_name(args):
	value = args
	if value is not None:
		parent = '%'
		child = '%'
		substring = value
		otherstring = value
		if (value.find(':')) is not -1 and value.find('/') is not -1:
			parent = value[0:value.rfind('/')+1]
			child = value[value.rfind('/')+1:len(value)]
		elif value.find(':') is not -1 and value.find('/') is -1:
			parent = value[0:value.rfind(':')+1] + '/'
			child = value[value.rfind(':')+1:len(value)]
		elif value.find(':') is -1 and value.find('/') is not -1:
			if value[0] is not '/':
				parent = '%/' + value[0:value.rfind('/')] + '/'
				child = value[value.rfind('/')+1:len(value)]
			else:
				parent = '%' + value[0:value.rfind('/')] + '/'
				child = value[value.rfind('/')+1:len(value)]
		else :
			child = value
		return [parent, child]
	return ['%', '%']

def create_job(connect, parent_oid, os_name, job_name,json_data):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val = cursor.callfunc("PCCDBA.REST_CREATE_JOB", return_value, (parent_oid,job_name,os_name , outcur,))
		outcur = outcur.getvalue()
		column_names_list = [x[0] for x in outcur.description]
		result_dicts = [dict(zip(column_names_list, row)) for row in outcur.fetchall()]
		if result_dicts[0]["ID"] is not 0:
			return [result_dicts[0]["ID"]]
		result = (result_dicts[0]["PARAM0"])
		update = create_job_update(connection, result.hex(), json_data)
		#update = "Done"
		return [update, result.hex()]
	except SQLAlchemyError as e:
		return None

def create_job_update(connect, *args): # this update function is only used with create procedure
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_JOB_UPDATE", return_value, (args[0],args[1], outcur,))
		out_result = return_value.getvalue()
		if int(out_result) is not 0:
			return 9010
		return f'Job have been created.'
	except SQLAlchemyError as e:
		return None

def update_job(connect, *args):
	try:
		oid = str(args[0]).upper()
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_JOB_UPDATE", return_value, (oid,args[1], outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return 9010
		return f'Job have been updated with OID {args[0]}.'
	except SQLAlchemyError as e:
		return 'Unknown Error Found.'

def update_project(connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		print(args)
		val=cursor.callfunc("PCCDBA.REST_JOB_UPDATE", return_value, (args[0],args[1], outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		return "Done"
	except SQLAlchemyError as e:
		return None


def file_dependency(connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_ADD_FILE_DEPENDENCIES", return_value, (args[0],args[1],outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		return "Unknown Error Occured"

def event_dependency(connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_ADD_EVENT_DEPENDENCIES", return_value, (args[0],args[1],outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		return "Unknown Error Occured"

def edit_job_dependency( connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_EDIT_JOB_DEPENDENCIES", return_value, (args[0],args[1],outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		return "Unknown Error Occured"

def edit_file_dependency( connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_EDIT_FILE_DEPENDENCIES", return_value, (args[0],args[1],outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		return "Unknown Error Occured"

def edit_event_dependency( connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_EDIT_EVENT_DEPENDENCIES", return_value, (args[0],args[1],outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		#result = result_dicts[0]["PARAM0"]
		return "Done"
	except SQLAlchemyError as e:
		return "Unknown Error Occured"

def collect_rules(value):
	return_dict = {}
	for key in value:
		if key == '@AL' or key =='AL':
			mail_trap = value[key]
			if mail_trap == "t":
				return_dict["Trap"] = True
			if mail_trap == "m":
				return_dict["Mail"] = True
			if mail_trap == "t,m":
				return_dict["Trap"] = True
				return_dict["Mail"] = True
		if key == "DO" or key == "@DO":
			if value[key].__class__ == collections.OrderedDict:
				return_dict["Command"] = dict(value[key])["@CMD"]
			else:
				return_dict["Command"] = (value[key])
		if key == "S" or key == "@S":
			return_dict["Status"] = value[key]
	return return_dict

def create_project(connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_CREATE_PROJECT", return_value, (args[0],args[1], outcur,))
		outcur = outcur.getvalue()
		column_names_list = [x[0] for x in outcur.description]
		result_dicts = [dict(zip(column_names_list, row)) for row in outcur.fetchall()]
		if result_dicts[0]["ID"] is not 0:
			return result_dicts[0]["ID"]
		return result_dicts[0]["PARAM0"].hex()
	except SQLAlchemyError as e:
		return None

def change_object_name(connect, *args):
	try:
		oid = str(args[0]).upper()
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_RENAME_OBJECT", return_value, (oid,args[1], outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return None
		return "Done"
	except SQLAlchemyError as e:
		return None

def create_net_project(connect, *args):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_CREATE_NET", return_value, (args[0],args[1], outcur,))
		outcur = outcur.getvalue()
		column_names_list = [x[0] for x in outcur.description]
		result_dicts = [dict(zip(column_names_list, row)) for row in outcur.fetchall()]
		if result_dicts[0]["ID"] is not 0:
			return result_dicts[0]["ID"]
		return result_dicts[0]["PARAM0"].hex()
	except:
		return None

def work_on_dependecies(add_dependency, connects, hexvalue):
	result = None
	json_data = str(add_dependency).replace("'",'"').replace("True", "true").replace("False","false")
	result = job_dependency(connects,hexvalue, json_data)
	return result

def work_on_edit_dependecies(add_dependency, connects, hexvalue):
	result = {}
	for key in add_dependency:
		if key == 'JOB' and len(add_dependency['JOB']) != 0:

			job = str(add_dependency['JOB']).replace("'",'"').replace("True", "true").replace("False","false")
			result['Job Dependency'] = edit_job_dependency(connects,hexvalue, job)

		if key == 'FILE' and len(add_dependency['FILE']) != 0:
			files = str(add_dependency['FILE']).replace("'",'"').replace("True", "true").replace("False","false")
			result['File Dependency'] = edit_file_dependency(connects,hexvalue,files)

		if key == 'EVENT' and len(add_dependency['EVENT']) != 0:
			event = str(add_dependency['EVENT']).replace("'",'"').replace("True", "true").replace("False","false")
			result['Event Dependency'] = edit_event_dependency(connects,hexvalue,event)
	return result

def get_at_rules(anyvar):
	at_rules = "<root>" + (anyvar["AT_RULES"]) + "</root>"
	at_rules = (xmltodict.parse(at_rules))
	if at_rules["root"] is not None:
		at_rules = (at_rules['root'])
		at_rules = (dict(at_rules))

	RULES = {
		"AT_LATEST_START":{},
		"AT_CANCEL":{},
		"AT_FINISH":{},
		"AT_MAX_RUNTIME":{},
		"AT_LATEST_FINISH":{},
		"AT_INTERVAL_DISTRIBUTED":{},
		"AT_MAX_TIME_IN_C":{},
		"AT_START":{},
		"AT_LAST_CANCEL":{}
	}
	for key in at_rules:
		if (key == "ST") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_START":collect_rules(at_rules[key])})

		elif (key == "LS") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_LATEST_START":collect_rules(at_rules[key])})

		elif (key == "KO") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_CANCEL":collect_rules(at_rules[key])})
		elif (key == "LC") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_LAST_CANCEL":collect_rules(at_rules[key])})
		elif (key == "OK") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_FINISH":collect_rules(at_rules[key])})
		elif (key == "MR") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_MAX_RUNTIME":collect_rules(at_rules[key])})
		elif (key == "LE") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_LATEST_FINISH":collect_rules(at_rules[key])})
		elif (key == "PD") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_INTERVAL_DISTRIBUTED":collect_rules(at_rules[key])})
		elif (key == "MC") and (at_rules[key] is not None):
			collect_rules(at_rules[key])
			RULES.update({"AT_MAX_TIME_IN_C":collect_rules(at_rules[key])})
	return RULES

def add_permissions(connect, oid,json_data):
	try:
		print(json_data)
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_ADD_PERMISSIONS", return_value, (oid,json_data,outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		return "Done"
	except SQLAlchemyError as e:
		print(e)
		return None

def edit_permission(connect, oid, json_data):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_EDIT_PERMISSIONS", return_value, (oid,json_data,outcur,))
		return_value = return_value.getvalue()

		if int(return_value) is not 0:
			return int(return_value)
		return "Done"
	except SQLAlchemyError as e:
		return None

def create_client(connect,data):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_CREATE_CLIENT", return_value, (data,outcur,))
		outcur = outcur.getvalue()
		column_names_list = [x[0] for x in outcur.description]
		result_dicts = [dict(zip(column_names_list, row)) for row in outcur.fetchall()]
		if result_dicts[0]["ID"] is not 0:
			return result_dicts[0]["ID"]
		return "Done"
	except SQLAlchemyError as e:
		return None

def delete_permission(connect, obj_oid, account_oid):
	try:
		connection = connect
		cursor = connection.cursor()
		outcur = cursor.var(cx_Oracle.CURSOR)
		return_value = cursor.var(cx_Oracle.NUMBER)
		val=cursor.callfunc("PCCDBA.REST_DELETE_PERMISSIONS", return_value, (obj_oid,account_oid,outcur,))
		return_value = return_value.getvalue()
		if int(return_value) is not 0:
			return int(return_value)
		return "Done"
	except SQLAlchemyError as e:
		return None

def check_sql_injection(query_string):
	list_keywords = ["ADD","add","ALTER","alter","BACKUP","backup","create","CREATE","REPLACE","replace","DELETE","delete","DROP","drop","INSERT","insert","SET","set","TRUNCATE","truncate","UPDATE","update"]
	if any(keyword in str(query_string).upper() for keyword in list_keywords):
		return True
	else: False

def find_user(connect, oid):
	try:

		connection = connect
		cursor = connection.cursor()
		return_value = cursor.var(cx_Oracle.BINARY)
		val=cursor.callfunc("PCCDBA.REST_FIND_USER", return_value, (oid,))
		return_value = return_value.getvalue()
		return return_value
	except SQLAlchemyError as e:
		return None

def custome_filters(connect, json_data):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_USER_FILTER {0}
			SELECT @error""".format(str(json_data).replace("'", '"'))
	try:
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return "Done"
	except SQLAlchemyError as e:
		print(e)
		return "Error Occured."
