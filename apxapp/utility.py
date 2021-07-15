# Database management system agnostic utility functions

import xmltodict
import base64
import logging;
from inspect import currentframe, getframeinfo
import collections

logger = logging.getLogger(__name__);

def log_exception(exception, frameinfo, message):
	template = "{} caught in {} line {}: ".format(type(exception).__name__, frameinfo.filename[-32:], frameinfo.lineno)
	logger.error(template + message)

# If the string starts and ends with " then that is interpreted as being part of the string
# Will put single quotes around the result so that it can be used directly in SQL code/queries
def string_to_sql_literal(s):
    if len(s) == 0:
        return "''"
	# Todo: This should check for sql injections, since this is the only place where they pose danger
    result = s.replace("'", "''")   # double up single quotes to escape them
    result = "'" + result + "'"
    return result

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

# Todo: This should be changed/deleted in the future
#	- The conversion between 'DEPENDENCIES' and 'Dependencies' is silly, let's decide on One
#	- We won't be using true and fals, since not all DBMSs support it, it will be 0/1 in the future
def json_dependency_conversion(add_dependency):
	add_dependency_new = {"Dependencies":add_dependency}
	json_data = str(add_dependency_new).replace("'",'"').replace("True", "true").replace("False","false")
	return json_data

def get_at_rules(rules_xml):
	at_rules = "<root>" + (rules_xml["AT_RULES"]) + "</root>"
	at_rules = (xmltodict.parse(at_rules))
	print(at_rules)
	if at_rules["root"] is not None:
		at_rules = (at_rules['root'])
		at_rules = (dict(at_rules))

	RULES = {
		"AT_LATEST_START": {},
		"AT_CANCEL": {},
		"AT_FINISH": {},
		"AT_MAX_RUNTIME": {},
		"AT_LATEST_FINISH": {},
		"AT_INTERVAL_DISTRIBUTED": {},
		"AT_MAX_TIME_IN_C": {},
		"AT_START": {},
		"AT_LAST_CANCEL": {}
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

def check_sql_injection(query_string):
	list_keywords = ["ADD","add","ALTER","alter","BACKUP","backup","create","CREATE","REPLACE","replace","DELETE","delete","DROP","drop","INSERT","insert","SET","set","TRUNCATE","truncate","UPDATE","update"]
	if any(keyword in str(query_string).upper() for keyword in list_keywords):
		return True
	else: False

def current_user(request):
	auth_header = request.META['HTTP_AUTHORIZATION']
	encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
	decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
	username = decoded_credentials[0]
	return username


def convert_sql_queries_rep(sql):
	sql = sql.replace("JOBNUMER", "JOBKEY").replace("STATE_1", "REAL_STATE").replace("PROJECT", "PATH")
	if "%" in sql:
		sql = sql.replace('=', ' like')
	if "NAME" in sql:
		sql = sql.replace("NAME", "OID_NAME")
	return  sql
		

def convert_sql_queries_prd(sql):
	sql = sql.replace("JOBNUMBER", "JOBKEY").replace("STATE_1", "STATE1").replace("PROJECT", "PATH")
	if "%" in sql:
		sql = sql.replace('=', ' like')
	if "NAME" in sql:
		sql = sql.replace("NAME", "JOBNAME")
	return  sql