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
        if target in targets.keys():
            for display in targets[target]:
                os.system('ssh ' + user + '@' + target + ' "xwd -out screenshot.xwd -root -display "' + display)

    # exposed commands ---
    def cmd_capture_at(self, freq):
        self.heartbeat = int(freq)
        print("Heartbeat: " + str(self.heartbeat))
    # exposed  -------|

    def cmd_captest(self):
        self.capture_single_target('192.168.0.175')

    def cmd_get_heartbeat(self):
        return self.heartbeat

    def cleanup(self):
        pass
