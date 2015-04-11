import re
import time
import socket
import thread
import IOTIOMapping
QUERY_TIMEOUT = 5

class IOTNode:
    def __init__(self,uid,name,iomapping,digitalstate=0,ipaddress=""):
        self.uid = uid
        self.name = name
        self.iomapping = iomapping
        self.digitalstate = digitalstate
        self.analoginputstate = {}
        self.digitalinputstate = {}
        self.ipaddress = ipaddress
        self.inputs_last_update = time.time()
    def packDigitalState(self):
        ports = []
        for port in self.digitalstate:
            ports.append("%d:%d"%(port,self.digitalstate[port]))
        return ";".join(ports)
    def _th_query_analog_and_digital_inputs(self):
        self.analoginputstate = {}
        self.digitalinputstate = {}
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.sendto(self.state, (self.ipaddress,8000))
        sock.settimeout(QUERY_TIMEOUT)
        starttime = time.time()
        while True:
            try:
                data,addr = sock.recvfrom(1500)
                if time.time() - starttime > QUERY_TIMEOUT:
                    break
            except socket.timeout:
                break
            if addr[0] == self.ipaddress:
                # portid:value;
                data = data.split(";")
                for port in data:
                    port = port.split(":")
                    portid = int(port[0])
                    portvalue = port[1]
                    if self.iomapping.isInputPortDigital(portid):
                        self.digitalinputstate[portid] = int(portvalue)
                    else:
                        self.analoginputstate[portid] = float(portvalue)
                self.inputs_last_update = time.time()
                break
        sock.close()
    def applyDigitalState(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.sendto("B"+self.packDigitalState(), (self.ipaddress,8000))
        sock.close() #In the case the command got lost, it will be retried at the next discovery round
    def tryQueryValues(self):
        thread.start_new_thread(self.applyDigitalState,(self,))
def unpackDigitalState(s):
    data = s.split(";")
    res = {}
    for port in data:
        port = port.split(":")
        portid = int(port[0])
        portvalue = port[1]
        res[portid] = portvalue
    return res
def createJSONReprFromNodeDict(d):
    result = {}
    for uid in d:
        node = d[uid]
        result[uid] = { "Name" : node.name, "IOMapping" : node.iomapping.genConfigStr(), "digitaloutstate" : node.digitalstate, "digitalinstate" : node.digitalinputstate, "analoginstate" : node.analoginputstate , "IPAddress" : node.ipaddress, "InputLastUpdate" : node.inputs_last_update }
    return result