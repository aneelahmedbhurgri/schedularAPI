# Introduction 
TODO: Give a short introduction of your project. Let this section explain the objectives or the motivation behind this project. 

# Installation Process 

To start the API first we need to create an environment so API can Run without any issue todo so first you have to cd to the API folder/location and run following commands to 
activate the Environment without "" marks 

    1) “python -m venv myAPIenvironment” 
    2) cd to “myAPIenvironment/Scripts/activate” 

Once you have activated the environment then you have to cd back to API project and in such a way you can see these directories in cmd line  

    27.02.2020  14:43  APX 
    16.07.2020  15:48  apxapp 
    04.02.2020  10:12  manage.py 
    18.02.2020  10:31  requirements.txt 

Now you need to Install the dependencies to in your environment to run the API to do so please run this command and wait till everything is installed on your Environment Folder  

    “pip install –r requirements.txt”. 

After the installation required files you can start the server by following command: 

    “python manage.py runsslserver 0.0.0.0:8000” or  

    “python manage.py runsslserver”  

You can choose any IP and Port address to start this Django Server.
you can find all the dependencies for project in requirements.txt file

# Status Code
| Response | Status Code | 
| :---: | :---: |
| success  | 200 ok |
| Job Not Found/ * Not Found | 404 Not Found |
| Invalid Username/Password | 406 Permission Denied |
| Multiple Results for single Job | 416 Not Applicable |

# Authentication

RestApi uses Basic Auth which means in order to successfully get a response user needs to pass username and password everytime a new request is being processed, Incase of failure Api
will response as Invalid username/password message. 


# API GUIDE
This API have the following Contents

    1 Production
    2 Control 
    3 Repository 

 ## 1 Production 

In this API part we can read all the jobs in production, single detailed job in production, jobs with different search condition such as “name=abc” or “jobkey =123” etc. 

From Here you will see explanations of all the “URLS” which can be used inside API 

### 1.1 Get list of jobs: 

#### URL format

    GET /apx_api/v1/production/jobs/

#### Response

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description                       |
|----------|:-------------------------------------------:|
| 200 ok   | Indicates the request completed successfully|


        [
            {
                "Size":111
            },
            {
                "JOBID": 9,
                "RUN_NO": 1,
                "JOBNAME": "cd",
                "REAL_STATE": "C",
                "EARLIEST_START": null,
                ............
            }
        ]


[to view full output click here](API/README-Examples/listjobs.json)


Above url can be used to output all the jobs in production 


### 1.2 Get list of jops with Filters: 

#### Requests

    GET /apx_api/v1/production/jobs/?name like=jobname 

    GET /apx_api/v1/production/jobs/?description like=Hello World 

    GET /apx_api/v1/production/jobs/?status=C 

    GET /apx_api/v1/production/jobs/?description=upload my file 
 

All the URLS above can be used to search the jobs in production according to the filter given to it.
These filters will make it possible to return multiple jobs

| Parameter | Description |
| :---: | :-------------: |
| name like | Parameter is passed to url for returning all jobs with 'like' wild card for job name               |
| description | Parameter is passed to url to get jobs with given description                                    |
| status | Parameter is passed to to get jobs with given status                                                  |
| description like | Parameter is passed to url for returning all jobs with 'like' wild card for job description |

**This request will return multiple jobs**

#### Response Example
    
    https://localhost:8000/apx_api/v1/production/jobs/?name like=job


| Header   |      Description                                                   |
|----------|:------------------------------------------------------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description                                              |
|---------------|:------------------------------------------------------------------:|
| 200 ok        | Indicates the request completed successfully                       |


        [
            {
                "Size":12
            },
            {
                "JOBID": 12,
                "RUN_NO": 1,
                "JOBNAME": "job",
                "REAL_STATE": "C",
                .....
            },
            {
                "JOBID": 13,
                "RUN_NO": 1,
                "JOBNAME": "job",
                .......
            }
        ]


