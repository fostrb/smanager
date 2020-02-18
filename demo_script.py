import os
import subprocess

from subprocess import Popen, PIPE

address = 'localhost'
port = 10000

def smanager_cmd(address, port, cmd):
    '''
    # subprocess method 
    p1 = Popen(['echo', '-n', cmd], stdout=PIPE)
    p2 = Popen(['nc', '-q', '1', 'localhost', '10000'], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    cmdoutput = output.decode('utf-8')
    '''
    cmdoutput = os.popen('echo -n ' + cmd + ' | nc -q 1 ' + address + ' ' + str(port)).read()
    return cmdoutput


def what_services():
    hstr = smanager_cmd(address, port, 'help -s')
    services = []

    for line in hstr.split('\n'):
        if line.startswith('SERVICES:'):
            for s in line.split(' '):
                if s != 'SERVICES:':
                    services.append(s)
    return services


def what_commands():
    hstr = smanager_cmd(address, port, 'help -s')
    commands = []

    for line in hstr.split('\n'):
        if line.startswith('COMMANDS:'):
            for c in line.split(' '):
                if c != 'COMMANDS:':
                    commands.append(c)
    return commands


def what_toplvl():
    hstr = smanager_cmd(address, port, 'help -s')
    commands = []

    for line in hstr.split('\n'):
        if line.startswith('TOP:'):
            for c in line.split(' '):
                if c != 'TOP:':
                    commands.append(c)
    return commands


if __name__ == '__main__':
    print("Checking smanager services:")
    services = what_services()
    if 'scrapman' in services:
        heartbeat = smanager_cmd(address, port, 'scrapman get_heartbeat')
        print(heartbeat)

    print(services)
    commands = what_commands()
    print(commands)
    toplvl = what_toplvl()
    print(toplvl)
