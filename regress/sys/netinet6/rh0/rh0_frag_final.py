#!/usr/local/bin/python2.7
# send a ping6 packet with routing header type 0
# the address pointer is at the final destination
# hide the routing header behind a fragment header to avoid header scan
# we expect an echo reply, as there are no more hops

print "send with fragment and routing header type 0 to the final destination"

import os
from addr import *
from scapy.all import *

pid=os.getpid()
eid=pid & 0xffff
fid=pid & 0xffffffff
payload="ABCDEFGHIJKLMNOP"
packet=IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)/\
    IPv6ExtHdrFragment(id=fid)/\
    IPv6ExtHdrRouting(addresses=[OTHER_FAKE1_ADDR6, OTHER_FAKE2_ADDR6], \
    segleft=0)/\
    ICMPv6EchoRequest(id=eid, data=payload)
eth=Ether(src=LOCAL_MAC, dst=REMOTE_MAC)/packet

if os.fork() == 0:
	time.sleep(1)
	sendp(eth, iface=LOCAL_IF)
	os._exit(0)

ans=sniff(iface=LOCAL_IF, timeout=3, filter=
    "ip6 and dst "+LOCAL_ADDR6+" and icmp6")
for a in ans:
	if a and a.type == ETH_P_IPV6 and \
	    ipv6nh[a.payload.nh] == 'ICMPv6' and \
	    icmp6types[a.payload.payload.type] == 'Echo Reply':
		reply=a.payload.payload
		id=reply.id
		print "id=%#x" % (id)
		if id != eid:
			print "WRONG ECHO REPLY ID"
			exit(2)
		data=reply.data
		print "payload=%s" % (data)
		if data != payload:
			print "WRONG PAYLOAD"
			exit(2)
		exit(0)
print "NO ICMP6 ECHO REPLY"
exit(1)