### 1.3 Get list of jobs with Generic filter

This Get url is used to return list of jobs with general filters you had passed to Request

#### Request

    GET /production/jobs/filter=''

here parameter filter is the general query you can pass to get your required jobs in a list
| Parameter | Type | Description |
| :---: | :---: | :---: |
| filter | String | Query must be inside '' |

#### Response Example 

    GET https://localhost:8000/apx_api/v1/production/jobs/filter='REAL_STATE in ('C','X','B')'

| Header   |      Description                                                   |
|----------|:------------------------------------------------------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description                            |
|---------------|:-------------------------------------------:|
| 200 ok        | Indicates the request completed successfully|

    [
        {
            "Size":81
        },

        {
            "JOBID": 5,
            "JOBNAME": "hello",
            "REAL_STATE": "C",
                ...
        },
        {
                ...
            "PATH": "APM:/",
            "RUN_NO": 1,
            "COND_CODE": "USER"
        }
    ]



### 1.4 Get single detailed Job with Filters: 

#### Requests

    GET /apx_api/v1/production/job/?name=myjob 

    GET /apx_api/v1/production/job/?jobkey=123 

    GET /apx_api/v1/production/job/?oid=0x123hgbdz 

Above Urls can be used to  see all the details of a singular job with following mentioned filters:

| Parameter | Type | Description |
| :---: | :---: |   :-----------:|
| name  | String | pass this parameter to search and get job with name | 
| jobkey | Number | pass this parameter to search and get job with jobkey |
| oid | String | pass this parameter to search and get job with oid |


#### Response Example 

    https://localhost:8000/apx_api/v1/production/job/?jobkey=12

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

        
            {
                "JOBID": 12,
                "REAL_STATE": "C",
                "JOBNAME": "job",
                ...............
                "PATH": "APM:/",
                "DESCRIPTION": "echo \"Simple Job\""
            }
        


[to view full output for single Detailed job click here](API/README-Examples/jobDetail.json)

### 1.5 Get Jobs Status:

#### Request

    GET /apx_api/v1/production/jobs/status/

    To return current jobs in production with status.

#### Response

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    {
        "Size": 110,
        "Job Status": {
            "_": 1,
            "C": 81,
            "F": 6,
            "H": 22
        }
    }

### 1.6 Get Control Status 

#### Request 

    GET /apx_api/v1/production/control/status/
    
    To get current information about pcc 

#### Response 

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    {
        "Environment": "WIN-AN19TOFSGDU NT 6.2 Server 4.0 SP 0 (Build 9200) ",
        "State": "RUN",
        "Active": "Yes",
        "Version": "2,3,52,1",
        "Last Action": "2020-07-21 13:11:39"
    }

### 1.7 Get Production Agents

#### Request 

    GET /apx_api/v1/production/agents/

#### Response 

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    [
        {
            "RCS_NAME": "APX",
            "OS": "WINNT",
                ...
        },
        {

            "RCS_NAME": "APX014",
            "OS": "UNIX",
                ...

        }
    ]

### 1.8 Get Critical Agents in production

#### Request 

    GET /apx_api/v1/production/agents/filter=PRESENT=1 and RCS_ACTIVE=1



#### Exception Cases and Errors 
 1) In case of any filter passed to given urls did not match with any jobs in production will result in following response

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 404 not Found   | Indicates the request could not find anything|

    {

        "Message": "No Job Found"

    }

 2) Incorrect Username or Password will result the following response


| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 406 not Allowed   | Indicates the request can not permit certain user or un known error|

    {

        "Message": "Invalid Username/password or Internal Server Issue"

    }


3) In special case where user query for single job but in Database there were multiple jobs for that reponse will be 


| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 406 not Allowed   | Indicates the request can not permit certain user or un known error|

    {

        "Message":"Multiple Jobs Found With parameter Please Search by JobKey or Choose /jobs/?name like for multiple Entries"
    
    }


