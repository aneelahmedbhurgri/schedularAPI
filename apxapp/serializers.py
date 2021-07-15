from rest_framework import serializers
import urllib.parse
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
import xmltodict
#from APX.Orm import JobDetail, Job

class ProductionGetSerializer(serializers.Serializer): # this serializer is used to convert production Get with list objects into JSON

	JOBNUMBER = serializers.SerializerMethodField('get_jobid')
	RUN_NO = serializers.IntegerField(read_only=True,default=0)

	NAME = serializers.SerializerMethodField('get_name')
	STATE_1 = serializers.SerializerMethodField('get_state1')
	EARLIEST_START = serializers.DateTimeField(read_only=True,default='Null')
	OID = serializers.SerializerMethodField('get_oid')
	RCS = serializers.CharField(read_only=True,default='Null')
	PROJECT = serializers.SerializerMethodField('get_path')
	DESCRIPTION = serializers.CharField(read_only=True, default='Null')
	COND_CODE = serializers.CharField(read_only=True, default='Null')
	#ACTUAL_START = serializers.SerializerMethodField('get_Date')
	OS = serializers.CharField(read_only=True, default='Null')
	SCHEDULE_KEY = serializers.DecimalField(read_only=True,max_digits=17, decimal_places=14, default = 'NULL')
	def get_oid(self, obj):
		return_statment = '0x'+ (obj.OID).hex()
		return return_statment

	def get_jobid(self,obj):
		return obj.JOBKEY

	def get_state1(self, obj):
		return obj.STATE1

	def get_path(self, obj):
		return obj.PATH

	def get_Date(self, obj):
		if obj.ACTUAL_START is None:
			return obj.ACTUAL_START
		date =  str(obj.ACTUAL_START)[0:int(str(obj.ACTUAL_START).rfind(':'))]
		return date

	def get_name(self, obj):
		return obj.JOBNAME

class ProductionDeleteSerializer(serializers.Serializer): # dummy serializer used in DeleteJob view

	JOBID = serializers.IntegerField(read_only=True, default=0)
	REAL_STATE = serializers.CharField(read_only=False, default='NULL')
	JOBNAME = serializers.CharField(read_only=True, default='NULL')
	OID = serializers.CharField(read_only=True, default='NULL')


class DependenciesList(serializers.Serializer):
	DEPENDENCY = serializers.CharField(read_only=False, default='NULL')
	CODE = serializers.CharField(read_only=False, default='NULL')
	STATE = serializers.CharField(read_only=False, default='NULL')


