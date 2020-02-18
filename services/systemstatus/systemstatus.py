from sservice import SService
import os


class SystemStatus(SService):
    """Simple example SService implementation"""
    def __init__(self):
        super(SystemStatus, self).__init__()

    def cmd_uptime(self):
        '''Returns uptime of system'''
        return os.popen('uptime').read()

    def toplevel_cmd_hostname(self):
        '''Returns hostname of system'''
        return os.popen('hostname').read()
