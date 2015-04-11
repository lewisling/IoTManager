import random
import IOTIOMapping
import sys
name = raw_input("Node name:")
name = name.replace(",","")
uid = ""
for i in range(0,16):
    uid += "%X"%(random.randint(0,16))

iomapping = IOTIOMapping.IOTIOMapping()
output_port_count = int(raw_input("Output port count:"))
output_gpio_mapping = {}
for i in range(0,output_port_count):
    portid = int(raw_input("Port ID(Arbitrary, unique between input and output):"))
    gpio = int(raw_input("GPIO Pin:"))
    out_name = raw_input("Output name:")
    
    iomapping.outputs.append(IOTIOMapping.OutputPort(portid,out_name))
    output_gpio_mapping[portid] = gpio

portconfig = iomapping.genConfigStr()

outfile = open(sys.argv[1],"w")
outfile.write("nome = \"%s\"\n"%(name))
outfile.write("uid = \"%s\"\n"%(uid))
outfile.write("portconfig = \"%s\"\n"%(portconfig))
outfile.write("tmr.alarm(0, 1000, 1, function()\n   if wifi.sta.getip() == nil then\n      print(\"Connecting to AP...\")\n   else\n      print('IP: ',wifi.sta.getip())\n      tmr.stop(0)\n   end\nend)\n")

for portid in output_gpio_mapping:
    outfile.write("gpio.mode(%d, gpio.OUTPUT)\n"%(output_gpio_mapping[portid]))
    outfile.write("state_%d = 0\n"%(portid))

outfile.write("function udprecv(c,pl)\n")
outfile.write("    if pl == \"A\" then\n") # Status request
statestr = ""
statestr_tokens = []
for portid in output_gpio_mapping:
    statestr_tokens.append("\"%d:\"..state_%d"%(portid,portid))
statestr = "..\";\"..".join(statestr_tokens)
outfile.write("         c:send(uid..\",\"..nome..\",\"..%s..\",\"..portconfig)\n"%(statestr))
outfile.write("   end\n")
outfile.write("end\n")
outfile.write("srv=net.createServer(net.UDP)\nsrv:on(\"receive\",udprecv)\nsrv:listen(8000)\n")






outfile.close()