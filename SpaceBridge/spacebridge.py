#!/usr/bin/env python
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
# Special thanks to the Paramiko project.
#

HELP="""
Tool to perform local port forwarding through the Hologram SpaceBridge Inbound Tunnel

This script connects to the Hologram SpaceBridge Tunnel server and sets up
local port forwarding (analogous to OpenSSH's "-L" option) from a
local port through the SpaceBridge server.
"""

import getpass
import os
import sys
import argparse
import paramiko
import logging
from sbexceptions import MissingParamException, ErrorException
import sbgui
import sbtextui
import requests
requests.packages.urllib3.disable_warnings()
import portforward


DEFAULT_LOCAL_HOST = '127.0.0.1'


class AllowHologramPolicy(paramiko.MissingHostKeyPolicy):
    hologram_fingerprint = '\xc7\xd2l\xe2WPI\xbf<#s\xc5\xcc9H\xa3'

    def missing_host_key(self, client, hostname, key):
        if key.get_fingerprint() != self.hologram_fingerprint:
            raise Exception("Server fingerprint does not match Hologram!")
        else:
            return


class SpaceBridge:
    verbose = False
    apibase = 'https://dashboard.hologram.io/api/1/'
    tunnel_server = 'tunnel.hologram.io'
    tunnel_port = 999
    stderr_log_level = logging.WARNING
    forwards = []
    local_host = DEFAULT_LOCAL_HOST

    def __init__(self, version, istext = False, isverbose = False):
        if istext:
            self.ui = sbtextui.SpaceBridgeTextUI(version)
        else:
            self.ui = sbgui.SpaceBridgeGUI(version)

        if isverbose:
            self.verbose = isverbose
            self.log_level = logging.INFO

        self.settings_dir = os.path.expanduser("~") + os.path.sep + '.hologram'
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)

        self.privatekey = self.settings_dir + os.path.sep + 'spacebridge.key'
        self.publickey = ''

        logfile = self.settings_dir + os.path.sep + 'spacebridge.log'
        rootlogger = logging.getLogger('')
        self.logger = logging.getLogger('spacebridge')
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(self.stderr_log_level)
        rootlogger.addHandler(sh)

        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.INFO)
        fmt = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s (%(process)d): %(message)s')
        fh.setFormatter(fmt)
        rootlogger.addHandler(fh)

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AllowHologramPolicy())

    def collect_user_prefs(self, args):
        if args.apibase:
            self.apibase = args.apibase

        if args.apikey:
            self.apikey = args.apikey
        else:
            self.apikey = self.ui.prompt_for_apikey()
            if self.apikey is None:
                sys.exit(0)
            elif self.apikey == "":
                raise MissingParamException('Missing APIKey')

        if args.publickey:
            self.publickey = args.publickey
        if args.privatekey:
            self.privatekey = args.privatekey

        if args.tunnel_server:
            self.tunnel_server = args.tunnel_server
        if args.tunnel_port:
            self.tunnel_port = args.tunnel_port
        if args.local_host:
            self.local_host = args.local_host

    def collect_forwards(self, args):
        if args.forwards:
            self.parse_forwards(args.forwards)
        else:
            user = self.load_user_info()
            orgs = self.load_orgs(user['id'])
            if len(orgs) > 1:
                orgid = self.ui.prompt_for_orgid(orgs)
            else:
                orgid = orgs[0]['id']
            if orgid is None or not orgid:
                sys.exit(0)
            links = self.load_link_list(orgid)
            if not links:
                raise ErrorException(
                        "You don't have any links with tunneling enabled. "\
                        "Go into the dashboard and enable tunneling on some links")
            self.forwards = self.ui.prompt_for_forwards(links)
            if self.forwards is None or not self.forwards:
                sys.exit(0)
            for f in self.forwards:
                if f[0] is None:
                    raise ErrorException(
                    'There was an error collecting link information. Contact support')

    def parse_forwards(self, forwardstrings):
        self.forwards = []
        for forward in forwardstrings:
            splfor = forward.split(":")
            if len(splfor) != 3:
                raise ErrorException(
                        "forward string formatted wrong [%s]"%forward)
            if not splfor[0].isdigit():
                raise ErrorException("Invalid linkid in [%s]"%
                        forward)
            if not splfor[1].isdigit() or not splfor[2].isdigit():
                raise ErrorException("Invalid port numbers in [%s]"%
                        forward)
            fwd = [int(splfor[0]), int(splfor[1]), int(splfor[2])]
            self.forwards.append(fwd)

    def load_user_info(self):
        apiurl = self.apibase + 'users/me/'
        url_params = {'apikey' : self.apikey}
        r = requests.get(apiurl, params=url_params)
        if r.status_code != requests.codes.ok:
            raise ErrorException('Error connecting to API: ' + r.text)
        else:
            resp = r.json();
            return resp['data']

    def load_link_list(self, orgid):
        self.logger.info("Loading links from account")
        apiurl = self.apibase + 'links/cellular/'
        url_params = {'apikey' : self.apikey,
                'orgid':orgid, 'tunnelable':1,
                'limit':1000}
        r = requests.get(apiurl, params=url_params)
        if r.status_code != requests.codes.ok:
            raise UpdaterException('Error connecting to API: ' + r.text)
        else:
            resp = r.json();
            return resp['data']


    def load_orgs(self, userid):
        apiurl = self.apibase + 'organizations/'
        url_params = {'apikey' : self.apikey, 'userid' : userid,
                      'limit' : 1000}
        orgs = []
        while True:
            r = requests.get(apiurl, params=url_params)
            if r.status_code != requests.codes.ok:
                raise UpdaterException('Error connecting to API: ' + r.text)
            else:
                resp = r.json();
                data = resp['data']
                orgs += data

                if (len(data) < 1000):
                    break
                else:
                    url_params['startafter'] = data[-1]['id']
        return orgs


    def check_credential_files(self):
        self.logger.info('Using private key ' + self.privatekey)
        if self.publickey:
            self.upload_key()
        if not os.path.isfile(self.privatekey):
            if not self.ui.prompt_for_keygen():
                # The user decided not to use our API key generator
                # so we exit and they can generate a key on their own if they want
                sys.exit(0)
            else:
                self.generate_and_upload_key()

    def upload_key(self):
        if self.publickey is not None:
            with open(self.publickey, 'r') as kf:
                publickey = kf.read()
            payload = {'public_key': publickey}
            params = {'apikey': self.apikey}
            r = requests.post(self.apibase + "tunnelkeys", json=payload, params=params)
            if r.status_code != requests.codes.ok:
                raise ErrorException('Error uploading public key: ' + r.text)
            else:
                self.logger.info('Uploaded public key ' + self.publickey)

    def generate_and_upload_key(self):
        self.logger.info('Generating keypair from API')
        apiurl = self.apibase + "tunnelkeys"
        params = {'apikey': self.apikey}
        r = requests.post(apiurl, params=params)
        if r.status_code != requests.codes.ok:
            raise ErrorException('Error generating keypair: ' + r.text)
        else:
            resp = r.json()
            with open(self.privatekey, 'w') as kf:
                kf.write(resp['data']['private_key'])
            with open(self.privatekey + '.pub', 'w') as kf:
                kf.write(resp['data']['public_key'])
            self.logger.info('Generated and saved keypair to %s and %s', self.privatekey, self.privatekey + '.pub')

    def connect_to_tunnel_server(self):
        self.logger.info('Connecting to server %s:%s ...'%(str(self.tunnel_server),
            str(self.tunnel_port)))
        try:
            self.client.connect(self.tunnel_server, self.tunnel_port, username="htunnel",
                    key_filename=self.privatekey, look_for_keys=True)
        except Exception as e:
            if e[0] == 'not a valid EC private key file':
                raise ErrorException('Invalid private key file')
            else:
                raise ErrorException('*** Failed to connect to %s:%s: %r'%
                        (str(self.tunnel_server), str(self.tunnel_port), e))

        forwardmessage = ""
        for forward in self.forwards:
            host = "link" + str(forward[0])
            msg = 'Now forwarding %s:%s to %s:%s ...' %\
                    (self.local_host, str(forward[2]), host, str(forward[1]))
            self.logger.info(msg)
            forwardmessage += msg + '\n'
            portforward.forward_tunnel(self.local_host, forward[2],
                    host, forward[1], self.client.get_transport())

        self.ui.tunnel_running(forwardmessage)

    def run(self, args):
        try:
            self.collect_user_prefs(args)
            self.check_credential_files()
            self.collect_forwards(args)
            self.connect_to_tunnel_server()
        except ErrorException as e:
            self.ui.show_error_message('Error: '+ str(e))
            sys.exit(1)
        except Exception:
            self.ui.show_exception()
            sys.exit(1)