class JobUpdateSerializer(serializers.Serializer): # this serializer is used in Creating and Updating Job Profiles

	NAME = serializers.CharField(default=None)
	PATH = serializers.CharField(default=None)
	QUEUE = serializers.CharField(default=None, allow_null=True)
	RCS = serializers.CharField(default=None)
	USERNAME = serializers.CharField( default=None)
	COMMAND = serializers.CharField(default=None)
	SEVERITY= serializers.CharField( default=None)
	SPOOL_FILTER= serializers.CharField(default=None)
	ARCHIVE_FORMAT= serializers.CharField(default=None)
	ENVIRONMENT= serializers.CharField(default=None)
	DUMMY_COMMAND= serializers.CharField(default=None)
	AT_RULES= serializers.DictField(default=None)
	MAX_REDO= serializers.CharField(default=None)
	OCQ_MODE= serializers.CharField(default=None)
	VALID_TO= serializers.CharField(default=None)
	VALID_FROM= serializers.CharField(default=None)
	PRIORITY= serializers.CharField(default=None)
	CALCULATE=serializers.CharField(default=None)
	MAX_CANCEL=serializers.CharField(default=None)
	MAX_RUNTIME=serializers.CharField(default=None)
	LATEST_END=serializers.CharField(default=None)
	LATEST_START=serializers.CharField(default=None,allow_null=True)
	EARLIEST_START=serializers.CharField(default=None,allow_null=True)
	STATE2=serializers.CharField(default=None,allow_null=True)
	CALENDAR = serializers.CharField(default=None,allow_null=True)
	TYPE_ACTIVE = serializers.CharField(default=None,allow_null=True)
	TYPE_INHERIT_TC = serializers.CharField(default=None)
	TYPE_INHERIT_TD = serializers.CharField(default=None)
	TYPE_INHERIT_ACTIVE = serializers.CharField(default=None)
	TYPE_INHERIT_VALID = serializers.CharField(default=None)
	TYPE_INHERIT_EARLIEST = serializers.CharField(default=None)
	TYPE_INHERIT_LATEST = serializers.CharField(default=None)
	TYPE_INHERIT_PERIOD = serializers.CharField(default=None)
	TYPE_INHERIT_DEPENDENCY = serializers.CharField(default=None)
	TYPE_INHERIT_CONSTRAINT = serializers.CharField(default=None)
	TYPE_WAIT_FOR_CHILDS = serializers.CharField(default=None)
	TYPE_HAS_CHILDS = serializers.CharField(default=None)
	TYPE_IS_WORKFLOW = serializers.CharField( default=None)
	TYPE_INCOMPLETE = serializers.CharField(default=None)
	TYPE_EXCLUDE_DATE = serializers.CharField(default=None)
	TYPE_SET_DUMMY_DATE = serializers.CharField(default=None)
	TYPE_UNSET_DUMMY_DATE = serializers.CharField(default=None)
	#DEPENDENCY = serializers.CharField(read_only=False, default='NULL')
	OP = serializers.CharField(default=None)
	COND_CODE = serializers.CharField(default=None)
	CODE = serializers.CharField(default=None)
	STATE = serializers.CharField(default=None)
	UNIX = serializers.DictField(default=None)
	WINDOWS = serializers.DictField(default=None)
	WINNT = serializers.DictField(default=None)
	#Permission =Serializers.DictField(default=None)
	DEPENDENCIES = serializers.DictField(default=None)
	R3 = serializers.DictField(default=None)
	BW = serializers.DictField(default=None)
	ISKV = serializers.DictField(default=None)
	OS400 = serializers.DictField(default=None)
	HS5000 = serializers.DictField(default=None)
	VMS = serializers.DictField(default=None)
	BS2000 = serializers.DictField(default=None)
	CONTROL = serializers.DictField(default=None)
	WEBAPX = serializers.DictField(default=None)
	CLIENTS = serializers.DictField(default=None)
	PERMISSIONS = serializers.ListField(default=None)
	OID_NAME = serializers.CharField(default=None)

	def to_representation(self, instance):
		rep = super().to_representation(instance)
		new_rep = {"Profile":{}, "Object":{}, "Dependencies":None, "PERMISSIONS":None}
		os_list = ["UNIX","WINDOWS","R3","BW","ISKV","OS400","HS5000","VMS","BS2000","CONTROL","WEBAPX","CLIENTS","WINNT"]
		profile = {}

		for key, value in list(rep.items()):
			if (value == None):
				del rep[key]
			if (key == 'OID_NAME') and (value != None):
				new_rep.update({"Object":{"OID_NAME":rep['OID_NAME']}})
			if (key == 'NAME') and (value != None):
				new_rep.update({"Object":{"OID_NAME":rep['NAME']}})
			if (key != 'NAME') and (key not in os_list) and (key != "Dependency") and (key != "PERMISSIONS") and (key != "DEPENDENCIES") and (value != None):
				profile[key] = value
			if (key == "DEPENDENCIES") and (value != None):
				new_rep.update({"Dependencies":value})
			if (key in os_list) and (value != None):
				if len(value) != 0:
					new_rep[key] = value
			if (key == 'PERMISSIONS') and (value != None):
				new_rep.update({"PERMISSIONS":value})
		new_rep["Profile"] = profile
		return new_rep


