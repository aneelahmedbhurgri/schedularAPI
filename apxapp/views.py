from django.shortcuts import render, render_to_response
import sqlalchemy, sqlalchemy.orm
import urllib.parse
from django.http import Http404, request
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddDependencySerializer,ControlLogSerializer,CriticalRcsSerializer,EditDependencySerializer,GetJobDependencySerializer,GetJobObjectSerializer,GetJobOSSerializer,InAppSerializer
from .serializers import GetJobProfileSerializer,JobDetailSerializer,JobDiscriptionSerializer,JobUpdateSerializer,ProductionDeleteSerializer,ProductionGetSerializer, DeleteDependencySerializer,PermissionsSerializer
from .serializers import *
import json
import binascii
from APX.Orm import *
import time
from datetime import datetime, timezone
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import urllib.parse
from sqlalchemy.orm import sessionmaker, scoped_session, mapper
import sqlalchemy as al
from sqlalchemy.exc import ProgrammingError
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
import socket
import cx_Oracle
import platform
import os
import pyodbc
from sqlalchemy import func
from sqlalchemy import select, column
from django.shortcuts import redirect
from sqlalchemy import and_
from .pagination import StandardResultsSetPagination
import sqlite3
import collections
from django.http import FileResponse
from sqlalchemy.sql import text
import ast	# Where is this used? Can this be deleted?
from.Authentication import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from.app_Functions import *
from.utility import *
from.models import *

error_codes = {
	9001:"Object not Found",
	9004:"Object with same name Already inside Directory",
	9010:"JSON format error",
	None:"Error Occured while updating"
}