## 2 Control
Control portion of API is used to Change the status of jobs in Production
Basically A job in Production can be changed into different status such as:
1) HOLD
2) CANCEL
3) RELEASED
4) REDO
5) LOAD

Below you can find the API URLS to change the job`s status into any of the above mentioned List in any case you need to give 'jobkey' as parameter to successfully process the request

#### Requests 

    POST /apx_api/v1/control/job/hold/jobkey=

    POST /apx_api/v1/control/job/cancel/jobkey=

    POST /apx_api/v1/control/job/release/jobkey=

    POST /apx_api/v1/control/job/redo/jobkey=

    POST /apx_api/v1/control/job/load/jobkey=


| Parameter | Type | Description |
| :---: | :---: |  :------------:|
| jobkey | Number | This request requires give jobkey as parameter to change the state of job in production |


#### Request

    POST /apx_api/v1/control/job/cmd=

#### Response Example

    https://localhost:8000/apx_api/v1/control/job/hold/jobkey=150

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

    [
        {
            "LOG_TIME": "2020-07-21 10:36:03.000000",
            "MESSAGE": "Reading Command: CHG_STATE1, 150, H"
            ..........
        },
        {
            ......
            "MESSAGE": "job_1 ( 150/2 ) - Setting hold state - Not allowed",
            .......
            "CMDID": 993,
            "JOBID": 150,
            "RUN_NO": 2
        }
    ]






But in case if you want to pass any of APX GUI command you can use the following generic URL

#### Request

    POST /apx_api/v1/control/job/cmd=

#### Response Example

    https://localhost:8000/apx_api/v1/control/general/cmd='CHG_STATE1, 150, H'

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

    [
        {
            "LOG_TIME": "2020-07-21 10:36:03.000000",
            "MESSAGE": "Reading Command: CHG_STATE1, 150, H"
            ..........
        },
        {
            ......
            "MESSAGE": "job_1 ( 150/2 ) - Setting hold state - Not allowed",
            .......
            "CMDID": 993,
            "JOBID": 150,
            "RUN_NO": 2
        }
    ]



and also below url can be used in case if you want to give a timout before executing command

    https://localhost:8000/apx_api/v1/control/general/cmd=/time=


## 3 Repository

With Repository function you can view job profile with full detail, create new jobs, edit and delete existing jobs.
All the urls related to Repository section have unique parameter 'name' which can be which refers the name of job/project/client in Database.
you can pass the name in any way and below you can see some examples

    name=SAP/job_a  
    name=Client:/Job_a   
    name=SAP/Mini_project/JOB  
    name=job    
    name=client/project/job    
    name=client/project/project/job


### 3.1 Get the full detail of Job Profile

    GET  apx_api/v1/repository/job/?name=

This url can return single profile of job with full detail including Profile, object, dependencies, and os

#### Request 

    https://127.0.0.1:8000/apx_api/v1/repository/job/?name=job

#### Response

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

    {
        "Profile": [
            {
                "QUEUE": null,
                "RCS": "APXS",
                .....
            },
            {
            "Dependency": [],

            "WINNT": 
                    {
                        "USERNAME": "Administrator",
                        .....
                    },

            "Object": 
                    {
                        ........
                        "OID_TYPE": 134217732,
                        "NAME": "job"
                    }
            }
    }
                        
[to view full output click here](API/README-Examples/repositoryjobDetail.json)

### 3.2 Post/Create a New Job Profile

    POST /apx_api/v1/repository/job/create/?name=

To create a new job profile user required to enter the correct project name or destination in parameter of url where job should be created.
User also need to pass JSON data to create job profile an Example of JSON Data can be found here 


#### Request

    https://127.0.0.1:8000/apx_api/v1/repository/job/create/?name=Test


    {
        "NAME":"my new job",
        "QUEUE": "2",
            ..
            ..
        "RCS": "NULL"
    }

#### Response 

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

    {
        Message : Job Created.
    }


[to view full json format for creating an unix/winnt job click here](API/README-Examples/repositoryUnixWintCreatejob.json)

[to view full json format for creating an SAP job click here](API/README-Examples/repositorySAPCreatejob.json)    

### 3.3 Post/Update an existing Job Profile 

    POST /apx_api/v1/repository/job/update/?name=

To update an existing job in Database, parameter is same name which already mentioned and explained above, this also required the same JSON Data same as above
create new job url

#### Request

    https://127.0.0.1:8000/apx_api/v1/repository/job/update/?name=old_job

    {
        "NAME":"change_my_job_name",
        "QUEUE": "1",
            ..
            ..
        "RCS": "Windows"
    }

#### Response 


| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

    {
        Message: Job Profile Updated."
    }

[to view full json format for update job click here](API/README-Examples/UpdateJob.json) 

### 3.4 Post/Delete an existing Job Profile

    POST /apx_api/v1/repository/job/delete/?name=

#### Request 

    https://127.0.0.1:8000/apx_api/v1/repository/job/delete/?name=job

#### Response

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|

    {
        Message: Job Deleted.
    }


### 3.5 Get Jobs in Repository with filters

    GET /apx_api/v1/repository/jobs/filter = '{sql query}'

#### Request

    https://127.0.0.1:8000/apx_api/v1/repository/jobs/filter='all'

#### Response

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    [
        {
            "TARGET": "0",
            "SEVERITY": 0,
            "JOBNAME": "job_new_for_testing23",
            "MAX_RUNTIME": null,
            ......
        },
        {
            .......
            "MAX_REDO": -1,
            "RUNTIME": "0 00:01:00.000000",
            "SWITCH_MODE": "Queue",
            "CALENDAR": "Standard",
            "BUSINESS_PROCESS": null
        }

    ]

[to view full json output click here](API/README-Examples/repositoryJobFilter.json) 

### 3.6 Add new Job Dependency in Repository

    POST /apx_api/v1/repository/dependency/add/?name={jobname}

#### Request

    https://localhost:8000/apx_api/v1/repository/dependency/add/?name=job_news

    {

    "Dependency":[
        {
            "DEPENDENCY":"0x03F00666A818C641A52D016271396745",
	        "OP": "=",
	        "COND_CODE": "*",
            "CODE": "+",
            "STATE":"FFF"
    
        }
        ]
    }


#### Response


| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    {
        "Message":"Dependency Have been Added"
    }



### 3.7 Edit existing Job Dependency in Repository

    POST /apx_api/v1/repository/dependency/edit/?name={jobname}

**It is very Important to pass only job which have same existing dependency which is being changed** 

#### Request

    https://localhost:8000/apx_api/v1/repository/dependency/edit/?name=job_news

    {

    "Dependency":[
        {

            "DEPENDENCY":"0x03F00666A818C641A52D016271396745",
            "STATE":"F"
    
        }
        ]
    }


#### Response


| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    {
        "Message":"Dependency Has Edited"
    }



### 3.7 Delete existing Job Dependency in Repository

    POST /apx_api/v1/repository/dependency/delete/?name={jobname}

**It is Important to give State of job with DEPENDENCY in json data as a job can rely on single job but with different state** 

#### Request

    https://localhost:8000/apx_api/v1/repository/dependency/delete/?name=job_news


    {

        "DEPENDENCY":"0x03F00666A818C641A52D016271396745",
        "STATE":"F"
    
    }

#### Response


| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 200 ok   | Indicates the request completed successfully|


    {
        "Message":"Dependency Deleted"
    }



### Exception Cases and Errors

1) In case of in correct paramter following response will be result

| Header   |      Description      |
|----------|:---------------------:|
| Accept   | Data format of the response body. Supported types: application/json|

| Status Code   |      Description      |
|----------|:---------------------:|
| 404 not Found   | Indicates the request could not find anything|

    {

        Message: No object/Job/ Found with Given parameter

    }
