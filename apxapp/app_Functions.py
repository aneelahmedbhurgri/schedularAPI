from sqlalchemy.orm import sessionmaker, scoped_session, mapper
import sqlalchemy as al
import pyodbc
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from.utility import *
# create and commit transaction........................................................................

def begin_transaction(connection):
    c = connection.begin()
    return c
def commit_transaction(connection):
    connection.commit()
# Methods for requesting data or info ------------------------------------------------------------------

def p_profile_detail(job_id, sess):
	p_profile_statement = f"select PCCDBA.REST_P_PROFILE_AS_JSON({job_id})"
	result = sess.execute(p_profile_statement).fetchall()
	return result

def convert_dependency_name_into_oid(dependency_json, connect):
	for i in range(len(dependency_json)):
		if "ACCOUNT_OID" not in dependency_json[i]:
			statement = "select PCCDBA.REST_FIND_USER({0}) as OID"
			statement = statement.format(string_to_sql_literal(dependency_json[i]["ACCOUNT_NAME"]))
			newoid = connect.execute(statement).fetchone()
			dependency_json[i]["ACCOUNT_OID"] = "0x" + newoid[0].hex()

def get_job_history_detail(jobkey, run_num, connect):
	sql_query = "SELECT PCCDBA.REST_H_PROFILE_AS_JSON({0},{1})".format(jobkey,run_num)
	job_object = connect.execute(sql_query).fetchall()
	return job_object

def get_object_view(oid, connect):
	sql = """
		DECLARE @parent_oid binary(16) = 0x{0}
		SELECT sec.OID, sec.OID_NAME, t.TYPE, l.PATH as PROJECT, l.DESCRIPTION, I.RCS
		FROM PCCDBA.SECURITY_OBJECT sec
		join PCCDBA.HIERARCHY h on h.MEMBER_OID=sec.OID
		join PCCDBA.REST_OBJECT_TYPE t on sec.OID=t.OID
		join PCCDBA.REST_I_PROFILE l on sec.OID=l.OID
		WHERE FOLDER_OID = @parent_oid
		""".format(oid)
	result = connect.execute(sql).fetchall()
	return result
def get_objects_view(project, connect):
	sql = """
		select * from PCCDBA.REST_I_PROFILE where OID_NAME = '{0}'
		""".format(project)
	result = connect.execute(sql).fetchall()
	return result


def get_object_oid(parent, child, sess):
	statement = "SELECT OID FROM PCCDBA.REST_FIND_OBJECTS({0}, {1})"
	statement = statement.format(string_to_sql_literal(parent), string_to_sql_literal(child))
	oid = sess.execute(statement).fetchone()
	return oid

def get_profile_view_json(oid, sess):
	sql_statement = f"SELECT PCCDBA.REST_I_PROFILE_AS_JSON (0x{oid})"
	json_data = sess.execute(sql_statement).fetchall()[0]
	return json_data

def find_objects(connection, name):
	parent, child = split_name(name)
	statement = "SELECT OID FROM PCCDBA.REST_FIND_OBJECTS({0},{1})"
	statement = statement.format(string_to_sql_literal(parent), string_to_sql_literal(child))
	found_oids = connection.execute(statement).fetchall()
	for i in range(len(found_oids)):
		found_oids[i] = found_oids[i][0].hex()
	return found_oids

def find_user(connect, account_name):
	try:
		statement = "SELECT PCCDBA.REST_FIND_USER({0})".format(string_to_sql_literal(account_name))
		oid = connect.execute(statement).fetchone()
		return oid[0].hex()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

# Methods for dependencies --------------------------------------------------------------------

def add_dependencies(connect, oid, json_data):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_ADD_DEPENDENCIES 0x{0}, {1}
			select @error
		""".format(oid, string_to_sql_literal(json_data))
	try:
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
	except SQLAlchemyError as e:
			return 9011
	return 0

def delete_all_dependencies(oid, connects):
	s = """
		 declare
		 @error integer
		 EXEC @error=PCCDBA.REST_DELETE_ALL_DEPENDENCIES 0x{0}
		 SELECT @error""".format(oid)
	try:
		result = connects.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		return 9011

# Methods for updating and editing objects --------------------------------------------------

def update_job(connect, oid, json_data):
	sql = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_JOB_UPDATE 0x{0}, {1}
			SELECT @error
	""".format(oid, string_to_sql_literal(json_data))
	try:
		result = connect.execute(sql).fetchall()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 'Unknown Error Found.'
	if "ERROR_CODE" in result[0]:
		return result[0]["ERROR_CODE"]
	return 0

