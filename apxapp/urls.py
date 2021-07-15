from django.urls import path, include
from rest_framework.routers import DefaultRouter
from.views import *

router = DefaultRouter()
router.register(r'apx_api/v1/production/job=(?P<id>[0-9]+),time=(?P<time>\w+),name=(?P<name>\w+)', ControlJobPostView, base_name = 'action_change')
router.register(r'apx_api/v1/production/job=(?P<id>[0-9]+),jobname=(?P<name>\w+)', ControlJobPostView, base_name = 'action_change_without_timout')
router.register(r'apx_api/v1/control/job/hold/jobkey=(?P<id>[0-9]+)', ControlJobPostView, base_name = 'hold_job')
router.register(r'apx_api/v1/control/job/cancel/jobkey=(?P<id>[0-9]+)', ControlJobPostView, base_name = 'cancel_job')
router.register(r'apx_api/v1/control/job/release/jobkey=(?P<id>[0-9]+)', ControlJobPostView, base_name = 'release_job')
router.register(r'apx_api/v1/control/job/redo/jobkey=(?P<id>[0-9]+)', ControlJobPostView, base_name = 'redo_job')
router.register(r'apx_api/v1/control/job/load/jobkey=(?P<id>[0-9]+)', ControlJobPostView, base_name = 'load_job')
router.register(r'apx_api/v1/control/job/finish/jobkey=(?P<id>[0-9]+)', ControlJobPostView, base_name ='finish_job')
router.register(r'apx_api/v1/repository/job/delete', ProfileDeleteView, base_name = 'delete_job')
router.register(r'apx_api/v1/repository/project/delete', ProfileDeleteView, base_name = 'delete_job')
router.register(r'apx_api/v1/repository/client/delete', ProfileDeleteView, base_name = 'delete_job')
router.register(r'apx_api/v1/repository/job/update',JobProfileUpdate, base_name = 'job_profile_update')
router.register(r'apx_api/v1/repository/project/update',CreateProjectView, base_name = 'project_update')
router.register(r'apx_api/v1/repository/client/update',CreateClient, base_name = 'client_up')
router.register(r'apx_api/v1/repository/job/create', JobProfileCreate, base_name = 'create_job')
router.register(r'apx_api/v1/repository/project/create', CreateProjectView, base_name = 'create_project')
router.register(r'apx_api/v1/repository/project/net/create', CreateProjectView, base_name = 'create_net_project')
router.register(r'apx_api/v1/repository/project/net/update', CreateProjectView, base_name = 'update_net_project')
router.register(r'apx_api/v1/repository/client/create', CreateClient, base_name = 'create_client')
router.register(r'apx_api/v1/repository/dependency/add', AddDependencyView, base_name = 'add_dependency'),
router.register(r'apx_api/v1/repository/dependency/delete', DeleteDependencyView, base_name = 'delete_dependency'),
router.register(r'apx_api/v1/repository/permissions/add', Permissions, base_name = 'add_permissions'),
router.register(r'apx_api/v1/repository/permissions/delete', DeletePermissionView, base_name = 'delete_permission'),
router.register(r'apx_api/v1/filters/add', CreateUserFilter, base_name = 'create_filters'),
router.register(r'apx_api/v1/filters/delete', DeleteUserFilter, base_name = 'delete_filter')
router.register(r'apx_api/v1/filters/delete/all', DeleteAllUserFilters, base_name = 'delete_filter')


urlpatterns = [
	path('apx_api/v1/control/execute/', ProductionJobControlView.as_view(), name='cmd_post'),# command, /execute/?cmd=''
	path('apx_api/v1/production/general/cmd=<str:query>/time=<slug:time>', ProductionJobControlView.as_view(), name='cmd_post'),
	path(r'apx_api/v1/production/jobs/general/', ProductionJobGenericView.as_view(), name='generic_view'),
	#path(r'apx_api/v1/production/jobs/filter=(?P<query>\S+)/$',ProductionJobGenericView.as_view(),name='generic_view'),
	path('apx_api/v1/repository/object/', GetJobProfileView.as_view(), name='get_profile'),
	path('apx_api/v1/repository/jobs/recursive/', GetJobProfilesView.as_view(), name='list_profile'), # to be changed.
	path('apx_api/v1/repository/objects/recursive/', GetObjectsRecursive.as_view(), name='list_profile'), # to be changed.
	path('apx_api/v1/repository/jobs/', GetJobProfilesView.as_view(), name='list_profile'),
	#path(r'apx_api/v1/production/job/', ProductionJobView.as_view(), name='name_view'),
	path(r'apx_api/v1/production/job/', JobDetailView.as_view(), name='name_view'),
	path(r'apx_api/v1/production/objects/', ProductionJobView.as_view(), name='name_view_all'),
 	path(r'apx_api/v1/production/objects/recursive/', ProductionJobRecursiveView.as_view(), name='name_view_all'),
	path(r'apx_api/v1/production/jobs/status/', StatusView.as_view(), name='count_jobs'),
	path(r'apx_api/v1/production/control/status/', StatusView.as_view(), name='state_pcc'),
	path(r'apx_api/v1/production/agents/', StatusView.as_view(), name='state_rcs'),
	path(r'apx_api/v1/controllog/', ControlLogview.as_view(), name='Control_Log_views'),
	path(r'apx_api/v1/inappview/', InAppView.as_view(), name='inAppView'),
	path(r'apx_api/v1/tokentable/', TokenTable.as_view(), name='TokenTable'),
	path(r'apx_api/v1/repository/objects/', GetObjectView.as_view(), name='get_objects'),
	path(r'apx_api/v1/history/jobs/', JobHistory.as_view(), name='job_history'),
	path(r'apx_api/v1/history/job/', JobHistoryDetail.as_view(), name='job_history_detail'),
	path(r'apx_api/v1/history/job/spool/', GetJobSpool.as_view(), name='job_spool'),
	path(r'apx_api/v1/createtoken/', CreateTokenRequest.as_view(), name='create_token'),
	path(r'apx_api/v1/deletetoken/', CreateTokenRequest.as_view(), name='create_token'),
	path(r'apx_api/v1/filters/', GetUserFilter.as_view(), name='get_filters'),
	path(r'apx_api/v1/scheduler/', SchedulerView.as_view(), name='get_schedular'),
	path(r'apx_api/v1/scheduler/progress/', SchedularProgressView.as_view(), name='get_schedular'),
	path(r'', include(router.urls)),
]
