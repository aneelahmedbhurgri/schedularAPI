
import socket
from APX.wsgi import application
import win32serviceutil
import signal
import servicemanager
import win32event
import win32service
import time
import os
import sys
import tornado.options
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

if sys.executable.lower().endswith("pythonservice.exe"):      
    # insert site-packages 2nd in path (behind project folder)
    sys.path.insert(1, os.path.join("env",'Lib','site-packages'))

class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'APIservice'
    _svc_display_name_ = 'REST API Service'
    _svc_description_ = 'Python Service Description'
    

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        #_exe_name_ = os.path.join(*[os.environ['VIRTUAL_ENV'], 'Scripts', 'pythonservice.exe'])

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        self.isrunning = True
        cwd = os.getcwd()
        print(cwd)
        container = tornado.wsgi.WSGIContainer(application)
        server = tornado.httpserver.HTTPServer(container, ssl_options={
        "certfile": "development.crt",
        "keyfile": "development.key"
        })
        server.listen(5323)
        tornado.ioloop.IOLoop.instance().start()
        

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        
        '''
        self.isrunning = False
        os.kill(os.getpid(), 9)
        #self.server.stop()
        #ioloop = tornado.ioloop.IOLoop.current()
        #ioloop.add_callback(ioloop.stop)

    def main(self):
        
        '''
        Main class to be ovverridden to add logic
        '''
        #container = tornado.wsgi.WSGIContainer(application)
        #server = tornado.httpserver.HTTPServer(container, ssl_options={
        #"certfile": "F:/ap installation/API/development.crt",
        #"keyfile": "F:/ap installation/API/development.key",
        #})
        #server.listen(8000)
        
        #looping = tornado.ioloop.IOLoop.instance().start()
        #while self.isrunning:
            #pass
            #serve(application, host = 'localhost', port='8000',url_scheme="https")
        
        #server.stop()
        #tornado.ioloop.IOLoop.instance().stop()
        pass


# entry point of the module: copy and paste into the new module
# ensuring you are calling the "parse_command_line" of the new created class
if __name__ == '__main__':
    SMWinservice.parse_command_line()
