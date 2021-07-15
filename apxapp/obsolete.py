# This file contains old functions that are no longer used for reference

def get_oracle_db(username, password):
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

# Editing dependencies --------------------------------------------------------

# from app_functions.py ----

def edit_job_dependency( connect, *args):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_EDIT_JOB_DEPENDENCIES 0x{0},'{1}'
		""".format(args[0],args[1])
	try:
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
	except SQLAlchemyError as e:
		return "Unknown Error Occured"
	return "Done"

def edit_file_dependency( connect, *args):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_EDIT_FILE_DEPENDENCIES 0x{0},'{1}'
			""".format(args[0],args[1])
	try:
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
	except SQLAlchemyError as e:
		return "Unknown Error Occurred"
	return "Done"

def edit_event_dependency( connect, *args):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_EDIT_EVENT_DEPENDENCIES 0x{0},'{1}'
			""".format(args[0],args[1])
	try:
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
	except SQLAlchemyError as e:
		return "Unknown Error Occured"
	return "Done"

def work_on_edit_dependecies(add_dependency, connects, hexvalue):
	json_data = str(add_dependency).replace("'",'"').replace("True", "true").replace("False","false")
	result = edit_dependencies(connects,hexvalue, json_data)
	return result

# from vies.py -------------

class EditDependencyView(viewsets.ModelViewSet):

	serializer_class = AddDependencySerializer

	def create(self, request, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		oid = request.GET.get('oid')
		if oid is None:
			found_oids = find_objects(connection, self.request.GET.get('name', None))
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]

		serializer = self.get_serializer(data=request.data)
		try:
			if not serializer.is_valid():
				return Response({"Message":"Invalid JSON input."})
			sample_json = (serializer.validated_data.get('DEPENDENCIES'))
			print(sample_json)
			if "JOB" in sample_json:
				convert_dependency_name_into_oid(sample_json, connection)
			transaction =  connection.begin()
			result = work_on_edit_dependecies(sample_json, connection,oid)
			print(result)
			for key in result:
				if result[key] != "Done":
					return Response({"Message":"Error, check Dependency,rolling Back."})
			transaction.commit()
			connect = connect.close()
			return Response({"Message":"Dependency Have Been Added."})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error While updating dependencies, rolling back."})

# from urls.py ------------------

router.register(r'apx_api/v1/repository/dependency/edit', EditDependencyView, base_name = 'edit_dependency'),


# Editing permissions --------------------------------------------------------

# app_Functions.py --------------------------

def edit_permission(connect, oid, json_data):
	sq = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_EDIT_PERMISSIONS 0x{0},'{1}'
			SELECT @error
		""".format(oid, json_data)
	try:
		result = connect.execute(sq)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return "Done"
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011
