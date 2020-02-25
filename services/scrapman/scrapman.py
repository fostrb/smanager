from sservice import SService
import threading
import json
import time
import os


class ScrapMan(SService):
    """demo service"""
    def __init__(self):
        super(ScrapMan, self).__init__()
        # heartbeat (int): The number of seconds between screen captures.
        self.heartbeat = 5

        # precision: The number of seconds the heartbeat will tick by.
        self.precision = 1

        # min_sleep: Minimum number of seconds to sleep between ticks. (Inverse of maximum capture frequency)
        self.min_sleep = 2

        self.capturing = False

    def begin_capture(self):
        if not self.capturing:
            return
        last_tick = time.time()
        print("Capture loop started at " + str(last_tick))
        self.capture_all(dryrun=True)
        while self.capturing:
            if time.time() - last_tick >= self.heartbeat:
                last_tick = time.time()
                self.capture_all(dryrun=True)
            else:
                time.sleep(self.precision)
        print("Capture loop stopped at " + str(time.time()))

    def capture_all(self, dryrun=False):
        if dryrun:
            print("Capturing all at " + str(time.time()))
            return [0, "Capturing all"]

    def capture_single_target(self, target, displays):
        print("capturing " + str(target) + str(displays))
        return [0, "Capturing " + str(target, displays)]

    # exposed commands --------------------------------------------------------|
    #                                                                          |
    def toplevel_cmd_capture_at(self, freq):
        """Change the heartbeat of the screen capture service
            :param freq: Seconds to sleep between ticks."""
        self.heartbeat = max([int(freq), self.min_sleep])
        return [0, "Heartbeat: " + str(self.heartbeat)]

    def toplevel_cmd_scrapfreq(self, freq):
        """Change the heartbeat of the screen capture service
            :param freq: Ticks per minute."""
        f = int(freq)
        self.heartbeat = max([int(60/f), self.min_sleep])
        return [0, "Heartbeat: " + str(self.heartbeat)]

    def toplevel_cmd_captest(self):
        """Take one screenshot the test target"""
        return self.capture_single_target('192.168.0.175', [':0'])

    def toplevel_cmd_startcap(self):
        """Begin the capture loop"""
        if not self.capturing:
            self.capturing = True
            t = threading.Thread(target=self.begin_capture)
            t.daemon = True
            t.start()
            return [0, "Started capture loop thread"]
        else:
            return [1, "Service is already capturing"]

    def toplevel_cmd_stopcap(self):
        """Stop the capture loop"""
        if self.capturing:
            self.capturing = False
            return [0, "Capture stopped."]
        else:
            return [1, "Not currently capturing."]

    def cmd_get_heartbeat(self):
        """Get the current heartbeat of the screencap service
            Reported as an integer, i (1 tick/60s = '60')"""
        return [self.heartbeat, "Heartbeat: 1 tick per " + str(self.heartbeat) + ' s']

    def cmd_get_freq(self):
        """Get the current frequency of the screepcap service
            Reported as an integer, i (1 tick/60s = '1')"""
        return [int(60/self.heartbeat), "Frequency: " + str(int(60/self.heartbeat)) + ' ticks per minute']
    #                                                                          |
    # exposed commands --------------------------------------------------------|

    def cleanup(self):
        pass
