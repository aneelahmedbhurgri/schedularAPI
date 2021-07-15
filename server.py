"""from waitress import serve
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application 
from APX.wsgi import application
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","APX.settings")
# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    #serve(application, host = 'localhost', port='5000',url_scheme='https')
    
    application = get_wsgi_application()
    call_command('runserver',  '127.0.0.1:8000')
"""
from waitress import serve
from APX.wsgi import application
import waitress

print('Interesting things happens.') # THIS IS WHERE YOU RUN YOUR tasks.checkdata.

if __name__ == '__main__':
    serve(application, port='8000')
    serve.close()
    
    