class JobDetailSerializer(serializers.Serializer): # this serializer is used for Get:repository/job/

	JOBNUMMBER = serializers.SerializerMethodField('get_jobid')
	STATE_1 = serializers.SerializerMethodField('get_state1')
	JOBNAME = serializers.CharField(read_only=True, default='NULL')
	OID = serializers.CharField(read_only=True, default='NULL')
	RUN_NO = serializers.IntegerField(read_only=True, default=0)
	PATH = serializers.CharField(read_only=True, default='NULL')
	STATE_2 = serializers.SerializerMethodField('get_state2')
	HOLD = serializers.SerializerMethodField('get_hold')
	COND_CODE = serializers.CharField(read_only=True, default='NULL')
	TARGET = serializers.CharField(read_only=True, default='NULL')
	PROCESS_ID = serializers.CharField(read_only=True, default='NULL')
	SWITCH_MODE = serializers.CharField(read_only=True, default='NULL')
	LATEST_START = serializers.CharField(read_only=True, default='NULL')
	ACTION_ON_DELAY = serializers.CharField(read_only=True, default='NULL')
	ACTUAL_START = serializers.CharField(read_only=True, default='NULL')
	ACTUAL_RUNTIME = serializers.CharField(read_only=True, default='NULL')
	MAX_RUNTIME = serializers.CharField(read_only=True, default='NULL')
	INHERIT_TERMINATION = serializers.SerializerMethodField('get_i_terminate')
	INHERIT_TIMINGS = serializers.SerializerMethodField('get_i_time')
	ACTION_ON_MAXR = serializers.CharField(read_only=True)
	ACTION_ON_START = serializers.CharField(read_only=True)
	ACTION_ON_SUCCESS = serializers.CharField(read_only=True)
	ACTION_ON_CANCEL = serializers.CharField(read_only=True, default='NULL')
	FINISH_ON_CANCEL = serializers.CharField(read_only=True, default='NULL')
	EDITSTATE = serializers.CharField(read_only=True, default='NULL')
	EDITUSER = serializers.CharField(read_only=True, default='NULL')
	BUSINESS_PROCESS = serializers.CharField(read_only=True, default='NULL')
	FOLDERKEY = serializers.IntegerField(read_only=True, default=0)
	MAX_REDO = serializers.IntegerField(read_only=True, default=0)
	PRIORITY = serializers.IntegerField(read_only=True, default=0)
	SEVERITY = serializers.IntegerField(read_only=True, default=0)
	PATH = serializers.CharField(read_only=True,default='Null')

	def get_jobid(self, obj):
		return obj.JOBID

	def get_state1(self, obj):
		return obj.REAL_STATE

	def get_state2(self, obj):
		return obj.STATE

	def get_hold(self, obj):
		if obj.HOLD == 'No' or 'NO' or 'no':
			return False
		elif obj.HOLD == 'Yes':
			return True
		else:
			return  obj.HOLD

	def get_i_terminate(self, obj):
		if obj.INHERIT_TERMINATION == 'No' or 'NO' or 'no':
			return False
		elif obj.INHERIT_TERMINATION == 'Yes':
			return True
		else:
			return obj.INHERIT_TERMINATION

	def get_i_time(self, obj):
		if obj.INHERIT_TIMINGS == 'No' or 'NO' or 'no':
			return False
		elif obj.INHERIT_TIMINGS == 'Yes':
			return True
		else:
			return obj.INHERIT_TIMINGS


class GetJobDependencySerializer(serializers.Serializer):# This serializer is used in Returning Json object of job Dependency
	Job = serializers.SerializerMethodField('get_jobs')
	Event = serializers.SerializerMethodField('get_events')
	File = serializers.SerializerMethodField('get_file')

	def get_jobs(self, obj):
		dependency = {}
		job_list = []
		if obj.COND_TYPE == 'DEPENDENCY':
			dependency['DEPENDENCY'] = obj.COND_NAME
			dummy_data = obj.CONDITION
			condition = xmltodict.parse(obj.CONDITION)
			print(condition['DATA']['@STATE'])
			dependency['STATE'] = condition['DATA']['@STATE']
			dependency['OP'] = condition['DATA']['@OP']
			dependency['COND_CODE'] = condition['DATA']['@COND_CODE']
			dependency['CODE'] = condition['DATA']['@CODE']
		return dependency

	def get_events(self, obj):
		dependency = {}
		if obj.COND_TYPE == 'EVENT':
			dependency['Event'] = obj.COND_NAME
			condition = xmltodict.parse(obj.CONDITION)
			dependency['EVENT_PARAM'] = condition['DATA']['@EVENT_PARAM']
			dependency['EVENT_TYPE'] = condition['DATA']['@EVENT_TYPE']
		return dependency

	def get_file(self, obj):
		dependency = {}
		if obj.COND_TYPE == 'FILE':
			dependency['FILENAME'] = obj.COND_NAME
			condition = xmltodict.parse(obj.CONDITION)
			dependency['RCS'] = condition['DATA']['@RCS']
			dependency['AVAILABLE'] = condition['DATA']['@AVAILABLE']
		return dependency

	def to_representation(self, instance):
		rep = super().to_representation(instance)
		if not ('Job' in rep and 'File' in rep and 'Event' in rep):
			print('There might have been an issue with dependency serialization')
			pass #todo
		if rep['Job'] is None:  # checks if value is 'None', this is different from "emptiness"
			rep.pop('Job')
		if rep['File'] is None:  # checks if value is 'None', this is different from "emptiness"
			rep.pop('File')
		if rep['Event'] is None:  # checks if value is 'None', this is different from "emptiness"
			rep.pop('Event')
		return rep