class JobDetailView(APIView):

	def get(self, request,**kwargs):
		if len(request.GET) != 1:
			return Response({"Message": "Wrong number of parameters."})
		connection, sess = new_Session_raw_connection(request)
		if connection is None or sess is None :
			return Response({"Message":"Invalid username/password."})
		name = request.GET.get('name')
		oid = request.GET.get('oid')
		key = request.GET.get('jobkey')
		result = None
		data = None
		job_id = ''
		if key is not None:
			job_id = key
		elif name is not None:
			try:
				name = name.replace('"', '').replace("'","")
				obj = sess.query(ProductionJobDetailORM).filter(ProductionJobDetailORM.JOBNAME == name).all()
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Databse error"}, status=status.HTTP_404_NOT_FOUND)
			finally:
				sess.close()
			if len(obj) > 1:
				return Response({"Message":"Multiple Jobs Found With parameter Please Search by JobKey or Choose production/objects/recursive/?name  for multiple Entries"}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
			elif len(obj) == 0:
				return Response({"No object found"}, status=status.HTTP_404_NOT_FOUND)
			job_id = obj[0].JOBID
		elif oid is not None:
			try:
				obj = sess.query(ProductionJobDetailORM).filter(ProductionJobDetailORM.OID==oid).all()
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Database error"}, status=status.HTTP_404_NOT_FOUND)
			finally:
				sess.close()
				connection.close()
			job_id = obj[0].JOBID
		result = p_profile_detail(job_id, connection)
		
		# Find out OID if only name is given:
		if "ERROR" in result[0][0]:
			return Response({"Message":"Error, Job Not Found"})
		data = json.loads(result[0][0]) # result[][]
		data["AT_RULES"] = get_at_rules((data))
		return Response(data)

class ProductionJobRecursiveView(APIView):
    
    def get(self, request,**kwargs):
        if len(request.GET) > 1:
            return Response({"Message": "One parameter max allowed"})
        state = request.GET.get('status')
        name = request.GET.get('name')
        description = request.GET.get('description')
        name_like = request.GET.get('name_like')
        description_like = request.GET.get('description_like')
        sql = request.GET.get('filters')
        jobkeys = request.GET.get('jobkey')
        names = request.GET.get('names')
        project = request.GET.get('project')
        print(request.GET, "-----------", len(request.GET))
        oids = request.GET.get('oids')
        folderkey = request.GET.get('folderkey')
        if state is 'H': # because in db H state of job is saved as empty
            state = ''
        obj = None
        query = []
        sess = return_session(request) # to create the session for query the db
        if sess is None: # if session is connected
            return Response({"Message":"Invalid Username/password or Internal Server Issue"}, status=status.HTTP_406_NOT_ACCEPTABLE) 
        path = request.get_full_path()
        if len(request.GET) == 0:
            obj = sess.query(ProductionJobORM).all()
            query = ProductionGetSerializer(obj, many=True).data # serializing the query data
        elif project is not None:
            project = project.replace("'", "").replace('"', '')
            obj = sess.query(ProductionJobORM).filter(text(f"PATH like '%{project}%'")).all()
            query = ProductionGetSerializer(obj, many=True).data
        elif name is not None:
            name = name.replace("'", "").replace('"', '')
            obj = sess.query(ProductionJobORM).filter(ProductionJobORM.JOBNAME.like(name)).all()
            query = ProductionGetSerializer(obj, many=True).data
        elif folderkey is not None:
            obj = sess.query(ProductionJobORM).filter(text(f"FOLDERKEY = {folderkey}")).all()
            query = ProductionGetSerializer(obj, many=True).data # serializing the query data
        elif name_like is not None:
            obj = sess.query(ProductionJobORM).filter(ProductionJobORM.JOBNAME.like(name_like)).all()
            query = ProductionGetSerializer(obj, many=True).data
        elif state is not None:
            obj = sess.query(ProductionJobORM).filter(ProductionJobORM.REAL_STATE == state)
            query = ProductionGetSerializer(obj, many=True).data
        elif sql is not None:
            if check_sql_injection(sql):
                return Response({"Message":"Given Query String is not supported."})
            sql = convert_sql_queries_prd(sql)
            obj = sess.query(ProductionJobORM).filter(text(sql[1:len(sql)-1]))
            query = ProductionGetSerializer(obj, many=True).data
        elif jobkeys is not None:
            keys = str(jobkeys).replace('[','').replace(']','')
            stmt = f"JOBID in ({keys})"
            obj = sess.query(ProductionJobORM).filter(text(stmt))
            query = ProductionGetSerializer(obj, many=True).data
        elif names is not None:
            names = str(names).replace('[','').replace(']','')
            stmt = f"JOBNAME in ({names})"
            obj = sess.query(ProductionJobORM).filter(text(stmt))
            query = ProductionGetSerializer(obj, many=True).data
        elif oids is not None:
            oids = str(oids).replace('[','').replace(']','')
            stmt = f"OID in ({oids})"
            obj = sess.query(ProductionJobORM).filter(text(stmt))
            query = ProductionGetSerializer(obj, many=True).data
        elif description is not None: # getting description of each job from db.
            try:
                description_sql = """
									select PCCDBA.CI_PRD_PROF_USR.JOBID,PCCDBA.CI_PRD_PROF_USR.JOBNAME,DESCRIPTION,REAL_STATE,PCCDBA.CI_PRD_PROF_USR.EARLIEST_START,PCCDBA.CI_PRD_PROF_USR.PATH,RUN_NO, PCCDBA.CI_PRD_PROF_USR.OID from PCCDBA.CI_PRD_PROF_USR
									INNER JOIN PCCDBA.CI_IDX_PROF_USR ON PCCDBA.CI_IDX_PROF_USR.JOBNAME = PCCDBA.CI_PRD_PROF_USR.JOBNAME WHERE DESCRIPTION
									LIKE ('{0}')""".format(description)
                obj = sess.execute(description_sql)
                if len(obj.fetchall()) > 0:
                    obj_serializer = ProductionGetSerializer(obj, many=True).data
                    sess = sess.close()
                    return Response({"Jobs":obj_serializer})
            except SQLAlchemyError as e:
                log_exception(e, getframeinfo(currentframe()), "Database error")
                return Response({"Message" : "Database error" },status=status.HTTP_404_NOT_FOUND)
        if description_like is not None:
            try:
                description_sql = """
									select PCCDBA.CI_PRD_PROF_USR.JOBID,PCCDBA.CI_PRD_PROF_USR.JOBNAME,DESCRIPTION,REAL_STATE,PCCDBA.CI_PRD_PROF_USR.EARLIEST_START,PCCDBA.CI_PRD_PROF_USR.PATH,RUN_NO, PCCDBA.CI_PRD_PROF_USR.OID from PCCDBA.CI_PRD_PROF_USR
									INNER JOIN PCCDBA.CI_IDX_PROF_USR ON PCCDBA.CI_IDX_PROF_USR.JOBNAME = PCCDBA.CI_PRD_PROF_USR.JOBNAME WHERE DESCRIPTION
									LIKE ('{0}')""".format(description_like)
                obj = sess.execute(description_sql)
                if len(obj.fetchall()) > 0:
                    obj_serializer = ProductionGetSerializer(obj, many=True).data
                    sess = sess.close()
                    return Response({"Jobs":obj_serializer})
            except SQLAlchemyError as e:
                log_exception(e, getframeinfo(currentframe()), "Database error")
                return Response({"Message" : "Database error" },status=status.HTTP_404_NOT_FOUND)
		# Adding an extra coloumn of Description into each job found
        for i in range(len(query)):
            sql_query_str = "select DESCRIPTION from PCCDBA.CI_IDX_PROF_USR where JOBID = {0}".format(str(query[i]['OID']))
            res = sess.execute(sql_query_str).fetchall()
            if len(res) is not 0 and res[0][0] is not None:
                query[i]['DESCRIPTION'] = res[0][0]
            else:
                query[i]['DESCRIPTION']='NULL'

        sess = sess.close()
        if len(query) == 0:
            return Response({"Message":"No job found with the given parameter"})
        else:
            print(len(query))
            return Response({"Jobs":query})

class ProductionJobView(APIView): # Return jOb List, job by filters(name, description, status, name like, description like,jobkey)

	def get(self, request, **kwargs):
		if len(request.GET) > 1:
			return Response({"Message" : "One parameter max allowed" })
		state = request.GET.get('status')
		description = request.GET.get('description')
		name = request.GET.get('name')
		name_like = request.GET.get('name_like')
		description_like = request.GET.get('description_like')
		sql = request.GET.get('filters')
		jobkeys = request.GET.get('jobkeys')
		names = request.GET.get('names')
		project = request.GET.get('project')
		print(request.GET, "-----------", len(request.GET))
		oids = request.GET.get('oids')
		folderkey = request.GET.get('folderkey')
		if state is 'H': # because in db H state of job is saved as empty
			state = ''
		obj = None
		query = []
		sess = return_session(request) # to create the session for query the db
		if sess is None: # if session is connected
			return Response({"Message":"Invalid Username/password or Internal Server Issue"}, status=status.HTTP_406_NOT_ACCEPTABLE)

		path = request.get_full_path()
		#if  path == "/apx_api/v1/production/jobs/": # to check if passed url is for listing all jobs from database.
		if len(request.GET) == 0:
			obj = sess.query(ProductionJobORM).filter(text("FOLDER_KEY is NULL")).all()
			query = ProductionGetSerializer(obj, many=True).data # serializing the query data
		elif name is not None:
			name = name.replace("'","").replace('"', '')
			obj = sess.query(ProductionJobORM).filter(ProductionJobORM.JOBNAME.like(name)).filter(text(f"FOLDER_KEY is NULL")).all()
			query = ProductionGetSerializer(obj, many=True).data
		elif project is not None:
			project = project.replace("'", "").replace('"','')
			obj = sess.query(ProductionJobORM).filter(text(f" PATH like  '%{project}%' and FOLDER_KEY is NULL")).all()
			query = ProductionGetSerializer(obj, many=True).data			
		elif folderkey is not None:
			obj = sess.query(ProductionJobORM).filter(text(f"FOLDER_KEY = {folderkey}")).all()
			query = ProductionGetSerializer(obj, many=True).data # serializing the query data
		elif name_like is not None:
			obj = sess.query(ProductionJobORM).filter(ProductionJobORM.JOBNAME.like(name_like)).filter(text(f"FOLDER_KEY is NULL")).all()
			query = ProductionGetSerializer(obj, many=True).data
		elif state is not None:
			obj = sess.query(ProductionJobORM).filter(ProductionJobORM.REAL_STATE == state).filter(text(f"FOLDER_KEY is NULL"))
			query = ProductionGetSerializer(obj, many=True).data
		elif sql is not None:
			if check_sql_injection(sql):
				return Response({"Message":"Given Query String is not supported."})
			sql = convert_sql_queries_prd(sql)
			obj = sess.query(ProductionJobORM).filter(text(sql[1:len(sql)-1])).filter(text(f"FOLDER_KEY is NULL"))
			query = ProductionGetSerializer(obj, many=True).data
		elif jobkeys is not None:
			keys = str(jobkeys).replace('[','').replace(']','')
			stmt = f"JOBID in ({keys})"
			obj = sess.query(ProductionJobORM).filter(text(stmt))
			query = ProductionGetSerializer(obj, many=True).data
		elif names is not None:
			names = str(names).replace('[','').replace(']','')
			stmt = f"JOBNAME in ({names})"
			obj = sess.query(ProductionJobORM).filter(text(stmt))
			query = ProductionGetSerializer(obj, many=True).data
		elif oids is not None:
			oids = str(oids).replace('[','').replace(']','')
			stmt = f"OID in ({oids})"
			obj = sess.query(ProductionJobORM).filter(text(stmt))
			query = ProductionGetSerializer(obj, many=True).data
		elif description is not None: # getting description of each job from db.
			try:
				description_sql = """
									select PCCDBA.CI_PRD_PROF_USR.JOBID,PCCDBA.CI_PRD_PROF_USR.JOBNAME,DESCRIPTION,REAL_STATE,PCCDBA.CI_PRD_PROF_USR.EARLIEST_START,PCCDBA.CI_PRD_PROF_USR.PATH,RUN_NO, PCCDBA.CI_PRD_PROF_USR.OID from PCCDBA.CI_PRD_PROF_USR
									INNER JOIN PCCDBA.CI_IDX_PROF_USR ON PCCDBA.CI_IDX_PROF_USR.JOBNAME = PCCDBA.CI_PRD_PROF_USR.JOBNAME WHERE DESCRIPTION
									LIKE ('{0}') and FOLDERKEY is NULL""".format(description)
				obj = sess.execute(description_sql)
				if len(obj.fetchall()) > 0:
					obj_serializer = ProductionGetSerializer(obj, many=True).data
					sess = sess.close()
					return Response({"Jobs":obj_serializer})
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Message" : "Database error" },status=status.HTTP_404_NOT_FOUND)
		elif description_like is not None:
			try:
				description_sql = """
									select PCCDBA.CI_PRD_PROF_USR.JOBID,PCCDBA.CI_PRD_PROF_USR.JOBNAME,DESCRIPTION,REAL_STATE,PCCDBA.CI_PRD_PROF_USR.EARLIEST_START,PCCDBA.CI_PRD_PROF_USR.PATH,RUN_NO, PCCDBA.CI_PRD_PROF_USR.OID from PCCDBA.CI_PRD_PROF_USR
									INNER JOIN PCCDBA.CI_IDX_PROF_USR ON PCCDBA.CI_IDX_PROF_USR.JOBNAME = PCCDBA.CI_PRD_PROF_USR.JOBNAME WHERE DESCRIPTION
									LIKE ('{0}') and FOLDERKEY is NULL""".format(description_like)
				obj = sess.execute(description_sql)
				if len(obj.fetchall()) > 0:
					obj_serializer = ProductionGetSerializer(obj, many=True).data
					sess = sess.close()
					return Response({"Jobs":obj_serializer})
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Message" : "Database error" },status=status.HTTP_404_NOT_FOUND)
		# Adding an extra coloumn of Description into each job found
		for i in range(len(query)):
			sql_query_str = "select DESCRIPTION from PCCDBA.CI_IDX_PROF_USR where JOBID = {0}".format(str(query[i]['OID']))
			res = sess.execute(sql_query_str).fetchall()
			if len(res) is not 0 and res[0][0] is not None:
				query[i]['DESCRIPTION'] = res[0][0]
			else:
				query[i]['DESCRIPTION']='NULL'

		sess = sess.close()
		if len(query) == 0:
			return Response({"Message":"No job found with the given parameter"})
		else:
			return Response({"Jobs":query})


class ProductionJobGenericView(APIView): # Returns the job with custome/generic Filteration

	def get(self, request,format=None, **kwargs): # used only with get request method to return data.
		if len(request.GET) > 1:
			return Response({"Message": "One parameter max allowed"})
		try:
			sess = return_connection(self.request)
			if sess is None:
				return Response({"Invalid Username/Password or Server Error"},status=status.HTTP_404_NOT_FOUND)
			sess = sess.connect() # creating session with db for the query.
			filters =  request.GET.get('filters')

			query_sql=f'Select JOBID as JOBNUMBER, JOBNAME, REAL_STATE as STATE_1, PATH as PROJECT,EARLIEST_START,RCS,RUN_NO,COND_CODE, ACTUAL_START From PCCDBA.CI_PRD_PROF_USR Where {filters[1:len(filters)-1]}' # sql statment to fetch data related to filter.
			obj = sess.execute(query_sql).fetchall()
			sess = sess.close()
			return Response({"Jobs":obj})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Invalid Username/Password or Server Error. Please check your query or URL"},status=status.HTTP_404_NOT_FOUND)


# post changes in a job in Production with predifined commands in PCC such as 'holding, releasing or REDO'
class ProductionJobControlView(APIView):

	def post(self, request, format = None, **kwargs):
		if len(request.GET) > 2:
			return Response({"Message": "Wrong number of parameters."})
		connection, dbms = return_connection(request)
		if connection is None:
			return Response({"Invalid Username/Password or Server Error"}, status = status.HTTP_404_NOT_FOUND)
		try:
			filters = request.GET.get('cmd')
			connected_connection = connection.connect()

			sql = "PCCDBA.CMD_SUBMIT"
			query = ''
			if query.startswith("'") and query.endswith("'"):
				query = query[1:len(query)-1]
			filters = str(filters).replace("'",'')
			print(filters)
			command_id = ''
			command_id = self.call_prco_mssql(connected_connection, sql, filters, 0)
			# todo db2

			if kwargs.__len__() == 1:
				time.sleep(int(kwargs['time']))
			else:
				time.sleep(3)
			sql_cmd_global = f'select MESSAGE, MSG_ID, CMDID, JOBID from PCCDBA.CI_CTL_LOG_USR where CMDID = {command_id}'
			result_global = ''
			result_global = connection.execute(sql_cmd_global).fetchall()

			if len(result_global) <= 1:
				wait_time = True
				start_time = time.time()
				while wait_time:
					time.sleep(2)
					result_global = connection.execute(sql_cmd_global).fetchall()
					if len(result_global) == 2:
						connection = connection.close()
						return Response(result_global, status=status.HTTP_201_CREATED)
					if time.time()-start_time > 5:
						connection = connection.close()
						return Response({"Command ID ": command_id, "Message ": "Command has been sent to PCC for Execution"}, status = status.HTTP_201_CREATED)

			connected_connection.close()
			#raw_connection = raw_connection.close()
			return Response(result_global, status=status.HTTP_201_CREATED)
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			error = f"Error {e}"
			return Response({error:2})

	def call_prco_mssql(self, connected_connection, sql_proc, *args):
		transaction = connected_connection.begin()
		sql = """SET NOCOUNT ON;
			DECLARE @ret int
			EXEC @ret = %s %s
			SELECT @ret""" % (sql_proc, ','.join(['?'] * len(args)))
		result =  connected_connection.execute(sql, args).fetchone()[0]
		transaction.commit()
		return int(result)


class ControlJobPostView(viewsets.ModelViewSet): # to change job status with raw command

	def create(self, request, *args, **kwargs): # Post method to change the state of Jobs belong to production.
		if len(request.GET) > 1:
			return Response({"Message": "Wrong number of parameters."})
		commands = ""
		sql = "PCCDBA.CMD_SUBMIT"
		connection, dbms = return_connection(request)
		if connection is None:
			return Response({"Invalid Username/Password or Server Error"}, status = status.HTTP_404_NOT_FOUND)
		delay = request.POST.get('delay') # in seconds
		try:
			if 'hold' in (request.path):
				commands = f'CHG_STATE1, {self.kwargs["id"]}, H'
			elif 'cancel' in (request.path):
				commands = f'CHG_STATE1, {self.kwargs["id"]}, C'
			elif 'release' in (request.path):
				commands = f'CHG_STATE1, {self.kwargs["id"]}'
			elif 'redo' in (request.path):
				commands = f'REDO, {self.kwargs["id"]}'
			elif 'load' in (request.path):
				query = f'select JOBNAME from CI_PRD_PROF_USR where JOBID = {self.kwargs["id"]}' # getting jobname from jobkey provided with request
				found_names = connection.execute(query).fetchall()
				if len(found_names) > 1:
					return Response({"Ambiguous Jobname":2})
				if len(found_names) == 0:
					return Response({"Error Object Not Found":2})
				commands = f'ADD_JOB, {found_names[0][0]}'
			elif 'finish' in (request.path):
				commands = f'CHG_STATE1, {self.kwargs["id"]}, F'

			connected_connection = connection.connect()
			command_id = ''
			command_id = self.call_prco_mssql(connected_connection, sql, commands, 0)
			time.sleep(3) # wait for sometime to fetch end result from db about passed query.
			if delay is not None:
				time.sleep(delay)
			sql_cmd_global = f'select MESSAGE, MSG_ID, CMDID, JOBID from PCCDBA.CI_CTL_LOG_USR where CMDID = {command_id}'
			result_global = ''
			result_global = connected_connection.execute(sql_cmd_global).fetchall()

			if len(result_global) <= 1: # wait till more seconds if db is not responding or pcc is inActive.
				wait_time = True
				start_time = time.time()
				while wait_time:
					time.sleep(2)
					result_global = connected_connection.execute(sql_cmd_global).fetchall()
					if len(result_global) == 2:
						connection.close()
						return Response(result_global, status = status.HTTP_201_CREATED)
					if time.time() - start_time > 5:
						connection.close()
						return Response({"Command ID ": command_id, "Message ": "PCC is not responding or is not Activated"})
			connected_connection.close()
			return Response(result_global, status=status.HTTP_201_CREATED)
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			error = f"Error {e}"
			return Response({error:1})

	def call_prco_mssql(self, connected_connection, sql_proc, *args): # stored procedure for mssql
		transaction = connected_connection.begin()
		sql = """SET NOCOUNT ON;
			DECLARE @ret int
			EXEC @ret = %s %s
			SELECT @ret""" % (sql_proc, ','.join(['?'] * len(args)))
		result = connected_connection.execute(sql, args).fetchone()[0]
		transaction.commit()
		return int(result)


# To delete the job from repository
class ProfileDeleteView(viewsets.ModelViewSet):

	serializer_class = ProductionDeleteSerializer	# inherited member variable

	def create(self, request, *args, **kwargs): # post method to delete job from repository.
		if len(request.GET) != 1:
			return Response({"Message": "Wrong number of parameters."})
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		oid = self.request.GET.get('oid',None)
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		transaction = begin_transaction(connection)
		message = delete_object(connection, oid)
		commit_transaction(transaction)
		connection.close()
		return Response({"Message": message})


class JobProfileUpdate(viewsets.ModelViewSet): # update a job in repository job

	serializer_class = JobUpdateSerializer # serializer class used for update view for job.

	def create(self, request, *args, **kwargs): # post method for update job
		if len(request.GET) != 1:
			return Response({"Message": "Wrong number of parameters."})
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		serializer = self.get_serializer(data=request.data)
		oid = self.request.GET.get('oid', None)
		result = None
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		if not serializer.is_valid(): # checking if given json data with request is valid or not.
			return Response({"Message":"Invalid JSON input."})

		serialized_data = serializer.data
		dependency = None
		if serialized_data["Dependencies"] is not None:
			dependency = serialized_data["Dependencies"]
		permissions = {"Permissions":serialized_data["PERMISSIONS"]}
		del serialized_data["Dependencies"] #todo: Unnecessary, delete later. Change serializer then as well
		del serialized_data["PERMISSIONS"]	#todo: Unnecessary, delete later. Change serializer then as well
		query = str(serialized_data).replace("'",'"').replace("True","true").replace("False","false")
		try:
			transaction = begin_transaction(connection)
			return_code = update_job(connection, oid, query) # call the function inside view to execute procedure.
			if return_code in error_codes:
				return Response(error_codes[return_code])
			if dependency is not None:
				delete_all_dependencies(oid, connection)
				converted_json = json_dependency_conversion(dependency)
				result = add_dependencies(converted_json, connection, oid)
				if result != 0:
					transaction.rollback()
					return Response({"Message":"Error Occured while Updating Please check your JSON format and confirm the dependency passed to job is correct."})
			if permissions['Permissions'] is not None:
				return_code = add_permissions(connection,oid,str(permissions["Permissions"]).replace("'",'"').replace("True","true").replace("False","false"))
				if return_code != 0:
					transaction.rollback()
					return Response({"Message":"Error Occured while updating Permissions, Rolling Back."})
			commit_transaction(transaction)
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({'Message': "Error Occured while Updating Please check your JSON format and confirm the dependency passed to job is correct."})
		connection = connection.close()
		time.sleep(3)
		return Response({'Message':return_code})


class JobProfileCreate(viewsets.ModelViewSet): # create new job in repository

	serializer_class = JobUpdateSerializer

	def create(self, request, *args, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		serializer = self.get_serializer(data=request.data)
		oid = self.request.GET.get('oid')
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		if not serializer.is_valid():
			return Response({"Message":"Invalid JSON input."})

		permissions = ''
		dependency = ''
		os_name = ''
		os_list = ["UNIX","WINDOWS","R3","BW","ISKV","OS400","HS5000","VMS","BS2000","CONTROL","WEBAPX","CLIENTS"]
		serialized_data = serializer.data
		for key in serialized_data:
			if key in os_list:
				os_name = key
		if os_name == '':
			return Response({"Message":"Can not create job without OS."})
		if serialized_data["Dependencies"] is not None:
			dependency = serialized_data["Dependencies"]
		permissions = {"Permissions":serialized_data["PERMISSIONS"]}
		del serialized_data["PERMISSIONS"]
		del serialized_data["Dependencies"]
		job_name = serialized_data["Object"]["OID_NAME"]
		query = str(serialized_data).replace("'",'"')

		try:
			transaction = begin_transaction(connection)
			return_code, new_oid = create_job(connection, oid, os_name, job_name, query)
			if return_code in error_codes:
				transaction.rollback()
				return Response({"Message":error_codes[return_code]})
			if dependency is not '':
				converted_json = json_dependency_conversion(dependency)
				result = add_dependencies(converted_json, connection, new_oid)
				if result != 0:
					transaction.rollback()
					return Response({"Message":"Error While Creating job, rolling Back."})
			if (permissions["Permissions"] is not None):
				time.sleep(2)
				permissions_str = str(permissions["Permissions"]).replace("'",'"').replace("True","true").replace("False","false")
				result = add_permissions(connection, new_oid, permissions_str)
				if result is None:
					transaction.rollback()
					return Response({"Message":"Error While Creating job, Rolling Back."})
			commit_transaction(transaction)
			connection = connection.close()
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Error while creating Job")
			transaction.rollback()
			return Response({"Message":"Error Occured While creating Job, Rolling Back."})
		return Response({"Message": return_code})


class GetJobProfileView(APIView): # see the job profile from repository

	def get(self, request):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		oid = request.GET.get('oid')
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", '')
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		try:
			json_data = get_profile_view_json(oid, connection)
			json_dict = json.loads((json_data[0]))
			json_dict['PROJECT'] = json_dict['PATH']
			del json_dict['PATH']
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			connection = connection.close()
			return Response({"Message": "Error While getting object."})
		if "DEPENDENCIES" in json_dict:
			if (len(json_dict["DEPENDENCIES"]["JOB"]) is 0) and ('DEPENDENCIES' in json_dict):
				del (json_dict["DEPENDENCIES"]["JOB"])
			if (len(json_dict["DEPENDENCIES"]["FILE"]) is 0) and ('DEPENDENCIES' in json_dict):
				del (json_dict["DEPENDENCIES"]["FILE"])
			if (len(json_dict["DEPENDENCIES"]["EVENT"]) is 0) and ('DEPENDENCIES' in json_dict):
				del (json_dict["DEPENDENCIES"]["EVENT"])
			if (len(json_dict["DEPENDENCIES"]) is 0) and ('DEPENDENCIES' in json_dict):
				del json_dict["DEPENDENCIES"]
		if len(json_dict["PERMISSIONS"]) is 0:
			del json_dict["PERMISSIONS"]
		if "AT_RULES" in json_dict:
			RULES = get_at_rules(json_dict)
			json_dict["AT_RULES"] = RULES
		connection = connection.close()
		return Response(json_dict)


class StatusView(APIView): # to view the job, controler and agents status

	def get(self, request, **kwargs):
		state = request.GET.get('status')
		if state is 'H':
			state = ''
		sess = return_session(request)
		if sess is None:
			return Response({"Message":"Invalid username/password"})
		path = request.get_full_path()
		size = 0
		print(path)
		if path == "/apx_api/v1/production/jobs/status/":
			obj = ''
			if state == '*' or state == None:
				union_stat = """ select REAL_STATE as state, COUNT(REAL_STATE) from PCCDBA.CI_PRD_PROF_USR where HOLD = 'No' Group by REAL_STATE
							union
							select HOLD as state, COUNT(HOLD) from PCCDBA.CI_PRD_PROF_USR where HOLD ='Yes' Group by HOLD"""
				status =  sess.execute(union_stat).fetchall()
				dict_state = {}
				for i in range(len(status)):
					if status[i][0] == ' ' or '':
						dict_state["_"] = status[i][1]
						size += status[i][1]
					elif status[i][0] == 'Yes':
						dict_state["H"] = status[i][1]
						size += status[i][1]
					else:
						dict_state[status[i][0]] = status[i][1]
						size += status[i][1]
				return  Response({"Size":size,"Job Status":dict_state})
			else:
				sq_query = "select COUNT(*) FROM PCCDBA.CI_PRD_PROF_USR where REAL_STATE = '%s'"%(state)
				return_statement = sess.execute(sq_query).fetchone()[0]
				return  Response({"Job Status":return_statement})
		elif path == "/apx_api/v1/production/control/status/":
			pcc_state = "select * FROM PCCDBA.CI_CTL_STAT_USR"
			pcc_state_query = sess.execute(pcc_state).fetchone()
			sess = sess.close()
			local_time='Not Found For this DB'
			local_time = str(pcc_state_query[5].replace(tzinfo=timezone.utc).astimezone(tz=None))
			local_time = local_time[0:local_time.rfind('.')]
			return Response({"Environment": pcc_state_query[0], "State":pcc_state_query[1], "Active":pcc_state_query[2], "Version":pcc_state_query[3],"Last Action":local_time})
		elif path == "/apx_api/v1/production/agents/":
			rcs_query = sess.query(CriticalRcsORM).all()
			rcs_serializer = CriticalRcsSerializer(rcs_query, many=True).data
			sess = sess.close()
			return Response(rcs_serializer)
		else:
			#sess = return_connection(self.request)[0].connect()
			filter = request.GET.get("filters")
			query_sql=f'Select * From PCCDBA.REST_CRITICAL_RCS Where {filter}'
			obj = sess.execute(query_sql).fetchall()
			sess = sess.close()
			return Response({"Size":len(obj),"RCSs":obj})
		return Response({"Message":"Error Found"})


class AddDependencyView(viewsets.ModelViewSet): # add new dependency in

	serializer_class = AddDependencySerializer

	def create(self, request, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		oid = request.GET.get('oid')
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]

		serializer = self.get_serializer(data=request.data)
		try:
			if not serializer.is_valid():
				return Response({"Message":"Invalid JSON input."})

			dependency_json = (serializer.validated_data.get('DEPENDENCIES'))
			if "JOB" in dependency_json:
				convert_dependency_name_into_oid(dependency_json, connection)
			transaction = begin_transaction(connection)

			converted_json = dependency_json(dependency_json)
			result = add_dependencies(converted_json, connection, oid)
			if result != 0:
				return Response({"Message":"Error, check Dependency, rolling Back."})

			commit_transaction(transaction)
			return Response({"Message":"Dependency Have Been Added."})

		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error While updating dependencies, rolling back."})
		# connection.close() missing?


class DeleteDependencyView(viewsets.ModelViewSet):

	def create(self, request, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		oid = self.request.GET.get('oid',None)
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		transaction = begin_transaction(connection)
		return_code = delete_all_dependencies(connection, oid)
		commit_transaction(transaction)
		return Response({"Message": return_code})


class ControlLogview(APIView):

	pagination_class = LimitOffsetPagination

	def get(self, request, **kwargs):
		sess = return_session(request)
		if sess is not None:
			controllog_object = sess.query(ControlLogORM).all()
			controlobject_serializer = ControlLogSerializer(controllog_object, many=True).data
			return Response(controlobject_serializer)
		else:
			return Response({"Invalid Username/Password or Link Broken"})


class GetJobProfilesView(APIView): # can be used for objects/ and with like statment can be used as objects/recursive

	def get(self, request):
		sess = return_session(request)
		if sess is not None:
			query = request.GET.get('filters')
			if(request.path == '/apx_api/v1/repository/jobs/recursive/') and (query is None):
				execute_statment = sess.query(RepositoryJobs).all()
			elif (query is not None):
				if check_sql_injection(query):
					return Response({"Message":"Given Query is not supported."})
				sql_statment = "{0}".format(query[1:len(query)-1])
				print(query)
				execute_statment = sess.query(RepositoryJobs).filter(text(query.replace('"', "'"))).all()
			else:
				return Response({"Message":"Provided URL is not Correct, Please Give jobs/recursive/ or Jobs/?filter"})
			serializer_data = GetJobProfileSerializer(execute_statment, many=True).data
			if len(execute_statment) > 0:
				return Response(serializer_data)
			else:
				return Response({"Message":"No Job Found"}, status=status.HTTP_404_NOT_FOUND)
		else:
			return Response({"Message":"Invalid Username/Password."})


class InAppView(APIView):

	def get(self, request,**kwargs):
		try:
			#db = al.create_engine('sqlite:///C:\\SQLiteStudio-3.2.1\\SQLiteStudio\\apxdblite') on testing device
			db = al.create_engine('sqlite:///C:\\tmp\\sqllite\\SQLiteStudio-3.2.1\\SQLiteStudio\\APMTest.db') # in apx_1 exact folder
			connection = db.connect()
			Session = sessionmaker(bind=connection)
			session = Session()
			filter = request.GET.get('filters')
			lit_statment = f"select * from filterTable where {filter}"
			if filter == 'all' or filter == '*'or filter == None:
				lit_statment = "select * from filterTable"
			result = session.execute(lit_statment)
			result = result.fetchall()
			json_data = InAppSerializer(result).data
			connection = connection.close()
			return Response({"data":result})

		except SQLAlchemyError as e:
			return Response({"Message":"Error Occured in Server"})

	def post(self, request, *args, **kwargs):
		try:
			db = al.create_engine('sqlite:///C:\\tmp\\sqllite\\SQLiteStudio-3.2.1\\SQLiteStudio\\APMTest.db?check_same_thread=False')
			connection = db.connect()
			json_data = {
				"name":"",
				"URL":"",
				"response":"",
				"condition":"",
				"message":"",
				"describtion":"",
				"predicate":"",
				"counter":""
				}
			for key in request.data:
				if key in json_data:
					json_data[key] = request.data[key]

			stment = """
					INSERT INTO filterTable (name, URL, response, condition, message, describtion, predicate, counter) VALUES
					("{0}", "{1}", "{2}", "{3}","{4}","{5}","{6}","{7}")""".format(json_data['name'],json_data['URL'],json_data['response'],json_data['condition'],json_data['message'],json_data['describtion'],json_data['predicate'],json_data['counter'])
			connection.execute(stment)
			connection = connection.close()
			return Response({"Message":"Data Posted."})

		except Exception as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error Occured in Server"})


class CreateProjectView(viewsets.ModelViewSet):

	serializer_class = JobUpdateSerializer

	def create(self, request, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		oid = request.GET.get('oid') # in case of OID instead of location name
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			connect = connection.close()
			return Response({"Message":"Json Error, Json data not correct."})

		dependency = None
		serialized_data = serializer.data
		permissions = None
		project_name = None
		if ("Dependency" in serialized_data) and (serialized_data["Dependency"] is not None):
			dependency = serialized_data["Dependency"]
			del serialized_data["Dependency"]
		if ("PERMISSIONS" in serialized_data) and (serialized_data["PERMISSIONS"] is not None):
			permissions = serialized_data["PERMISSIONS"]
			del serialized_data["PERMISSIONS"]
		if ("OID_NAME" in serialized_data["Object"]):
			project_name = serialized_data["Object"]["OID_NAME"]
		body_json = str(serialized_data).replace("'",'"')
		try:
			return_code = 0
			transaction = begin_transaction(connection)
			if "net/create" in request.path:
				return_code, new_oid = create_net_project(connection, oid, project_name)
			elif "project/create" in request.path:
				return_code, new_oid = create_project(connection, oid, project_name)
			elif ("net/update" in request.path) or ("project/update" in request.path):
				if project_name is not None:
					return_code = change_object_name(connection, oid, project_name)
			if return_code != 0 and return_code in error_codes:
				return Response({"Message":error_codes[return_code]})
			elif return_code == 0:
				if dependency is not None:
					converted_json = json_dependency_conversion(dependency)
					result = add_dependencies(connection, new_oid, converted_json)
					for key in result:
						if result[key] != 0:
							connect = connection.close()
							return Response({"Message":"Error While Creating job, Rolling Back."})
				if permissions is not None:
					result = add_permissions(connection, new_oid,str(permissions).replace("'",'"').replace("True","true").replace("False","false"))
					if result is None:
						connect = connection.close()
						return Response({"Message":"Error While Creating project, Rolling Back."})
			else:
				connect = connection.close()
				return Response({"Message":"Error While Creating/updating Project, Project with same name already exist or Permission Limmited. Rolling Back."})
			commit_transaction(transaction)
			connect = connection.close()
			return Response({"Message":"Success"})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			connect = connection.close()
			return Response({"Message":"Unknown Error Occured please retry."})


class GetObjectView(APIView): # with  objects/folder name

	def get(self, request):
		connection, sess = new_Session_raw_connection(request)
		if connection is None or sess is None :
			return Response({"Message":"Invalid username/password."})
		project_oid = request.GET.get('oid')
		name = self.request.GET.get('name', None)
		filters = request.GET.get('filters')
		result = ''
		if project_oid is None:
			project = self.request.GET.get('project', None)
			if project is not None:
				project = project.replace('"', '').replace("'","")
				if project.endswith("/"): project = project[:-1]
				print(project)
				found_oids = find_objects(connection, project)
				if len(found_oids) == 0:
					return Response({"Message":"object not found with given name"})
				if len(found_oids) > 1:
					return Response({"Message":"{} objects found with given name, Use instead objects/recursive/".format(len(found_oids))})
				project_oid = found_oids[0]
				result = get_object_view(project_oid, connection)
			elif name is not None:
				if name is not None:
					name = name.replace('"', '').replace("'","")
					result = get_objects_view(name, connection)

			elif filters is not None:
				sql = convert_sql_queries_rep(filters)
				result = sess.query(RepositoryJobs).filter(text(sql[1:len(sql)-1])).all()				
				pass
			else:
				result = sess.query(ClientORM).all()
				result = ClientSerializer(result, many=True).data
				return Response({"Clients":result})
		elif project_oid is not None:
			result = sess.query(RepositoryJobs).filter(RepositoryJobs.OID == project_oid)
		if (result == '') or (len(result)==0): return Response({"Message":"No Result Found with given URL"})
		"""output_dict = {"OID":None, "NAME":None, "TYPE":None, "PROJECT":None, "DESCRIPTION":None}
		result_list = []
		for i in range(len(result)):
			output_dict["OID"] = '0x'+ (result[i][0]).hex()
			output_dict["NAME"] =  result[i][1]
			output_dict["TYPE"] =  result[i][2]
			output_dict["PROJECT"] =  result[i][3]
			output_dict["DESCRIPTION"] =  result[i][4]
			result_list.append(output_dict.copy())

		data = (json.dumps(result_list)).replace("\'","\"")
		data = json.loads(data)"""
		data = GetJobProfileSerializer(result, many=True).data
		return Response(data)


class CreateClient(viewsets.ModelViewSet):

	serializer_class = JobUpdateSerializer

	def create(self, request, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			return Response({"Message":"Invalid JSON input."})
		oid = request.GET.get("oid")
		if (oid is None) and ("client/update" in request.path):
			found_oids = find_objects(connection, self.request.GET.get('name', None))
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		try:
			serializer_data = str(serializer.data).replace("'",'"')
			print(serializer_data)
			name = request.data["NAME"]
			print(name)
			transaction = begin_transaction(connection)
			if "client/create" in request.path:
				return_code, new_oid = create_client(connection, name)
			elif "client/update" in request.path:
				return_code = change_object_name(connection, oid, name)
			if return_code == 0:
				commit_transaction(transaction)
				connect = connection.close()
				return Response({"Message": "Success"})
			else:
				connect = connection.close()
				return Response({"Message":"Error Occured while creating or updating client: {}".format(error_codes[return_code])})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error Occured, Rolling Back."})


class JobHistory(APIView):

	def get(self, request,**kwargs):
		connection = return_session(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		filters = request.GET.get("filters")
		sql_query = "SELECT JOBID as JOBNUMBER, RUN_NO, JOBNAME, STATE, REAL_STATE AS STATE_1, ACTUAL_START, ACTUAL_RUNTIME AS RUNTIME, SPOOL from PCCDBA.CI_PRD_HIST_USR"
		if filters is not None:
			if check_sql_injection(filters):
				return Response({"Message":"Unsupported sql statment give."})
			sql_query = sql_query + " WHERE " + filters[1:len(filters)-1]
			print(sql_query)
		execute_query = connection.execute(sql_query).fetchall()
		connection = connection.close()
		return Response(execute_query)


class JobHistoryDetail(APIView):

	def get(self,request, **kwargs):
		job_object = []
		try:
			connection = new_connection(request)
			if connection is None:
				return Response({"Message":"Invalid username/password."})
			jobkey = request.GET.get("jobkey")
			run_num = request.GET.get("run_no")
			if (jobkey is None) or (run_num is None):
				return Response({"Message":"Please provide correct jobkey and run number"})
			job_object = get_job_history_detail(jobkey, run_num, connection)
			connection.close()
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Couldn't get job history detail")
			connection.close()
			return Response(e)
		print(job_object)
		connect = connection.close()
		if len(job_object) == 0 or len(job_object[0]) == 0: #todo: this could be more elegant
			Response({"Message":"Error No Job Found."})
		data = json.loads(job_object[0][0])
		print(data)
		return Response(data)


class GetJobSpool(APIView):

	def get(self, request, **kwargs):
		connection = return_session(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})

		name = request.GET.get("name")
		key = request.GET.get("jobkey")
		run_num = request.GET.get("run_num")
		sql_query = "SELECT SPOOL FROM PCCDBA.SPOOL_LIST where JOBKEY = {0} and RUN_NO = {1} and JOBNAME = {2}".format(key,run_num,name)
		print(sql_query)
		execute_query = connection.execute(sql_query).fetchone()
		print(execute_query)
		connection = connection.close()
		files = open("C:\\Users\\Administrator\\Desktop\\task.txt",'rb')
		print(files)
		content = 'any string generated by django'
		response = Response(content, content_type='text/plain')
		response['Content-Disposition'] = 'attachment; filename={0}'.format(files)
		file_response = FileResponse(files)
		return file_response


class Permissions(viewsets.ModelViewSet):

	serializer_class = PermissionsSerializer

	def create(self, request, **kwargs):
		connection = new_connection(request)
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		oid = request.GET.get('oid')
		if oid is None:
			name = self.request.GET.get('name')
			name = name.replace('"', '').replace("'", "")
			found_oids = find_objects(connection, name)
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]

		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			return Response({"Message":"Invalid JSON input."})
		try:
			permission_json = (serializer.validated_data.get('PERMISSIONS'))
			transaction = begin_transaction(connection)
			result = add_permissions(connection, oid,str(permission_json).replace("'",'"').replace("True","true").replace("False","false"))
			if result in error_codes:
				return Response(error_codes[result])
			if result is None:
				connection = connection.close()
				return Response({"Message":"Error, user Permissions already have,rolling Back."})
			commit_transaction(transaction)
			connection = connection.close()
			return Response({"Message":"Permissions Have Been Added."})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error While updating Permissions, rolling back."})


class TokenTable(APIView):

	def post(self, request,**kwargs):
		try:
			#db = al.create_engine('sqlite:///C:\\Users\\aneel\\Desktop\\apxdblite') used in local machine for testinf
			db = al.create_engine('sqlite:///C:\\tmp\\sqllite\\SQLiteStudio-3.2.1\\SQLiteStudio\\APMTest.db')
			connection = db.connect()
			Session = sessionmaker(bind=connection)
			session = Session()
			serializer = TokenTableSerializer(request.data).data
			serialized_data = serializer
			query = ("select Token from TokenTable where Token='{0}'".format(serialized_data['Token']))
			result_sess = connection.execute(query).fetchone()
			if result_sess is None:
				insert_query = """INSERT INTO TokenTable (Token,Subscription, New)
								VALUES
								("{0}","{1}",{2})""".format(serialized_data['Token'],serialized_data['Subscriptions'],serialized_data['New'])

				transaction = connection.begin()
				execute_insert = connection.execute(insert_query)
				transaction.commit()

			update_query="""UPDATE ToKenTable
							SET Subscription = '{0}',
								New = {1}
							WHERE Token = {2};""".format(serialized_data['Subscriptions'],serialized_data['New'],serialized_data['Token'])

			transaction = begin_transaction(connection)
			execute_insert = connection.execute(update_query)
			commit_transaction(transaction)
			result="Database Updated."
			connection = connection.close()
			return Response({"data":result})

		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error Occured in Server"})

	def get(self, request):
		return Response({"Message":"Not Allowed"})


class DeletePermissionView(viewsets.ModelViewSet):

	def create(self, request, **kwargs):
		results = {9001:"Permission Account Not Found in Object","Done":"Account Deleted."}
		connection = new_connection(self.request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		oid = self.request.GET.get('oid',None)
		if oid is None:
			found_oids = find_objects(connection, self.request.GET.get('name', None))
			if len(found_oids) == 0:
				return Response({"Message":"object not found with given name"})
			if len(found_oids) > 1:
				return Response({"Message":"{} objects found with given name".format(len(found_oids))})
			oid = found_oids[0]
		account = self.request.GET.get('account')
		account_oid = find_user(connection, account)
		if account_oid is None:
			return Response({"Message":"User/Accunt Error"})
		try:
			transaction = begin_transaction(connection)
			return_code = delete_permission(connection, oid, account)
			commit_transaction(transaction)
			return Response({"Message":results[return_code]})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Error can not delete Permission"})


class CreateTokenRequest(APIView):

    def get(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        try:
            api_key, key = APIKey.objects.create_key(name=auth_header)
            content = {'message': 'API KEY CREATED',
                       'Key':str(key)
                       }
            return Response(content)
        except Exception as e:
            print(e)
            content = {'message': 'API KEY ALREADY IN DB'}
            return Response(content)


class GetUserFilter(APIView): # Needed to be implemented from Monday.

	def get(self, request):
		connection = return_session(request)
		if connection is None:
			return Response({"Message":"Invalid username/password."})
		try:
			sess = connection
			user = current_user(request)
			if user is None:
				return Response({"Message":"User Could not be Found."})
			objs = sess.query(UserFilters).filter(UserFilters.OID_NAME == user).all()
			serializer_values = UserFilterSerializer(objs,many=True).data
			sess = sess.close()
			return Response({"data":serializer_values})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Unexpected Error Occured."})


class CreateUserFilter(viewsets.ModelViewSet):

	def create(self, connection):
		connection = new_connection(self.request)
		if not ('FILTER_NAME' in self.request.data and 'REQUEST' in self.request.data):
			return Response({"Message":"Missing Parameters in body"})
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		try:
			transaction = begin_transaction(connection)
			user = current_user(self.request) if 'USER' not in self.request.data else self.request.data['USER']
			filter_name = self.request.data['FILTER_NAME']
			filter_request = self.request.data['REQUEST']
			return_code= add_custom_filter(connection, user,filter_name, filter_request)
			if return_code != 0:
				transaction.rollback()
				connection = connection.close()
				return Response({"Message":"Filter could not be created."})
			commit_transaction(transaction)
			return Response({"Message":"Filter was successfully created."})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Unexpected Error Occurred."})


class DeleteUserFilter(viewsets.ModelViewSet):

	def create(self, connection):
		connection = new_connection(self.request)
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		try:
			transaction = begin_transaction(connection)
			user_name = current_user(self.request)
			filters = self.request.data
			if len(filters) > 1: return Response({"Message":"Please provide only one filter name."})
			filter_name = (list(filters.values()))[0]
			print(filter_name)
			if filter_name is None:
				return Response({"Message":"Please provide the name of the filter you want to delete."})
			filter_name = filter_name.replace('"', '').replace("'", "")
			return_code = delete_custom_filter(connection, user_name, filter_name)
			if return_code != 0:
				transaction.rollback()
				connection = connection.close()
				return Response({"Message":"Filter could not be deleted."})
			commit_transaction(transaction)
			return Response({"Message":"Filter was deleted successfully."})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Unexpected Error Occured."})


class DeleteAllUserFilters(viewsets.ModelViewSet):

	def create(self, connection):
		connection = new_connection(self.request)
		if connection is None:
			return Response({"Message":"Invalid username/password"})
		try:
			transaction = begin_transaction(connection)
			user = self.request.GET.get('user')
			if user is None:
				return Response({"Message":"Please provide a user name."})
			user = find_user(connection,user)
			return_code = delete_all_filters_for_user(connection, user)
			if return_code != 0:
				transaction.rollback()
				connection = connection.close()
				return Response({"Message":"Filters could not be deleted."})
			commit_transaction(transaction)
			return Response({"Message":"All of {}'s' filters were deleted successfully.".format(user)})
		except SQLAlchemyError as e:
			log_exception(e, getframeinfo(currentframe()), "Database error")
			return Response({"Message":"Unexpected Error Occured."})

class DeleteTokenRequest(APIView):
    
    def get(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        try:
            api_key = APIKey.objects.get(oid=auth_header)
            APIKey.objects.filter(oid=auth_header).delete()
            content = {'message': 'API KEY DELETED FROM DB'}
            return Response(content)
        except:
            content = {'message': 'NO KEY FOUND'}
            return Response(content)                   
        
class SchedulerView(APIView):
    
	def get(self, request,**kwargs):
		if len(request.GET) > 1:
			return Response({"Message": "Wrong number of parameters."})
		connection, sess = new_Session_raw_connection(request)
		if connection is None or sess is None :
			return Response({"Message":"Invalid username/password."})
		filters = request.GET.get('filters')
		result = None
		obj = None
		if filters is not None:
			try:
				obj = sess.query(Scheduler).filter(text(f"{filters}")).all()
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Message":"Databse error"}, status=status.HTTP_404_NOT_FOUND)
			finally:
				sess.close()
		else:
			try:
				obj = sess.query(Scheduler).order_by(desc(Scheduler.SCHEDULE_DATE)).order_by(desc(Scheduler.SCHEDULE_NO)).all()
				sess.close()
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Databse error"}, status=status.HTTP_404_NOT_FOUND)
		if len(obj) == 0:
			return Response({"No object found"}, status=status.HTTP_404_NOT_FOUND)
		serializer_data = SchedulerSerializer(obj, many=True).data
		return Response({"Schedules":serializer_data})


class GetObjectsRecursive(APIView): # can be used for objects/ and with like statment can be used as objects/recursive

	def get(self, request):
		sess = return_session(request)
		if len(request.GET) > 1:
			return Response({"Message":"Wrong Number of Parameters."})
		if sess is not None:
			name = request.GET.get('name')
			project = request.GET.get('project')
			filters = request.GET.get('filters')
			if(request.path == '/apx_api/v1/repository/objects/recursive/') and (len(request.GET) == 0):
				result = sess.query(ClientORM).all()
				result = ClientSerializer(result, many=True).data
				return Response({"Clients":result})
			elif (project is not None):
				if check_sql_injection(project):
					return Response({"Message":"Given Query is not supported."})
				project = project.replace('"', '').replace("'","")
				if not project.endswith("/") and project.find("/") != -1:
					project = project + "/"
				sql_statment = f"PATH like '%{project}%'"
				print(sql_statment)
				execute_statment = sess.query(RepositoryJobs).filter(text(sql_statment)).all()
			elif (name is not None):
				name = name.replace('"', '').replace("'","")
				execute_statment = sess.query(RepositoryJobs).filter(RepositoryJobs.OID_NAME == name).all()
			elif filters is not None:
				sql = convert_sql_queries_rep(filters)
				execute_statment = sess.query(RepositoryJobs).filter(text(sql[1:len(sql)-1])).all()
			else:
				return Response({"Message":"Provided URL is not Correct, Please Give jobs/recursive/ or Jobs/?filter"})
			serializer_data = GetJobProfileSerializer(execute_statment, many=True).data
			if len(execute_statment) > 0:
				return Response(serializer_data)
			else:
				return Response({"Message":"No Job Found"}, status=status.HTTP_404_NOT_FOUND)
		else:
			return Response({"Message":"Invalid Username/Password."})


class SchedularProgressView(APIView): # to be implemented.

	def get(self, request, **kwargs):
		if len(request.GET) > 1:
			return Response({"Message": "Wrong number of parameters."})
		connection, sess = new_Session_raw_connection(request)
		if connection is None or sess is None :
			return Response({"Message":"Invalid username/password."})
		filters = request.GET.get('filters')
		result = None
		obj = None
		if filters is not None:
			try:
				obj = sess.query(SchedularProgress).filter(text(f"{filters}")).all()
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Databse error"}, status=status.HTTP_404_NOT_FOUND)
			finally:
				sess.close()
		else:
			try:
				obj = sess.query(SchedularProgress).all()
	
			except SQLAlchemyError as e:
				log_exception(e, getframeinfo(currentframe()), "Database error")
				return Response({"Databse error"}, status=status.HTTP_404_NOT_FOUND)
		if len(obj) == 0:
			return Response({"Message":"No object found"}, status=status.HTTP_404_NOT_FOUND)
		serializer_data = SchedulerProgresSerializer(obj, many=True).data
		return Response({"Schedules":serializer_data})
		

		