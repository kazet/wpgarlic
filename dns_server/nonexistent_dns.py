import dnslib
from dnslib.server import DNSServer


class Resolver:
    def resolve(self, request, handler):
        reply = request.reply()
        reply.header.rcode = dnslib.RCODE.NXDOMAIN
        return reply


resolver = Resolver()
server = DNSServer(resolver, port=53)
server.start()