class GetJobOSSerializer(serializers.Serializer):

	CMD_TYPE = serializers.CharField(read_only=True, default='Command System')
	#USERNAME = serializers.SerializerMethodField("get_username")
	#COMMAND = serializers.SerializerMethodField("get_command")
	IS_DUMMY = serializers.CharField(read_only=True, default='NULL')
	ENVIRONMENT = serializers.CharField(read_only=True, default='NULLL')
	DATA = serializers.SerializerMethodField("get_data")

	def get_oid(self, obj):
		return '0x' + (obj.JOBID).hex()

	def get_username(self, obj):
		username = xmltodict.parse(obj.COMMAND)
		use = username
		for key in use["DATA"]:
			key_value = str(key).replace("@", '')
		username = username["DATA"]["@USERNAME"]
		return username

	def get_command(self, obj):
		command = xmltodict.parse(obj.COMMAND)
		command = command["DATA"]["@COMMAND"]
		return command

	def get_data(self,obj):
		return xmltodict.parse(obj.COMMAND)["DATA"]


class GetJobObjectSerializer(serializers.Serializer):
	NAME = serializers.CharField(read_only=True, default='NULL')
	OWNER = serializers.SerializerMethodField('get_owner')
	CREATED = serializers.DateTimeField(read_only=True)
	OID = serializers.SerializerMethodField('get_oid')
	def get_owner(self, obj):
		return_statment = (obj.OWNER).hex()
		values = '0x' + return_statment
		return values
	#OID = serializers.SerializerMethodField('get_oid')

	def get_oid(self, obj):
		return '0x' + (obj.OID).hex()
	#OID_TYPE = serializers.IntegerField(read_only=True, default=0)

class GetJobProfileSerializer(serializers.Serializer):

	OID = serializers.SerializerMethodField('get_oid')
	NAME = serializers.SerializerMethodField('get_name')
	TYPE = serializers.CharField(read_only=True)
	PROJECT = serializers.SerializerMethodField('get_folder')
	DESCRIPTION = serializers.CharField(read_only=True)
	OS = serializers.CharField(read_only=True)
	#COMMAND = serializers.SerializerMethodField("get_command")
	RCS = serializers.CharField(read_only=True, default="NULL")
	QUEUE = serializers.CharField(read_only=True,default="NULL")
	BUSINESS_PROCESS = serializers.CharField(read_only=True, default="NULL")

	def get_folder(self,obj):
		return obj.PATH

	def get_oid(self, obj):
		return '0x' + (obj.OID).hex()

	def get_command(self, obj):
		command = xmltodict.parse(obj.COMMAND)
		return command["DATA"]["@COMMAND"]

	def get_name(self, obj):
		return obj.OID_NAME

class JobDiscriptionSerializer(serializers.Serializer):

	DESCRIPTION = serializers.CharField(read_only=True, default='NULL')
	JOBID = serializers.SerializerMethodField('get_oid')
	JOBNAME = serializers.CharField(read_only=True, default='Null')

	def get_oid(self, obj):
		return '0x' + (obj.OID).hex()


class AddDependencySerializer(serializers.Serializer):

	DEPENDENCIES = serializers.DictField(default=None)


class EditDependencySerializer(serializers.Serializer):

	Dependency = serializers.ListField(read_only=False, default=None)
	File = serializers.ListField(child=serializers.DictField(read_only=False),default=None)
	Event = serializers.ListField(child=serializers.DictField(read_only=False),default=None)


