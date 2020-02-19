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
        self.robot_or_human = 'robot'

    def dataReceived(self, data):
        self.lineReceived(data)

    def send_string(self, data):
        self.sendLine(bytes(data, 'utf-8'))

    def connectionMade(self):
        print("connected: " + str(self.transport.client[0]))

        # TODO: always connect as robot, format connection message so it's useful to both humans and robots

        '''
        self.send_string("*" * 50)
        self.send_string("Service Manager")
        self.send_string("*" * 50)
        self.send_string("Available Services:")
        for name in self.service_manager.services.keys():
            self.send_string('-' + name)
        self.send_string("-" * 50)
        '''

    def connectionLost(self, reason=None):
        print("Disconnected: " + str(self.transport.client[0]))

    def lineReceived(self, line):

        # change_id_for_one: If using 'humanrun' or 'robotrun', this value becomes previous identifier,
        #   then is used to switch back after command is run
        change_id_for_one = False
        try:
            line = line.decode('utf-8')
        except:
            return
        arg0 = line.strip().split(' ')[0]
        if arg0.lower() in ['human', 'robot']:
            if arg0.lower() == 'human':
                self.robot_or_human = 'human'
                return
            else:
                self.robot_or_human = 'robot'
                return
        elif arg0.lower() in ['humanrun', 'robotrun']:
            change_id_for_one = self.robot_or_human
            if arg0.lower() == 'humanrun':
                # run one command as a human
                self.robot_or_human = 'human'
            else:
                # run one command as a robot
                self.robot_or_human = 'robot'
            line2 = line.strip().split(' ')
            line2.pop(0)
            line = ' '.join(line2)

            arg0 = line.strip().split(' ')[0]

        if arg0.lower() in self.service_manager.services.keys():
            line = line[len(arg0) + 1:]
            r = self.service_manager.services[arg0.lower()].parse_command(line)
        else:
            r = self.service_manager.parse_command(line)

        if isinstance(r, list):
            # if return value is a list, this should mean there's optional human/robot output
            #   first string should be robot
            #   second string should be human

            if self.robot_or_human == 'human':
                self.send_string(str(r[1]))
                self.send_string("-" * 50)
            else:
                self.send_string(str(r[0]))
        else:
            self.send_string(str(r))
            self.send_string("-" * 50)
        if change_id_for_one:
            self.robot_or_human = change_id_for_one


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

        """
        sessions dict maps each session to a session type; 'human' or 'robot'.
            defaults to robot
        """
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
        # TODO: Simple service help

        human_string = ''
        robot_string = ''

        human_string += "-" * 50 + '\n'
        human_string += self.__class__.__name__+'\n'
        human_string += "-" * 50 + '\n'
        if target:
            if target.lower() in self.services.keys():
                # needs to be updated for human/robot output
                return self.services[target.lower()].cmd_help()

        # toplevel commands
        human_string += 'Toplevel exposed commands:\n'
        robot_string += 'TOP:'
        for s, serv in self.services.items():
            for cmd in serv.toplv_cmds:
                human_string += '\t'+cmd
                robot_string += ' ' + cmd
                boundmeth = serv.cmds[cmd]
                if boundmeth.__doc__ is not None:
                    human_string += ': ' + boundmeth.__doc__.strip() + '\n'
        robot_string += '\n'

        human_string += '-'*50 + '\n'
        human_string += "Services:\n"

        robot_string += "SERVICES:"
        for s, serv in self.services.items():
            if serv.__doc__ is not None:
                human_string += '\t' + s + ': ' + serv.__doc__.strip()+'\n'
            else:
                human_string += '\t' + s + '\n'
            robot_string += ' ' + s
        robot_string += '\n'

        human_string += "Commands:\n"
        robot_string += "COMMANDS:"
        for cmd, boundmeth in self.cmds.items():
            if not boundmeth.__name__.startswith('toplevel_cmd_'):
                if boundmeth.__doc__ is not None:
                    human_string += ('\t' + cmd + ": " + boundmeth.__doc__.strip() + '\n')
                else:
                    human_string += '\t'+cmd+'\n'

                robot_string += (' '+cmd)
        return [robot_string, human_string]

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

    def cmd_human(self):
        """Switch mode to human console"""

    def cmd_kill(self):
        """kill server"""
        for sname, service in self.services.items():
            service.cleanup()
        reactor.stop()


if __name__ == '__main__':
    reactor.listenTCP(10000, SMFactory())
    reactor.run()
