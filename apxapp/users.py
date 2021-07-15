from .models import models
from rest_framework import authentication
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed

class DeviceUser(AnonymousUser):

	def __init__(self, device):
		self.device = device

	@property
	def is_authenticated(self):
		return True