class CriticalRcsSerializer(serializers.Serializer):

	RCS_NAME = serializers.CharField(read_only=False, default='NULL')
	OS = serializers.CharField(read_only=False, default='NULL')
	PRESENT = serializers.IntegerField(read_only=False)
	HOSTNAME = serializers.CharField(read_only=False, default='NULL')
	PORT = serializers.IntegerField(read_only=False)
	RCS_ACTIVE = serializers.IntegerField(read_only=False)
	QUEUE_ACTIVE = serializers.IntegerField(read_only=False)


class ControlLogSerializer(serializers.Serializer):

	LOG_TIME = serializers.CharField(read_only=False)
	MESSAGE = serializers.CharField(read_only=False)
	MSG_ID = serializers.CharField(read_only=False)
	CMDUSER = serializers.CharField(read_only=False)
	CMDHOST = serializers.CharField(read_only=False)
	CMDID = serializers.IntegerField(read_only=False)
	JOBID = serializers.IntegerField(read_only=False)
	RUN_NO = serializers.IntegerField(read_only=False)
	OID = serializers.SerializerMethodField('get_oid')

	def get_oid(self, obj):
		return '0x' + (obj.OID).hex()


class DeleteDependencySerializer(serializers.Serializer):

	DEPENDENCY = serializers.CharField(read_only=False, default=None)
	STATE = serializers.CharField(read_only=False, default=None)


class InAppSerializer(serializers.Serializer):

	name = serializers.CharField(read_only=True)
	URL = serializers.CharField(read_only=True)
	response = serializers.CharField(read_only=True)
	condition = serializers.CharField(read_only=True)
	message = serializers.CharField(read_only=True)
	describtion = serializers.CharField(read_only=True)
	predicate = serializers.CharField(read_only=True)
	counter = serializers.CharField(read_only=True)


class PermissionsSerializer(serializers.Serializer):
	PERMISSIONS = serializers.ListField(default=None)


class TokenTableSerializer(serializers.Serializer):
	Token = serializers.CharField(read_only=True)
	Subscriptions = serializers.CharField(read_only=True, default=None)
	New = serializers.IntegerField(read_only=True, default=0)


class UserFilterSerializer(serializers.Serializer):
	OID_NAME = serializers.CharField(read_only=True)
	FILTER_NAME = serializers.CharField(read_only=True)
	REQUEST = serializers.CharField(read_only=True)


class SchedulerSerializer(serializers.Serializer):
    
	SCHEDULE_KEY = serializers.DecimalField(read_only=True,max_digits=17, decimal_places=14)
	NAME = serializers.SerializerMethodField('get_name')
	DATE = serializers.SerializerMethodField('get_Date')
	JOBS = serializers.SerializerMethodField('get_jobs')
	ERRORS = serializers.IntegerField(read_only=True)
	WARNINGS = serializers.IntegerField(read_only=True)
	VERSION = serializers.SerializerMethodField('get_version')
	STATE = serializers.IntegerField(read_only=True)

	def get_name(self,obj):
		return obj.SCHEDULE_NAME

	def get_jobs(self,obj):
		return obj.ENTRIES

	def get_Date(self, obj):
		if obj.SCHEDULE_DATE is None:
			return obj.SCHEDULE_DATE
		date =  str(obj.SCHEDULE_DATE)[0:int(str(obj.SCHEDULE_DATE).rfind(':'))]
		return date

	def get_version(self, obj):
		return obj.SCHEDULE_NO


class SchedulerProgresSerializer(serializers.Serializer):
	SCHEDULE_KEY = serializers.DecimalField(read_only=True,max_digits=17, decimal_places=14)
	SCHEDULE_NAME = serializers.CharField(read_only=True)
	SCHEDULE_DATE = serializers.SerializerMethodField('get_Date')
	TOTAL_JOBS = serializers.IntegerField(read_only=True)
	FINISHED_JOBS = serializers.IntegerField(read_only=True)
	def get_Date(self, obj):
		if obj.SCHEDULE_DATE is None:
			return obj.SCHEDULE_DATE
		date =  str(obj.SCHEDULE_DATE)[0:int(str(obj.SCHEDULE_DATE).rfind(':'))]
		return date
class ClientSerializer(serializers.Serializer):
	OID = serializers.SerializerMethodField('get_oid')

	def get_oid(self, obj):
		return '0x' + (obj.OID).hex()
	NAME = serializers.CharField(read_only=True)