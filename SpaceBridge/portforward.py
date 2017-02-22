# portforward.py
# Copyright 2016 Hologram
#
# Authors:
# Reuben Balik <reuben@hologram.io>
# Pat Wilbur <hello@hologram.io> <pdub@pdub.net>
#
# This file is part of SpaceBridge
#
# SpaceBridge is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# SpaceBridge is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with KTunnel; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Suite 500, Boston, MA  02110-1335  USA.
#
# This file is based upon a file, licensed under the LGPL, distributed with
# the Paramiko project and with the original copyright notice:
# 
#   Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# Special thanks to the Paramiko project.
#

import socket
import select
import logging
import threading

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

class ForwardServer (SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    

class Handler (SocketServer.BaseRequestHandler):

    def handle(self):
        logger = logging.getLogger('forwardhandler')
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            logger.warning('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                              self.chain_port,
                                                              repr(e)))
            return
        if chan is None:
            logger.warning('Incoming request to %s:%d was rejected by the server.' %
                    (self.chain_host, self.chain_port))
            return

        logger.info('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                            chan.getpeername(), (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
                
        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        logger.info('Tunnel closed from %r' % (peername,))


def forward_tunnel(local_host, local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHandler (Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    server = ForwardServer((local_host, local_port), SubHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
