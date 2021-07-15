import urllib.parse
from rest_framework.fields import DecimalField
import sqlalchemy as al
from sqlalchemy.orm import sessionmaker, scoped_session, mapper
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Binary, VARCHAR,DateTime,Numeric
from sqlalchemy.sql.elements import collate
from sqlalchemy.types import BINARY
from sqlalchemy import func
import socket
from django.db import models
from sqlalchemy import ForeignKey

hostname = socket.gethostname()
username=''
password=''
engine =''
Base = declarative_base()
from django.db import models



class ProductionJobORM(Base):

	JOBKEY = Column(Integer, primary_key=True)
	RUN_NO = Column(Integer)
	JOBNAME = Column(String)
	STATE1 = Column(String)
	OID = Column(String)
	EARLIEST_START = Column(DateTime)
	PATH = Column(String)
	COND_CODE = Column(String)
	#ACTUAL_START = Column(DateTime)
	OS = Column(String)
	SCHEDULE_KEY = Column(Numeric)

	def __init__(self,JOBID,RUN_NO,PROCESS_ID,JOBNAME,REAL_STATE, OID,EARLIEST_START):
		self.JOBID = JOBID
		self.RUN_NO = RUN_NO
		self.JOBNAME = JOBNAME
		self.REAL_STATE = REAL_STATE
		self.OID = OID
		self.EARLIEST_START = EARLIEST_START

	def __repr__(self):
		return (f"Jobkey :{self.JOBID} Name:{self.JOBNAME}")


class ProductionJobDetailORM(Base):

	OID = Column(String, primary_key=True)
	STATE = Column(String)
	HOLD = Column(String)
	COND_CODE = Column(String)
	TARGET = Column(String)
	PROCESS_ID = Column(String)
	SWITCH_MODE = Column(String)
	LATEST_START = Column(String)
	ACTION_ON_DELAY = Column(String)
	ACTUAL_START = Column(String)
	ACTUAL_RUNTIME = Column(String)
	MAX_RUNTIME = Column(String)
	INHERIT_TERMINATION = Column(String)
	ACTION_ON_MAXR = Column(String)
	ACTION_ON_START = Column(String)
	ACTION_ON_SUCCESS = Column(String)
	ACTION_ON_CANCEL = Column(String)
	FINISH_ON_CANCEL = Column(String)
	EDITSTATE = Column(String)
	EDITUSER = Column(String)
	BUSINESS_PROCESS = Column(String)
	FOLDERKEY = Column(Integer)
	MAX_REDO = Column(Integer)
	PRIORITY = Column(Integer)
	SEVERITY = Column(Integer)
	PATH = Column(String)
	COND_CODE = Column(String)
	INHERIT_TIMINGS = Column(String)

class GetJobDependencyORM(Base):

	COND_TYPE = Column(String)
	JOBID = Column(Binary, primary_key=True)
	COND_NAME = Column(String, primary_key=True)
	CONDITION = Column(String, primary_key=True)


class JobWinntORM(Base):

	OID = Column(Binary, primary_key=True)
	USERNAME = Column(String)
	COMMAND = Column(String)
	SPOOL_STDERR = Column(Integer)
	SPOOL_STDOUT = Column(Integer)
class JobUnixORM(Base):

	OID = Column(Binary, primary_key=True)
	USERNAME = Column(String)
	COMMAND = Column(String)
	SPOOL_STDERR = Column(Integer)
	SPOOL_STDOUT = Column(Integer)

class OScmdORM(Base):

	JOBID = Column(Binary, primary_key=True)
	CMD_TYPE = Column(String)
	COMMAND = Column(String)
	IS_DUMMY = Column (String)
	ENVIRONMENT = Column (String)

class JobObjectORM(Base):

	OID = Column(Binary, primary_key=True)
	#OID_NAME = Column(String)
	OWNER = Column(Binary)
	CREATED = Column(DateTime)

class JobProfileORM(Base):

	TARGET = Column (String)
	JOBID = Column(Binary, primary_key=True)
	SEVERITY = Column (Integer)
	JOBNAME = Column(String)
	MAX_RUNTIME = Column (DateTime)
	MAX_REDO = Column (Integer)
	RUNTIME = Column (DateTime)
	SWITCH_MODE = Column(String)
	CALENDAR = Column(String)
	BUSINESS_PROCESS = Column(String)
	PATH = Column(String)
	DESCRIPTION = Column(String)
	LATEST_START = Column(String)
	ACTION_ON_DELAY = Column(String)
	ACTION_ON_MAXR = Column(String)
	ACTION_ON_START = Column(String)
	ACTION_ON_CANCEL = Column(String)
	ACTION_ON_SUCCESS = Column(String)

class RespositoryJobsORM(Base):

	JOBID = Column(Binary, primary_key=True)
	JOBNAME = Column(String)
	PATH = Column(String)
	MAX_REDO = Column (Integer)
	DESCRIPTION = Column(String)

class RepositoryJobs(Base):

	OID = Column(Binary, primary_key=True)
	OID_NAME = Column(String)
	PATH = Column(String)
	OS = Column(String)
	TYPE = Column(String)
	DESCRIPTION = Column(String)
	RCS = Column(String)
	QUEUE = Column(String)
	BUSINESS_PROCESS = Column(String)

class ProductionJobDescriptionORM(Base):

	DESCRIPTION = Column(String)
	JOBID = Column(Binary, primary_key=True)
	JOBNAME = Column(String)
	def __repr__(self):
		return (f"{self.OID}")

class CriticalRcsORM(Base):

	RCS_NAME = Column(String,primary_key=True)
	OS = Column(String)
	PRESENT = Column(Integer,primary_key=True)
	HOSTNAME = Column(String,primary_key=True)
	PORT = Column(Integer)
	RCS_ACTIVE = Column(Integer,primary_key=True)
	QUEUE_ACTIVE = Column(Integer,primary_key=True)

class ControlLogORM(Base):

	LOG_TIME = Column(String)
	MESSAGE = Column(String)
	MSG_ID = Column(String,primary_key=True)
	CMDUSER = Column(String)
	CMDHOST = Column(String)
	CMDID = Column(Integer,primary_key=True)
	JOBID = Column(Integer)
	RUN_NO = Column(Integer)
	CLIENT = Column(Binary)

class UserFilters(Base):

	OID_NAME = Column(String)
	FILTER_NAME = Column(String,primary_key=True)
	REQUEST = Column(String)

class Scheduler(Base):

	SCHEDULE_KEY = Column(Numeric, primary_key=True)
	SCHEDULE_NAME = Column(String)
	SCHEDULE_DATE = Column(DateTime)
	SCHEDULE_NO = Column(Integer)
	ENTRIES = Column(Integer)
	WARNINGS = Column(Integer)
	ERRORS = Column(Integer)
	STATE = Column(Integer)

class SchedularProgress(Base):

	SCHEDULE_KEY = Column(Numeric, primary_key=True)
	SCHEDULE_NAME = Column(String)
	SCHEDULE_DATE = Column(DateTime)
	TOTAL_JOBS = Column(Integer)
	FINISHED_JOBS = Column(Integer)

class ClientORM(Base):
	OID = Column(Binary, primary_key=True)
	NAME = Column(String, name="OID_NAME")
