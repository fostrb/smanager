from twisted.internet import reactor, protocol, stdio
from twisted.protocols import basic
from sys import stdout
import socket
from OpenSSL import SSL
from twisted.internet import ssl as tssl
import ssl
import os
import json

import argparse

host = 'localhost'
delimiter = '\n'

# load configuration
dirname = os.path.dirname(__file__)
configfile = os.path.join(dirname, 'config.json')
with open(configfile) as fp:
    config = json.load(fp)
if not str(config['keydir']).startswith('/'):
    # relative path to keys directory
    config['keydir'] = os.path.join(dirname, config['keydir'])
KEYS_LOCATION = config['keydir']
client_key = os.path.join(KEYS_LOCATION, config['client_key'])
client_cert = os.path.join(KEYS_LOCATION, config['client_cert'])

PORT = config['default_port']


class ConsoleClient(protocol.Protocol):
    def dataReceived(self, data):
        stdout.write(data.decode('utf-8'))
        stdout.flush()

    def sendData(self, data):
        self.transport.write(bytes(data, 'utf-8'))


class ConsoleClientFactory(protocol.ClientFactory):
    def startedConnecting(self, connector):
        print("Connecting to " + str(host) + ':' + str(PORT) + '...')

    def buildProtocol(self, addr):
        print("Connected")
        self.client = ConsoleClient()
        self.client.name = 'console'
        return self.client

    def clientConnectionFailed(self, connector, reason):
        print("Failed: ", reason)


class CtxFactory(tssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = tssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(KEYS_LOCATION + '/client.pem')
        ctx.use_privatekey_file(KEYS_LOCATION + '/client.key')
        return ctx


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


def send_command(cmd, hostname=host, portnum=PORT):
    # Connect with SSL auth and send a single command
    context = ssl.SSLContext(SSL.SSLv23_METHOD)
    context.load_cert_chain(keyfile=client_key, certfile=client_cert)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.connect((hostname, portnum))
            ssock.write(bytes(cmd, 'utf-8'))
            rmsg = ssock.read().decode('utf-8')
            #print(rmsg)
            return rmsg


def main():
    factory = ConsoleClientFactory()
    stdio.StandardIO(Console(factory))
    reactor.connectSSL(host, PORT, factory, CtxFactory())
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
            PORT = int(port_str)
        else:
            host = args.address
    if args.command:
        str_command = ' '.join(args.command)
        print('command: ' + str_command)
        send_command(str_command)
    else:
        main()