def get_basedir():
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        return sys._MEIPASS
    else:
        # we are running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '..'


def get_version():
    with open(get_basedir() + os.path.sep + 'version.txt', 'r') as f:
        return f.readline().rstrip()


def main():
    version = get_version()
    parser = argparse.ArgumentParser(description=HELP,
        add_help=True)
    parser.add_argument('--apikey', help='Hologram API key')
    parser.add_argument('-f', '--forward', dest="forwards", action="append",
        help="Specify any number of port forwards in the format <linkid>:<device port>:<local port>")
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--text-mode', action='store_true',
        help="Disable the GUI and do everything via text inputs")
    parser.add_argument('--local-host', default=DEFAULT_LOCAL_HOST,
        help='local host IP to bind to (default: %s)' % DEFAULT_LOCAL_HOST)
    parser.add_argument('--upload-publickey', dest="publickey",
        help='Upload specified public key to the server to authenticate against with --privatekey')
    parser.add_argument('-i', '--privatekey', dest="privatekey",
        help='Use specified private key to authenticate. Defaults to ~/.hologram/spacebridge.key')
    parser.add_argument('--version', action='version',
        version='SpaceBridge v'+version)
    # hidden options
    parser.add_argument('--apibase', help=argparse.SUPPRESS)
    parser.add_argument('--tunnel-server', help=argparse.SUPPRESS)
    parser.add_argument('--tunnel-port', help=argparse.SUPPRESS, type=int)
    args = parser.parse_args()

    sb = SpaceBridge(version, args.text_mode, args.verbose)
    sb.run(args)
