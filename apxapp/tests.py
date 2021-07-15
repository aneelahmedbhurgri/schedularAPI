from django.test import TestCase
import pytest

from.serializers import ProductionGetSerializer
# Create your tests here.


def test_serializer():
	data = {
		"JOBID":2,
		"JOBNAME":"hello_job"
		}
	test_serializer = ProductionGetSerializer(data=data)
	assert(test_serializer.is_valid()) == True

test_serializer()
