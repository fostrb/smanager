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
    
    def cmd_help(self, simple_output=None, target=None):
        """display help message"""
        print("HELP COMMAND")
        # TODO: Simple service help
        returnstring = ''
        simple = False
        if simple_output:
            if simple_output == '-s':
                simple = True
            else:
                target = simple_output
        if not simple:
            returnstring = "-" * 50 + '\n'
            returnstring += self.__class__.__name__+'\n'
            returnstring += "-" * 50 + '\n'
        if target:
            if target.lower() in self.services.keys():
                return self.services[target.lower()].cmd_help()

        # toplevel commands
        if not simple:
            returnstring += 'Toplevel exposed commands:\n'
        else:
            returnstring += 'TOP:'
        for s, serv in self.services.items():
            for cmd in serv.toplv_cmds:
                if not simple:
                    returnstring += '\t'+cmd
                else:
                    returnstring += ' ' + cmd
                boundmeth = serv.cmds[cmd]
                if not simple:
                    if boundmeth.__doc__ is not None:
                        returnstring += ': ' + boundmeth.__doc__.strip() + '\n'
                    else:
                        returnstring += '\n'
        if simple:
            returnstring += '\n'
        if not simple:
            returnstring += '-'*50 + '\n'

        if not simple:
            returnstring += "Services:\n"
        else:
            returnstring += "SERVICES:"
        for s, serv in self.services.items():
            if not simple:
                if serv.__doc__ is not None:
                    returnstring += '\t' + s + ': ' + serv.__doc__.strip()+'\n'
                else:
                    returnstring += '\t' + s + '\n'
            else:
                returnstring += ' ' + s
        if simple:
            returnstring += '\n'

        if not simple:
            returnstring += "Commands:\n"
        else:
            returnstring += "COMMANDS:"
        for cmd, boundmeth in self.cmds.items():
            if not boundmeth.__name__.startswith('toplevel_cmd_'):
                if not simple:
                    if boundmeth.__doc__ is not None:
                        returnstring += ('\t' + cmd + ": " + boundmeth.__doc__.strip() + '\n')
                    else:
                        returnstring += '\t'+cmd+'\n'
                else:
                    returnstring += (' '+cmd)
        return returnstring

    def cmd_restart(self, service_name=None):
        """restart services"""
        # TODO: Since services modularized, restart needs to be restructured
        if service_name is None:
            for k, v in self.services.items():
                v.cleanup()
            for k, v in services.__dict__.items():
                if isinstance(v, type):
                    if issubclass(v, SService):
                        self.services[v.__name__.lower()] = v()
        else:
            if service_name in self.services.keys():
                print(services.__dict__[service_name])
                self.services[service_name] = services.__dict__[service_name]()

    def cmd_kill(self):
        """kill server"""
        for sname, service in self.services.items():
            service.cleanup()
        reactor.stop()


if __name__ == '__main__':
    reactor.listenTCP(10000, SMFactory())
    reactor.run()