def change_object_name(connect, oid, new_name):
	sq = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_RENAME_OBJECT 0x{0}, {1}
			SELECT @error""".format(oid, string_to_sql_literal(new_name))
	try:
		result = connect.execute(sq)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		return 9011

def add_permissions(connect, oid, json_data): # permissions are not working correctly.
	json_data = '{"'+'Permissions'+'"'+':'+json_data + '}'	#Todo: Unify name, so this conversion doesn't have to happen
	sq = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_ADD_PERMISSIONS 0x{0}, {1}
			SELECT @error""".format(oid, string_to_sql_literal(json_data))
	try:
		result = connect.execute(sq)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

def delete_permission(connect, object_oid, account_oid):
	s = """
		 declare
		 @error integer
		 EXEC @error=PCCDBA.REST_DELETE_PERMISSION 0x{0}, 0x{1}
		 SELECT @error""".format(object_oid, account_oid)
	try:
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

def delete_object(connect,oid): # this function is callled to delete job from db.
	sql = "DELETE from PCCDBA.SECURITY_OBJECT WHERE OID=0x{0}".format(oid)
	try:
		result = connect.execute(sql)
		return 0
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

# Methods for creating Objects -------------------------------------------------------

def create_job(connect, parent_oid, os_name, job_name, json_data):
	sql = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_CREATE_JOB 0x{0}, {1}, {2}
			SELECT @error
		""".format(parent_oid, string_to_sql_literal(os_name), string_to_sql_literal(job_name))
	# Creating the Job
	try:
		result = connect.execute(sql)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0], 0
		new_oid = result[0][0].hex()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011, 0
	# Updating the created Job
	return_code = update_job(connect, new_oid, json_data)
	if return_code != 0:
		return return_code, 0
	return 0, new_oid

def create_project(connect, parent_oid, name):
	sq = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_CREATE_PROJECT 0x{0}, {1}
			SELECT @error
		""".format(parent_oid, string_to_sql_literal(name))
	try:
		result = connect.execute(sq)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"], 0
		result = result[0][0]
		return 0, result.hex()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011, 0

def create_net_project(connect, parent_oid, name):
	sq = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_CREATE_NET 0x{0}, {1}
			SELECT @error
		""".format(parent_oid, string_to_sql_literal(name))
	try:
		print(sq)
		result = connect.execute(sq)
		result = result.fetchall()
		print(result)
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"], 0
		result = result[0][0]
		return 0, result.hex()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011, 0

def create_client(connect, data):
	sq = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_CREATE_CLIENT {0}
			SELECT @error
		""".format(string_to_sql_literal(data))
	try:
		result = connect.execute(sq)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		result = result[0][0]
		return 0, result.hex()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011, 0

# Methods for dealling with custom user filters -----------------------------------------------

def add_custom_filter(connect, user, filter_name, filter_request):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_ADD_FILTER {0}, {1}, {2}
			SELECT @error
		""".format(string_to_sql_literal(user), string_to_sql_literal(filter_name), string_to_sql_literal(filter_request))
	try:
		print(s)
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

def delete_custom_filter(connect, user_name, filter_name):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_DELETE_FILTER {0}, {1}
			SELECT @error
		""".format(string_to_sql_literal(user_name), string_to_sql_literal(filter_name))
	try:
		print(s)
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

def delete_all_filters_for_user(connect, user_oid):
	s = """
			declare
			@error integer
			EXEC @error=PCCDBA.REST_DELETE_ALL_FILTERS_FOR_USER 0x{0}
			SELECT @error""".format(user_oid)
	try:
		print(s)
		result = connect.execute(s)
		result = result.fetchall()
		if "ERROR_CODE" in result[0]:
			return result[0]["ERROR_CODE"]
		return 0
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011

def get_clients(connect):

	try:
		result = connect.execute("SELECT * FROM PCCDBA.REST_CLIENT")
		return result.fetchall()
	except SQLAlchemyError as e:
		log_exception(e, getframeinfo(currentframe()), "Database error")
		return 9011