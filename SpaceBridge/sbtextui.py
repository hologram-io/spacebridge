#
#  sbtextgui.py
#
# Author: Reuben Balik <reuben@holgram.io>
#
# License: Copyright (c) 2016 Hologram All Rights Reserved.
#
# Released under the MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from sbexceptions import ErrorException, MissingParamException
import sys

class SpaceBridgeTextUI:
    title = "Hologram SpaceBridge"
    def __init__(self, version):
        title = self.title + ' v' + version
        self.title = title


    def prompt_for_apikey(self):
        return input("Please enter your Hologram API key: ")


    def prompt_for_forwards(self, links):
        print("Links with tunneling enabled:")
        result = []
        if not links:
            print("  [NONE]")
        else:
            linkids = []
            for link in links:
                linkids.append(link['id'])
                print("  ID#%s - %s (Device ID#%s)"%(str(link['id']), link['devicename'],
                    str(link['deviceid'])))
            linkid = 0
            device_port = 0
            local_port = 0
            while True:
                linkid = input("Enter link ID to forward: ")
                device_port = input("Enter device port: ")
                local_port = input("Enter local port: ")
                if not linkid.isdigit():
                    print("Error: Invalid linkid")
                linkid = int(linkid)
                if linkid not in linkids:
                    print("Error: Invalid linkid")
                    continue
                if not device_port.isdigit():
                    print("Error: Invalid device port")
                    continue
                if not local_port.isdigit():
                    print("Error: Invalid local port")
                    continue
                break
            fwd = [linkid, int(device_port), int(local_port)]
            result.append(fwd)
        return result


    def prompt_for_orgid(self, orgs):
        print("Available organizations: ")
        result = None
        orgids = []
        if not orgs:
            print("  [NONE]")
        else:
            for org in orgs:
                orgids.append(org['id'])
                print("  ID#%d - %s"%(org['id'], org['name']))
            while True:
                orgid = input(
                        "Choose the organization id to search for the device: ")
                if not orgid.isdigit():
                    print("Error: Invalid organization id")
                    continue
                orgid = int(orgid)
                if orgid not in orgids:
                    print("Error: Invalid organization id")
                    continue
                break
            result = orgid
        return result

    
    def prompt_for_keygen(self):
        message = ("We're going to generate a set of secure keys to protect "
        "your connection to your device. These keys will be generated by the "
        "Hologram API. The Hologram servers will only store the public key and "
        "the private key will be saved to your computer.\n"
        "If you have a key already that you want to use or want to generate "
        "one on your own exit this program (CTRL-C) and run with the --upload-publickey and --privatekey arguments.")
        print(message)
        input("Press enter to continue...")
        return True


    def show_message(self, message):
        print(message)


    def show_error_message(self, message):
        print("Error: "+message)


    def show_exception(self):
        print(str(sys.exc_info()))


    def tunnel_running(self, fwdmessage):
        msg = "Tunnel is running\n\n" + fwdmessage + "\n"
        print(msg)
        input("Hit enter to close tunnel and exit...")


