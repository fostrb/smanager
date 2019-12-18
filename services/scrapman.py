from sserv import SServ
import time
import os

targets = {'192.168.0.175': [':0']}
user = 'fostrb'


class ScreencapMan(SServ):
    """demo service"""
    def __init__(self):
        super(ScreencapMan, self).__init__()
        self.heartbeat = 60
        print("ScreencapMan Init")

    def capture_single_target(self, target):
        try:
            if target in targets.keys():
                for display in targets[target]:
                    ret = os.system('ssh ' + user + '@' + target + ' "xwd -out screenshot.xwd -root -display "' + display)
                    if not ret == 0:
                        return "FAILURE"
            else:
                return "Target not in list"
        except:
            return "Capture failure"
        return "Capture success"

    # exposed commands --------------------------------------------------------|
    #                                                                          |
    def toplevel_cmd_capture_at(self, freq):
        '''
        Change the heartbeat of the screen capture service
        '''
        self.heartbeat = int(freq)
        return "Heartbeat: " + str(self.heartbeat)
    # exposed  -------|

    def toplevel_cmd_captest(self):
        '''
        Take one screenshot the test target
        '''
        return self.capture_single_target('192.168.0.175')

    def cmd_get_heartbeat(self):
        '''
        Get the current heartbeat of the screencap service
            Reported as an integer, 1/Hz (1/60s = '60')
        '''
        return self.heartbeat
    #                                                                          |
    # exposed commands --------------------------------------------------------|

    def cleanup(self):
        pass
