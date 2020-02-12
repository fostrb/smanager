from twisted.internet import reactor, protocol, stdio
from twisted.protocols import basic
from sys import stdout
import socket

import argparse

host = 'localhost'
port = 10000
delimiter = '\n'


class ConsoleClient(protocol.Protocol):
    def dataReceived(self, data):
        stdout.write(data.decode('utf-8'))
        stdout.flush()

    def sendData(self, data):
        self.transport.write(bytes(data, 'utf-8'))


class ConsoleClientFactory(protocol.ClientFactory):
    def startedConnecting(self, connector):
        print("Connecting to " + str(host) + ':' + str(port) + '...')

    def buildProtocol(self, addr):
        print("Connected")
        self.client = ConsoleClient()
        self.client.name = 'console'
        return self.client

    def clientConnectionFailed(self, connector, reason):
        print("Failed: ", reason)


class Console(basic.LineReceiver):
    factory = None
    delimiter = delimiter

    def __init__(self, factory):
        self.factory = factory

    def dataReceived(self, data):
        self.lineReceived(data.decode('utf-8'))

    def lineReceived(self, line):
        if line == 'quit':
            self.quit()
        else:
            self.factory.client.sendData(line)

    def quit(self):
        reactor.stop()
        exit()


def send_command(cmd):
    s = socket.socket()
    s.connect((host, port))
    s.send(bytes(str(cmd + '\n'), 'utf-8'))


def main():
    factory = ConsoleClientFactory()
    stdio.StandardIO(Console(factory))
    reactor.connectTCP(host, port, factory)
    reactor.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address', nargs='?', default='localhost')
    parser.add_argument('-c', '--command', action='store', nargs='+')
    args = parser.parse_args()
    if args.address:
        print('address: ' + str(args.address))
        if ':' in str(args.address):
            host, port_str = str(args.address).split(':')
            port = int(port_str)
        else:
            host = args.address
    if args.command:
        str_command = ' '.join(args.command)
        print('command: ' + str_command)
        send_command(str_command)
    else:
        main()
