from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
from twisted.internet import reactor

from sservice import SService
import services

LOGFILE = "/tmp/smanager.log"


class SMProtocol(LineReceiver):
    """
    Holds context for each SManager session
    For instance ,if a user was accessing SManager via a shell, this will hold the state of which service they
        are addressing currently.
    """

    def rawDataReceived(self, data):
        print("Received unprecedented raw data:", data)

    def __init__(self, service_manager):
        self.service_manager = service_manager

    def dataReceived(self, data):
        self.lineReceived(data)

    def send_string(self, data):
        self.sendLine(bytes(data, 'utf-8'))

    def connectionMade(self):
        print("connected: " + str(self.transport.client[0]))
        self.send_string("*" * 50)
        self.send_string("Service Manager")
        self.send_string("*" * 50)
        self.send_string("Available Services:")
        for name in self.service_manager.services.keys():
            self.send_string('-' + name)
        self.send_string("-" * 50)
    
    def connectionLost(self, reason=None):
        print("Disconnected: " + str(self.transport.client[0]))

    def lineReceived(self, line):
        try:
            line = line.decode('utf-8')
        except:
            return
        arg0 = line.strip().split(' ')[0]
        if arg0.lower() in self.service_manager.services.keys():
            line = line[len(arg0) + 1:]
            r = self.service_manager.services[arg0.lower()].parse_command(line)
        else:
            r = self.service_manager.parse_command(line)
        self.send_string(str(r))
        self.send_string("-" * 50)


class SMFactory(Factory):
    def __init__(self):
        self.service_manager = SManager()
    
    def buildProtocol(self, addr):
        return SMProtocol(self.service_manager)


class SManager(SService):
    """
    SServ object used for parser
    because service manager is a service, we could (but probably shouldn't) nest service managers.
    """
    def __init__(self):
        super(SManager, self).__init__()
        # log.startLogging(open(LOGFILE, "a+"))
        self.services = {}
        self.init_services()

    def init_services(self):
        for k, v in services.__dict__.items():
            if isinstance(v, type):
                if issubclass(v, SService):
                    self.services[v.__name__.lower()] = v()

        # Raising level of service toplv_cmds to Smanager.
        for sname, service in self.services.items():
            for cmd in service.toplv_cmds:
                if cmd in self.cmds.keys():
                    print("Command name collision: \'" + cmd+"\'")
                else:
                    self.cmds[cmd] = service.cmds[cmd]

    def handle_disconnect(self, address):
        for k, v in self.services.items():
            v.disconnect_notification(address)
    
    def cmd_help(self, target=None):
        """display help message"""
        returnstring = "-"*50+'\n'
        returnstring += self.__class__.__name__+'\n'
        returnstring += "-" * 50 + '\n'
        if target:
            if target.lower() in self.services.keys():
                return self.services[target.lower()].cmd_help()

        # toplevel commands
        returnstring += 'Toplevel exposed commands:\n'
        for s, serv in self.services.items():
            for cmd in serv.toplv_cmds:
                returnstring += '\t'+cmd
                boundmeth = serv.cmds[cmd]
                if boundmeth.__doc__ is not None:
                    returnstring += ': ' + boundmeth.__doc__.strip() + '\n'
                else:
                    returnstring += '\n'
        returnstring += '-'*50 + '\n'

        returnstring += "Services:\n"
        for s, serv in self.services.items():
            if serv.__doc__ is not None:
                returnstring += '\t' + s + ': ' + serv.__doc__.strip()+'\n'
            else:
                returnstring += '\t' + s + '\n'
        returnstring += "Commands:\n"
        for cmd, boundmeth in self.cmds.items():
            if boundmeth.__doc__ is not None:
                returnstring += ('\t' + cmd + ": " + boundmeth.__doc__.strip() + '\n')
            else:
                returnstring += ('\t'+cmd+'\n')
        return returnstring
    
    def cmd_restart(self):
        """restart services"""
        for k, v in self.services.items():
            v.cleanup()
        for k, v in services.__dict__.items():
            if isinstance(v, type):
                if issubclass(v, SService):
                    self.services[v.__name__.lower()] = v()

    def cmd_kill(self):
        """kill server"""
        for sname, service in self.services.items():
            service.cleanup()
        reactor.stop()


if __name__ == '__main__':
    reactor.listenTCP(10000, SMFactory())
    reactor.run()
