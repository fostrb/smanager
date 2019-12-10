from twisted.internet import reactor, protocol, stdio
from twisted.protocols import basic
from sys import stdout

import argparse

import readline

host='localhost'
port = 10000
delimiter = '\n'

class ConsoleClient(protocol.Protocol):
    def dataReceived(self, data):
        stdout.write(data)
        stdout.flush()
  
    def sendData(self, data):
        self.transport.write(data + delimiter)


class ConsoleClientFactor(protocol.ClientFactory):
    def startedConnecting(self, connector):
        print("Connecting...")
    
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
        
    def lineReceived(self, line):
        if line == 'quit':
            self.quit()
        else:
            self.factory.client.sendData(line)

    def quit(self):
        reactor.stop()

def main():
    factory = ConsoleClientFactory()
    stdio.StandardIO(Console(factory))
    reactor.connectTCP(host, port, factory)
    reactor.run()


if __name__ == '__main__':
    main()
        
