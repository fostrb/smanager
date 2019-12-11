import threading
import time
import subprocess
import socket
import argparse

from sserv import SServ

import os


class ScreencapMan(SServ):
    """demo service"""
    def __init__(self):
        super(ScreencapMan, self).__init__()
        self.heartbeat = 60
        print("ScreencapMan Init")
        print("Heartbeat: " + str(self.heartbeat))
    
    def start_server(self):
        pass

    # exposed commands ---
    def cmd_capture_at(self, freq):
        self.heartbeat = int(freq)
        print("Heartbeat: " + str(self.heartbeat))

    # exposed  -------|
    
    
    def cleanup(self):
        pass
    
