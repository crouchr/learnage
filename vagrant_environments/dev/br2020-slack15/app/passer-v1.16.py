#!/usr/bin/python
#Copyright 2008, William Stearns <wstearns@pobox.com>
#Passer is a PASsive SERvice sniffer.
#Home site http://www.stearns.org/passer/
#Dedicated to Mae Anne Laroche.
#Released under the GPL.
#Version 1.16

# This file has been modified by R.Crouch
# Changed nmap,arp-scan and wireshark directories to /usr/local/share/...
# Needs scapy 1.x copied into site-packages

#======== Imports ========
import sys
import re
#This may be too restrictive.
#from scapy import sniff, p0f, sr1, IP, ICMP, IPerror, TCPerror, UDPerror, ICMPerror
from scapy import *
import os


#======== Global arrays ========
#These two are used to discover servers.  If we've seen a SYN go to a port, and a SYN/ACK back from it,
#that's a pretty good sign it's a server.  Not truly stateful, but a generally good guess.
SynSentToTCPService = { }	#Boolean dictionary: Have we seen a syn sent to this "IP,Proto_Port" pair yet?
LiveTCPService = { }		#Boolean dictionary: Have we seen a SYN/ACK come back (true) or a RST (False) from this "IP,Proto_Port" pair?

#Next two are used to discover clients.  If we've seen a SYN/ACK going to what appears to be a client port, and it
#later responds with a FIN, we'll call that a live TCP client.
SynAckSentToTCPClient = { }	#Boolean dictionary: Have we seen a SYN/ACK sent to this "IP,Proto_Port" pair yet?
LiveTCPClient = { }		#Boolean dictionary: Have we seen a FIN from this client, indicating a 3 way handshake and successful conversation?

NmapServerDescription = { }	#String dictionary: What server is this "IP,Proto_Port" pair?  These descriptions come from nmap-service-probes.
ManualServerDescription = { }	#Same as above, but locally found strings
ClientDescription = { }		#String dictionary: What client is on this "IP,Proto_Port"?  NOTE: the port here is the _server_ port at the other end.  So if
				#Firefox on 1.2.3.4 is making outbound connections to port 80 on remote servers, ClientDescription['1.2.3.4,TCP_80'] = "http/firefox"
LiveUDPService = { }		#Boolean dictionary: we've found a UDP server here at "IP,Proto_Port"
LiveUDPClient = { }		#Boolean dictionary: we've found a UDP client here at "IP,Proto_Port".  Like TCP, this is client IP and _server_ port.

IsRouter = { }			#Boolean dictionary: For a given IP key, is it a router?  Unset or True

OSDescription = { }		#String dictionary: What OS is this IP key?

MacAddr = { }			#String dictionary: For a given IP (key), what is its mac (value)?
EtherManuf = { }		#String dictionary: for a given key of the first three uppercase octets of a mac address ("00:01:0F"), who made this card?

DNSRecord = { }			#Dictionary of arrays of strings: For a given key of IPAddr,'A' or IPAddr,'PTR', what are it's corresponding hostname(s) (stored in an array)?

HostIPs = { }			#Dictionary of arrays: For a given fully qualified hostname, what IPs (array) are associated?

ServiceFPs = { }		#Dictionary of service fingerprints.  Keys are straight int port numbers (no TCP or UDP), or 'all' for strings that need
				#to be matched against all ports.  These are loaded from nmap's "nmap-service-probes", ignoring the probes since we're passive.
				#Values are lists of tuples, ala: [("Apache *server ready.", "Apache web"), ("VSFTPD FTP at your service", "vsftpd ftp")]
				#Note that the first object in a tuple is a _compiled regex_ rather than the printable strings I've used above.
				#A sample (non-compiled) version looks like:  {80: [('^Server: Apache/', 'http/apachewebserver')]}

Devel = False


#For my internal use to look for new service strings
#This payload logging is disabled when Devel == False
#Quite likely a security risk, I don't recommend enabling it.
ServerPayloadDir = '/var/tmp/passer-server/'
ClientPayloadDir = '/var/tmp/passer-client/'



#======== Functions ========
def Debug(DebugStr):
	"""Prints a note to stderr"""
	sys.stderr.write(DebugStr + '\n')


#FIXME - remove this function
def LogNewPayload(PayloadDir, PayloadFile, Payload):
	"""Saves the payload from an ack packet to a file named after the server or client port involved."""

	#Better yet, wrpcap("/path/to/pcap", list_of_packets)

	global Devel

	if (Devel == True):
		if os.path.isdir(PayloadDir):
			if (not Payload == "None"):
				pfile=open(PayloadFile, 'a')
				pfile.write(Payload)
				pfile.close()


def UnhandledPacket(Packet):
	"""Save packets that have not been (completely) processed out to a pcap file for later analysis"""

	global UnhandledFile

	if (UnhandledFile != None):
		UnhandledFile.write(Packet)


def LoadMacData(MacFile):
	"""Load Ethernet Mac address prefixes from standard locations (from ettercap, nmap, wireshark, and/or arp-scan)."""
	global EtherManuf

	More=''
	if (len(EtherManuf) > 0):
		More=' more'

	LoadCount = 0
	
	if os.path.isfile(MacFile):
		try:
			MacHandle=open(MacFile, 'r')

			for line in MacHandle:
				if (len(line) >= 8) and (line[2] == ':') and (line[5] == ':'):
					#uppercase incoming strings just in case one of the files uses lowercase
					MacHeader=line[:8].upper()
					Manuf=line[8:].strip()
					if (not EtherManuf.has_key(MacHeader)):
						EtherManuf[MacHeader] = Manuf
						LoadCount += 1
				elif (len(line) >= 7) and (re.search('^[0-9A-F]{6}[ \t]', line) <> None):
					MacHeader=str.upper(line[0:2] + ':' + line[2:4] + ':' + line[4:6])
					Manuf=line[7:].strip()
					if (not EtherManuf.has_key(MacHeader)):
						EtherManuf[MacHeader] = Manuf
						LoadCount += 1

			MacHandle.close()
			if EtherManuf.has_key('00:00:00'):
				del EtherManuf['00:00:00']		#Not really Xerox
				LoadCount -= 1
			Debug(str(LoadCount) + More + " mac prefixes loaded from" + str(MacFile))
			return True
		except:
			Debug("Unable to load " + str(MacFile))
			return False
	else:
		Debug("Unable to load " + str(MacFile))
		return False




def LoadNmapServiceFP(ServiceFileName):
	"""Load nmap fingerprints from nmap-service-probes, usually in /usr/share/nmap."""

	#File format details at http://nmap.org/vscan/vscan-fileformat.html

	global ServiceFPs
	
	LoadCount = 0
	CompileSuccess = 0
	CompileFail = 0
	PortList = ""
	PortArray = [ ]

	if os.path.isfile(ServiceFileName):
		try:
			ServiceHandle = open(ServiceFileName, "r")
			for line in ServiceHandle:
				if (len(line) >= 5) and (line[0:6] == "Probe "):
					#print "==== PROBE ===="
					PortArray = [ ]
					#print len(PortArray), PortArray			#len of empty array is 0
				elif (len(line) >= 5) and (line[0:6] == "match "):
					#print "match"
					#print line
					InformationPresent = True
													#Sample line:
													#  match srun m|^X\0\0\0$| p/Caucho Resin JSP Engine srun/
					Remainder=line[6:].strip()					#  srun m|^X\0\0\0$| p/Caucho Resin JSP Engine srun/
					MatchStart=Remainder.find(" m")					#      4
					ProtoString=Remainder[:MatchStart].replace(',', ';')		#  srun
					#At the moment, nmap-service-probes uses these separators:
					#3 m%, 2 m+, 126 m/, 29 m=, 2 m@, and 3509 m|
					#No flags on %, +, 
					#Only flags should be "i" (case-insensitive) and "s" ("." can match newline)
					Separator=Remainder[MatchStart+2:MatchStart+3]			#        |
					MatchEnd=Remainder.find(Separator,MatchStart+3)			#                  16
					MatchString=Remainder[MatchStart+3:MatchEnd]			#         ^X\0\0\0$

					#Handle an "i" or "s" flag after separator
					#Debug("==== " + Remainder[MatchEnd+1:MatchEnd+4])
					if MatchEnd + 1 == len(Remainder):
						InformationPresent = False
						#Debug("No information data for " + MatchString)
					elif (Remainder[MatchEnd+1:MatchEnd+2] == " "):
						PPointer=MatchEnd + 2
						MatchFlags = re.M
						#Debug(Remainder + ", no flags")
					elif (Remainder[MatchEnd+1:MatchEnd+3] == "i "):
						PPointer=MatchEnd + 3
						MatchFlags = re.M | re.I
						#Debug(Remainder + ", i flag")
					elif (Remainder[MatchEnd+1:MatchEnd+3] == "s "):
						PPointer=MatchEnd + 3
						MatchFlags = re.M | re.S
						#Debug(Remainder + ", s flag")
					elif (Remainder[MatchEnd+1:MatchEnd+4] == "is ") or (Remainder[MatchEnd+1:MatchEnd+4] == "si "):
						PPointer=MatchEnd + 4
						MatchFlags = re.M | re.I | re.S
						#Debug(Remainder + ", i and s flag")
					else:
						Debug("Unrecognized nmap-service-probes flag combination")
						print MatchEnd + 1, len(Remainder)
						Debug(Remainder + ", unknown flags")
						#quit()

					#Substitute ; for , in ProtoString and ServerDescription since we're using commas as field delimiters in output
					ServerDescription=Remainder[PPointer:].replace(',', ';')	#                    p/Caucho Resin JSP Engine srun/
					
					#The nmap-service-probes file uses a character set ("[...]") issue that python doesn't like.
					#If a "-" is used inside a character set, it should either be in the first or last position,
					#or used in a character range ("[.....a-z.....]").  The following move any dashes to first or 
					#last position so re.compile is happy.
					MatchString=MatchString.replace("[\w-","[-\w")			#The dash needs to be at the end or it's treated as a range specifier
					MatchString=MatchString.replace("[\d-","[-\d")			#same
					MatchString=MatchString.replace("[\w\d-_.]","[\w\d_.-]")	#and so on...
					MatchString=MatchString.replace("[\w\d-_]","[\w\d_-]")
					MatchString=MatchString.replace("[.-\w]","[.\w-]")
					MatchString=MatchString.replace("[\s-\w.,]","[\s\w.,-]")
					MatchString=MatchString.replace("[\w\d-.]","[\w\d.-]")
					MatchString=MatchString.replace("[\d\.-\w]","[\d\.\w-]")
					MatchString=MatchString.replace("[^-_A-Z0-9]","[^_A-Z0-9-]")
					MatchString=MatchString.replace("[^-A-Z0-9]","[^A-Z0-9-]")

					if (ServerDescription.find('Skype VoIP data channel') > -1):
						#This "14 bytes of random stuff" signature way misfires.
						pass
					elif (ServerDescription.find('Microsoft Distributed Transaction Coordinator') > -1):
						#This "ERROR" signature matches other protocols.
						pass
					elif (InformationPresent == False):
						#There's a regex match, but no information about, skip.
						pass
					else:
						try:
							#We try to compile the MatchString now before inserting into ServiceFPs so the work only needs to be 
							#done once.  If this fails we fall down to the except and simply don't use the tuple.
							#Originally 413 out of 3671 match lines failed to compile because of "-" placement in character sets.
							#The problem, and a fixed version, have been reported to the nmap developers.
							#The use of "str" seems redundant, but we have occasionally gotten:
							#line 511: OutputDescription = OneTuple[1]
							#TypeError: expected a character buffer object
							SearchTuple=(re.compile(MatchString, MatchFlags), str(ProtoString + "://" + ServerDescription))
							CompileSuccess += 1
							if (len(PortArray) == 0):
								#No ports declared yet; we'll place this search pair under the special port "all"
								if (not(ServiceFPs.has_key('all'))):
									ServiceFPs['all'] = [ ]
								ServiceFPs['all'].append(SearchTuple)
								LoadCount += 1
							else:
								#Register this search pair for every port requested
								for OnePort in PortArray:
									if (not(ServiceFPs.has_key(int(OnePort)))):
										ServiceFPs[int(OnePort)] = [ ]
									ServiceFPs[int(OnePort)].append(SearchTuple)
									LoadCount += 1
						except:
							#print "Failed to compile " + MatchString
							CompileFail += 1
					
				elif (len(line) >= 5) and (line[0:6] == "ports "):
					PortArray = [ ]
					RawPortsString=line[6:].strip()
					#print "ports are ", RawPortsString
					for PortBlock in RawPortsString.split(","):		#Each PortBlock is either an individual port or port range
						if (PortBlock.find("-") > -1):
							#We have a port range
							PortRange=PortBlock.split("-")
							for OnePort in range(int(PortRange[0]), int(PortRange[1]) + 1):
								PortArray.append(OnePort)
						else:
							PortArray.append(PortBlock)
					#print len(PortArray), PortArray
				elif (len(line) >= 9) and (line[0:10] == "softmatch "):
					pass
					#softmatches look very weak at the moment; none give a productname.  Skip for the moment.
					#print "softmatch"

			ServiceHandle.close()

			if (CompileFail == 0):
				Debug(str(CompileSuccess) + " nmap service signatures successfully loaded.")
			else:
				Debug(str(CompileSuccess) + " nmap service signatures successfully loaded, unable to parse " + str(CompileFail) + " others.")
			return True
		except:
			Debug("Failed to load " + ServiceFileName)
			return False
	else:
		Debug("Unable to find " + ServiceFileName)
		return False



def ReportId(Type, IPAddr, Proto, State, Description):
	"""Print and log a new piece of network information."""

	#Can't use : for separator, IPv6, similarly '.' for ipv4
	#Can't use "/" because of filesystem
	#Don't want to use space because of filesystem
	#	Type,	IPAddr,	Proto		State			Optional description (may be empty)
	#	'IP',	IPaddr,	'IP',		dead or live,		p0f OS description
	#	'MA',	IPaddr, 'Ethernet',	MacAddr,		ManufDescription
	#	'TC',	IPaddr,	'TCP_'Port,	closed or open,		client description
	#	'TS',	IPaddr,	'TCP_'Port,	closed or listening,	server description
	#	'UC',	IPaddr,	'UDP_'Port,	open or closed,		udp client port description
	#	'US',	IPaddr,	'UDP_'Port,	open or closed,		udp server port description
	#	'DN',	IPaddr,	'A' or 'PTR',	hostname,		possible extra info
	#	'RO',	IPaddr, 'TTLEx',	router,			possible extra info

	global ServerDescription
	global ClientDescription
	global MacAddr
	global EtherManuf
	global LogFile
	global OSDescription
	#global DNSRecord
	global IsRouter
	#No longer needed
	#global MuteWarned
	
	Location = IPAddr + "," + Proto

	if (Type == "TS"):
		pass
		#Only assign this (and the others in this function) if Description non-null
		#if (Description != ''):
		#	#FIXME - assign externally to the right *ServerDescription
		#	ServerDescription[Location] = Description
	elif (Type == "TC"):
		if (Description != ''):
			ClientDescription[Location] = Description
	elif (Type == "US"):
		if (Description != ''):
			ManualServerDescription[Location] = Description
	elif (Type == "UC"):
		if (Description != ''):
			ClientDescription[Location] = Description
	elif (Type == "IP"):
		if (Description != ''):
			OSDescription[IPAddr] = Description
	elif (Type == "DN"):
		#FIXME - perhaps description could indicate low TTL?  <300?  <150?
		RememberDNS(IPAddr, State, Proto)
	elif (Type == "RO"):
		IsRouter[IPAddr] = True
	elif (Type == "MA"):
		State = State.upper()
		MacAddr[IPAddr] = State
		if EtherManuf.has_key(State[:8]):
			Description = EtherManuf[State[:8]]

	OutString = Type + "," + IPAddr + "," + Proto + "," + State + "," + Description

	print OutString
	if (LogFile != None):
		LogFile.write(OutString + '\n')
		LogFile.flush()


def isFQDN(Hostname):
	"""Boolean function: Checks to se if a hostname ends in a TLD.  Not a strict check, just some quick checks."""

	if len(Hostname) < 5:		#Shortest I can think of is "h.uk.", technically a domain, but still a dns object
		Debug("Hostname " + Hostname + " too short, ignoring.")
		return False
	elif not ( Hostname.endswith('.') ):
		Debug("Hostname " + Hostname + "doesn't end in '.', ignoring.")
		return False
	elif len(Hostname) >= 6 and ( Hostname.endswith('.biz.') or Hostname.endswith('.cat.') or Hostname.endswith('.com.') or Hostname.endswith('.edu.') ):
		return True
	elif len(Hostname) >= 6 and ( Hostname.endswith('.gov.') or Hostname.endswith('.int.') or Hostname.endswith('.mil.') or Hostname.endswith('.net.') ):
		return True
	elif len(Hostname) >= 6 and ( Hostname.endswith('.org.') or Hostname.endswith('.pro.') or Hostname.endswith('.tel.') ):
		return True
	elif len(Hostname) >= 7 and ( Hostname.endswith('.aero.') or Hostname.endswith('.asia.') or Hostname.endswith('.coop.') or Hostname.endswith('.info.')):
		return True
	elif len(Hostname) >= 7 and ( Hostname.endswith('.jobs.') or Hostname.endswith('.mobi.') or Hostname.endswith('.name.') ):
		return True
	elif len(Hostname) >= 9 and ( Hostname.endswith('.museum.') or Hostname.endswith('.travel.') ):
		return True
	elif re.search('\.[a-z][a-z]\.$', Hostname) != None:		#ends in 2 letter TLD
		return True
	else:
		Debug("Hostname " + Hostname + " has invalid TLD, ignoring.")
		return False



def RememberDNS(IPAddr, Hostname, RecType):
	"""Remember dns objects in DNSRecord and HostIPs.  RecType is 'A', 'PTR', or 'CNAME'."""
	global DNSRecord
	global HostIPs

	if (Hostname == ''):
		return

	if (not DNSRecord.has_key(IPAddr + "," + RecType)):		#If we haven't seen this hostname for this IPAddr,
		DNSRecord[IPAddr + "," + RecType] = [ Hostname ]	#make an array with just this hostname
	elif not (Hostname in DNSRecord[IPAddr + "," + RecType] ):	#If we _do_ have existing hostnames for this IP, but this new Hostname isn't one of them
		DNSRecord[IPAddr + "," + RecType].append(Hostname)	#Add this Hostname to the list

	if not(HostIPs.has_key(Hostname)):
		if not(isFQDN(Hostname)):	#We don't want to remember ips for names like "www", "ns1.mydom", "localhost", etc.
			return
		HostIPs[Hostname] = [ ]
	#else:
		#Since we've found "Hostname" as a key, we don't need to check if it's an FQDN again, we already checked once.

	if not( IPAddr in HostIPs[Hostname] ):		#If we haven't seen this IP address for this hostname,
		HostIPs[Hostname].append(IPAddr)	#Remember this new IP address for this hostname.


def processpacket(p):
	"""Extract information from a single packet off the wire."""

	global SynSentToTCPService
	global SynAckSentToTCPClient
	global LiveTCPService
	global LiveTCPClient
	global LiveUDPService
	global LiveUDPClient
	global NmapServerDescription
	global ManualServerDescription
	global ClientDescription
	global MacAddr
	global OSDescription
	global ServiceFPs
	global SipPhoneMatch
	global Devel
	global IsRouter
	global DNSRecord
	global HostIPs

	if (type(p) == Dot3) and (type(p['LLC']) == LLC):
		UnhandledPacket(p)
		#Spanning Tree Protocol
		#Debug("802.3")
		#p.show()
		#print type(p['LLC'])
	elif (p['Ethernet'] == None):
		Debug("non-ethernet packet")		#Need more details on how to handle.
		UnhandledPacket(p)
		#p.show()
		#print type(p)
		#quit()
	elif p['Ethernet'].type == 0x0806:		#ARP
		#pull arp data from here instead of tcp/udp packets, as these are all local
		if (p['ARP'].op == 1):			#1 is request ("who-has")
			pass
		if (p['ARP'].op == 2):			#2 is reply ("is-at")
			if (p['ARP.psrc'] != None) and (p['ARP.hwsrc'] != None):
				IPAddr=p['ARP.psrc']
				MyMac=p['ARP.hwsrc'].upper()
				if (not MacAddr.has_key(IPAddr)) or (MacAddr[IPAddr] != MyMac):
					ReportId("MA", IPAddr, 'Ethernet', MyMac, '')
			else:
				UnhandledPacket(p)
		else:
			UnhandledPacket(p)
	elif p['Ethernet'].type == 0x0800:		#IP
		sIP=str(p['IP'].src)
		dIP=str(p['IP'].dst)
		#Best to get these from arps instead; if we get them from here, we get router macs for foreign addresses.
		#if not MacAddr.has_key(sIP):
		#	ReportId("MA", sIP, "Ethernet", p['Ethernet'].src, '')
		#if not MacAddr.has_key(dIP):
		#	ReportId("MA", dIP, "Ethernet", p['Ethernet'].dst, '')

		if p['IP'].proto == 1:			#ICMP
			Type = p['ICMP'].type
			Code = p['ICMP'].code

			if (Type == 0):						#Echo reply
				if (not(OSDescription.has_key(sIP))):
					ReportId("IP", sIP, "IP", "live", 'icmp echo reply')
			elif (Type == 3) and (type(p[IPerror]) == IPerror):	#Unreachable, check that we have an actual embedded packet
				#if (type(p[IPerror]) != IPerror):
				#	p.show()
				#	print type(p[IPerror])
				#	quit()
				OrigdIP = p[IPerror].dst
				if (Code == 0):					#Net unreachable
					if (not(OSDescription.has_key(OrigdIP))):
						ReportId("IP", OrigdIP, "IP", "dead", 'net unreachable')
					if (not(IsRouter.has_key(sIP))):
						ReportId("RO", sIP, "NetUn", "router", "")
				elif (Code == 1):				#Host unreachable
					if (not(OSDescription.has_key(OrigdIP))):
						ReportId("IP", OrigdIP, "IP", "dead", 'host unreachable')
					if (not(IsRouter.has_key(sIP))):
						ReportId("RO", sIP, "HostUn", "router", "")
				elif (Code == 3) and (p[IPerror].proto == 17):	#Port unreachable and embedded protocol = 17, UDP, as it should be
					DNSServerLoc = p[IPerror].src + ",UDP_53"
					if (p[UDPerror].sport == 53) and (ManualServerDescription.has_key(DNSServerLoc)) and (ManualServerDescription[DNSServerLoc] == "dns/server"):
						#If orig packet coming from 53 and coming from a dns server, don't do anything (closed port on client is a common effect)
						#Don't waste time on port unreachables going back to a dns server; too common, and ephemeral anyways.
						pass
					else:
						#If orig packet coming from something other than 53, or coming from 53 and NOT coming from a dns server, log as closed
						OrigDPort = str(p[UDPerror].dport)
						OrigDstService = OrigdIP + ",UDP_" + OrigDPort
						if ((not LiveUDPService.has_key(OrigDstService)) or (LiveUDPService[OrigDstService] == True)):
							LiveUDPService[OrigDstService] = False
							ReportId("US", OrigdIP, "UDP_" + OrigDPort, "closed", "port unreachable")
				elif (Code == 3) and (p[IPerror].proto == 6) and (p[TCPerror].dport == 113):	#Port unreachable and embedded protocol = 6, TCP, which it shouldn't.  May be the same firewall providing the TCP FR's
					pass
				elif (Code == 6):				#Net unknown
					if (not(OSDescription.has_key(OrigdIP))):
						ReportId("IP", OrigdIP, "IP", "dead", 'net unknown')
				elif (Code == 7):				#Host unknown
					if (not(OSDescription.has_key(OrigdIP))):
						ReportId("IP", OrigdIP, "IP", "dead", 'host unknown')
				elif (Code == 9):				#Network Administratively Prohibited
					pass					#Can't tell much from this type of traffic.  Possibly list as firewall?
				elif (Code == 10):				#Host Administratively Prohibited
					pass
				elif (Code == 11):				#Network unreachable for TOS
					pass
				elif (Code == 12):				#Host unreachable for TOS
					pass
				elif (Code == 13):				#Communication Administratively prohibited
					pass
				else:
					UnhandledPacket(p)
			elif (Type == 8):					#ping
				#FIXME - check payload for ping sender type, perhaps
				pass
			elif (Type == 11):					#Time exceeded
				if (Code == 0):					#TTL exceeded
					if (not(IsRouter.has_key(sIP))):
						#FIXME - put original target IP as column 5?
						ReportId("RO", sIP, "TTLEx", "router", "")
				else:
					UnhandledPacket(p)
			else:
				UnhandledPacket(p)
		elif p['IP'].proto == 2:		#IGMP
			UnhandledPacket(p)
		elif p['IP'].proto == 6:		#TCP
			sport=str(p['TCP'].sport)
			dport=str(p['TCP'].dport)
			#print p['IP'].src + ":" + sport + " -> ", p['IP'].dst + ":" + dport,
			if (p['TCP'].flags & 0x17) == 0x12:	#SYN/ACK (RST and FIN off)
				CliService = dIP + ",TCP_" + sport
				if not SynAckSentToTCPClient.has_key(CliService):
					SynAckSentToTCPClient[CliService] = True

				#If we've seen a syn sent to this port and have either not seen any SA/R, or we've seen a R in the past:
				#The last test is for a service that was previously closed and is now open; report each transition once.
				Service = sIP + ",TCP_" + sport
				if ( (SynSentToTCPService.has_key(Service)) and ((not LiveTCPService.has_key(Service)) or (LiveTCPService[Service] == False)) ):
					LiveTCPService[Service] = True
					ReportId("TS", sIP, "TCP_" + sport, "listening", '')
			elif (p['TCP'].flags & 0x17) == 0x02:	#SYN (ACK, RST, and FIN off)
				Service = dIP + ",TCP_" + dport
				if not SynSentToTCPService.has_key(Service):
					SynSentToTCPService[Service] = True
				#Debug("trying to fingerprint " + sIP)
				try:
					p0fdata = p0f(p)
					#FIXME - reasonably common occurence, don't whine, just fix it.
					#if (len(p0fdata) >1):
					#	Debug("More than one OS fingerprint for " + sIP + ", using the first.")
					if (len(p0fdata) >=1):
						PDescription = p0fdata[0][0] + " " + p0fdata[0][1] + " (" + str(int(p0fdata[0][2]) + 1)	#FIXME - Grabbing just the first candidate, may need to compare correlation values; provided?
						if (p0fdata[0][2] == 0):
							PDescription = PDescription + " hop away)"
						else:
							PDescription = PDescription + " hops away)"
													#[N][2] param appears to be distance away in hops (but add 1 to this to get real hop count?)
						PDescription = PDescription.replace(',', ';')		#Commas are delimiters in output
						if (not(OSDescription.has_key(sIP))) or (OSDescription[sIP] != PDescription):
							OSDescription[sIP] = PDescription
							ReportId("IP", sIP, "IP", "live", PDescription)
				except:
					PDescription = 'p0f failure'
					if (not(OSDescription.has_key(sIP))) or (OSDescription[sIP] != PDescription):
						Debug("P0f failure in " + sIP + ":" + sport + " -> " + dIP + ":" + dport)
						OSDescription[sIP] = PDescription
						ReportId("IP", sIP, "IP", "live", PDescription)
			elif (p['TCP'].flags & 0x07) == 0x01:	#FIN (SYN/RST off)
				CliService = sIP + ",TCP_" + dport
				if ( (SynAckSentToTCPClient.has_key(CliService)) and ((not LiveTCPClient.has_key(CliService)) or (LiveTCPClient[CliService] == False)) ):
					LiveTCPClient[CliService] = True
					ReportId("TC", sIP, "TCP_" + dport, "open", '')
			elif (p['TCP'].flags & 0x07) == 0x04:	#RST (SYN and FIN off)
				#FIXME - handle rst going in the other direction?
				Service = sIP + ",TCP_" + sport
				if ( (SynSentToTCPService.has_key(Service)) and ((not LiveTCPService.has_key(Service)) or (LiveTCPService[Service] == True))  ):
					LiveTCPService[Service] = False
					ReportId("TS", sIP, "TCP_" + sport, "closed", '')
			elif ((p['TCP'].flags & 0x3F) == 0x15) and (sport == "113"):	#FIN, RST, ACK (SYN, PSH, URG off)
				#This may be a firewall or some other device stepping in for 113 with a FIN/RST.
				pass
			elif (p['TCP'].flags & 0x17) == 0x10:	#ACK (RST, SYN, and FIN off)
				#FIXME - check for UnhandledPacket placement in ACK
				FromPort = sIP + ",TCP_" + sport
				ToPort = dIP + ",TCP_" + dport
				Payload = str(p['Raw.load'])			#For some reason this doesn't handle p['Raw'].load
				if ( (LiveTCPService.has_key(FromPort)) and (LiveTCPService[FromPort] == True) and (LiveTCPService.has_key(ToPort)) and (LiveTCPService[ToPort] == True)):
					print "Logic failure: both " + FromPort + " and " + ToPort + " are listed as live services."
					UnhandledPacket(p)
				elif ((LiveTCPService.has_key(FromPort)) and (LiveTCPService[FromPort] == True)):	#If the "From" side is a known TCP server:
					if (not NmapServerDescription.has_key(FromPort) ):		#Check nmap fingerprint strings for this server port
						if (ServiceFPs.has_key(int(sport))):
							for OneTuple in ServiceFPs[int(sport)]:
								MatchObj = OneTuple[0].search(Payload)
								if (MatchObj != None):
									#Debugging:
									#FIXME - removeme once understood:
									#File "/home/wstearns/med/programming/python/passer/passer.py", line 504, in processpacket
									#OutputDescription = OutputDescription.replace('$' + str(Index), MatchObj.group(Index))
									#TypeError: expected a character buffer object
									if (OneTuple[1] == None):
										Debug("Null description for " + OneTuple[0])
										#quit()
									OutputDescription = OneTuple[1]
									if len(MatchObj.groups()) >= 1:
										#We have subexpressions matched, these need to be inserted into the description string
										for Index in range(1,len(MatchObj.groups())+1):
											#Example: Replace "$1" with MatchObj.group(1)
											OutputDescription = OutputDescription.replace('$' + str(Index), str(MatchObj.group(Index)))
									ReportId("TS", sIP, "TCP_" + sport, "listening", OutputDescription)
									NmapServerDescription[sIP + ",TCP_" + sport] = OutputDescription
									break					#Exit for loop, no need to check any more fingerprints now that we've found a match

					if (not NmapServerDescription.has_key(FromPort)):		#If the above loop didn't find a server description
						if (ServiceFPs.has_key('all')):				#Now recheck against regexes not associated with a specific port (port 'all').
							for OneTuple in ServiceFPs['all']:
								MatchObj = OneTuple[0].search(Payload)
								if (MatchObj != None):
									OutputDescription = OneTuple[1]
									if len(MatchObj.groups()) >= 1:
										#We have subexpressions matched, these need to be inserted into the description string
										for Index in range(1,len(MatchObj.groups())+1):
											OutputDescription = OutputDescription.replace('$' + str(Index), MatchObj.group(Index))
									ReportId("TS", sIP, "TCP_" + sport, "listening", OutputDescription)
									NmapServerDescription[sIP + ",TCP_" + sport] = OutputDescription
									break

					if (not ManualServerDescription.has_key(FromPort) ):
						if (sport == "22") and (Payload != None) and (Payload.find('SSH-') > -1):
							if ( (Payload.find('SSH-1.99-OpenSSH_') > -1) or (Payload.find('SSH-2.0-OpenSSH_') > -1) ):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "ssh/openssh")
								ManualServerDescription[sIP + ",TCP_" + sport] = "ssh/openssh"
							elif (Payload.find('SSH-1.5-') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "ssh/generic")
								ManualServerDescription[sIP + ",TCP_" + sport] = "ssh/generic"
								#LogNewPayload(ServerPayloadDir, FromPort, Payload)
							else:
								UnhandledPacket(p)
								#LogNewPayload(ServerPayloadDir, FromPort, Payload)
						elif (sport == "25") and (Payload != None) and (Payload.find(' ESMTP Sendmail ') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "smtp/sendmail")
							ManualServerDescription[sIP + ",TCP_" + sport] = "smtp/sendmail"
						elif (sport == "25") and (Payload != None) and (Payload.find(' - Welcome to our SMTP server ESMTP') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "smtp/generic")
							ManualServerDescription[sIP + ",TCP_" + sport] = "smtp/generic"
							UnhandledPacket(p)
							#LogNewPayload(ServerPayloadDir, FromPort, Payload)
						#Check for port 80 and search for "Server: " once
						elif (sport == "80") and (Payload != None) and (Payload.find('Server: ') > -1):
							if (Payload.find('Server: Apache') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/apache")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/apache"
							elif (Payload.find('Server: Embedded HTTP Server') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/embedded")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/embedded"
							elif (Payload.find('Server: gws') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/gws")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/gws"
							elif (Payload.find('Server: KFWebServer') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/kfwebserver")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/kfwebserver"
							elif (Payload.find('Server: micro_httpd') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/micro-httpd")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/micro-httpd"
							elif (Payload.find('Server: Microsoft-IIS') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/iis")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/iis"
							elif (Payload.find('Server: lighttpd') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/lighttpd")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/lighttpd"
							elif (Payload.find('Server: MIIxpc') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/mirrorimage")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/mirrorimage"
							elif (Payload.find('Server: mini_httpd') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/mini-httpd")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/mini-httpd"
							elif (Payload.find('Server: nc -l -p 80') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/nc")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/nc"
							elif (Payload.find('Server: nginx/') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/nginx")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/nginx"
							elif (Payload.find('Server: Nucleus') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/nucleus")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/nucleus"
							elif (Payload.find('Server: RomPager') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/rompager")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/rompager"
							elif (Payload.find('Server: Server') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/server")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/server"
							elif (Payload.find('Server: Sun-ONE-Web-Server/') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/sun-one")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/sun-one"
							elif (Payload.find('Server: TrustRank Frontend') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/trustrank")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/trustrank"
							elif (Payload.find('Server: YTS/') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/yahoo")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/yahoo"
							elif (Payload.find('HTTP/1.0 404 Not Found') > -1) or (Payload.find('HTTP/1.1 200 OK') > -1):
								ReportId("TS", sIP, "TCP_" + sport, "listening", "http/generic")
								ManualServerDescription[sIP + ",TCP_" + sport] = "http/generic"
								UnhandledPacket(p)
								#LogNewPayload(ServerPayloadDir, FromPort, Payload)
							else:
								UnhandledPacket(p)
								#LogNewPayload(ServerPayloadDir, FromPort, Payload)
						elif (sport == "110") and (Payload != None) and (Payload.find('POP3 Server Ready') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "pop3/generic")
							ManualServerDescription[sIP + ",TCP_" + sport] = "pop3/generic"
						elif (sport == "143") and (Payload != None) and (Payload.find('* OK dovecot ready') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "imap/dovecot")
							ManualServerDescription[sIP + ",TCP_" + sport] = "imap/dovecot"
						elif (sport == "143") and (Payload != None) and (Payload.find(' IMAP4rev1 ') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "imap/generic")
							ManualServerDescription[sIP + ",TCP_" + sport] = "imap/generic"
							UnhandledPacket(p)
							#LogNewPayload(ServerPayloadDir, FromPort, Payload)
						elif (sport == "783") and (Payload != None) and (Payload.find('SPAMD/1.1 ') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "spamd/spamd")
							ManualServerDescription[sIP + ",TCP_" + sport] = "spamd/spamd"
						elif ( (sport == "3128") or (sport == "80") ) and (Payload != None) and (Payload.find('Via: ') > -1) and (Payload.find(' (squid/') > -1):
							ReportId("TS", sIP, "TCP_" + sport, "listening", "proxy/squid")
							ManualServerDescription[sIP + ",TCP_" + sport] = "proxy/squid"
						else:
							UnhandledPacket(p)
							#LogNewPayload(ServerPayloadDir, FromPort, Payload)
				elif ((LiveTCPService.has_key(ToPort)) and (LiveTCPService[ToPort] == True)):		#If the "To" side is a known TCP server:
					ClientKey = sIP + ",TCP_" + dport	#Note: CLIENT ip and SERVER port
					if (not ClientDescription.has_key(ClientKey)):
						if (dport == "22") and (Payload != None) and ( (Payload.find('SSH-2.0-OpenSSH_') > -1) or (Payload.find('SSH-1.5-OpenSSH_') > -1)  ):
							ReportId("TC", sIP, "TCP_" + dport, "open", "ssh/openssh")
						#As cute as it is to catch this, it miscatches any relay that's carrying a pine-generated mail.
						#elif (dport == "25") and (Payload != None) and (Payload.find('Message-ID: <Pine.') > -1):
						#	ReportId("TC", sIP, "TCP_" + dport, "open", "smtp/pine")
						elif ( (dport == "80") or (dport == "3128") ) and (Payload != None) and (Payload.find('User-Agent: libwww-perl/') > -1):
							ReportId("TC", sIP, "TCP_" + dport, "open", "http/libwww-perl")
						elif ( (dport == "80") or (dport == "3128") ) and (Payload != None) and (Payload.find('User-Agent: Lynx') > -1):
							ReportId("TC", sIP, "TCP_" + dport, "open", "http/lynx")
						elif ( (dport == "80") or (dport == "3128") ) and (Payload != None) and (Payload.find('User-Agent: Mozilla') > -1)  and (Payload.find(' Firefox/') > -1):
							ReportId("TC", sIP, "TCP_" + dport, "open", "http/firefox")
						elif ( (dport == "80") or (dport == "3128") ) and (Payload != None) and (Payload.find('User-Agent: Wget/') > -1):
							ReportId("TC", sIP, "TCP_" + dport, "open", "http/wget")
						elif (dport == "143") and (Payload != None) and (Payload.find('A0001 CAPABILITY') > -1):
							ReportId("TC", sIP, "TCP_" + dport, "open", "imap/generic")
							#LogNewPayload(ClientPayloadDir, ClientKey, Payload)
						elif (dport == "783") and (Payload != None) and (Payload.find('PROCESS SPAMC') > -1):
							ReportId("TC", sIP, "TCP_" + dport, "open", "spamd/spamc")
						else:
							UnhandledPacket(p)
							#LogNewPayload(ClientPayloadDir, ClientKey, Payload)
				else:	#Neither port pair is known as a server
					UnhandledPacket(p)
					#Following is debugging at best; it should only show up early on as the sniffer listens to conversations for which it didn't hear the SYN/ACK
					#print "note: neither " + FromPort + " nor " + ToPort + " is listed as a live service."
			else:	#Other TCP flag combinations here
				UnhandledPacket(p)
		elif p['IP'].proto == 17 and (type(p['UDP']) == UDP):		#UDP.  We have to check the object type as well as we do get (corrupted? truncated?) packets with type 17 that aren't udp:  AttributeError: 'NoneType' object has no attribute 'sport'
			#FIXME - possibly run udp packets through ServiceFPs as well?
			sport=str(p['UDP'].sport)
			dport=str(p['UDP'].dport)
			SrcService = sIP + ",UDP_" + sport
			DstService = dIP + ",UDP_" + dport
			SrcClient = sIP + ",UDP_" + dport
			Payload = p['Raw.load']

			#Multicast DNS: http://files.multicastdns.org/draft-cheshire-dnsext-multicastdns.txt
			#- usually sent to 224.0.0.251 (or FF02::FB) (link-local multicast).
			#	- if ".local." in query, these MUST be the target IPs
			#	- non-local queries may be sent to these or normal dns servers
			#	- rdns queries for "254.169.in-addr.arpa." MUST be sent to 224.0.0.251
			#	- rdns queries for "8.e.f.ip6.arpa.", "9.e.f.ip6.arpa.","a.e.f.ip6.arpa.", and "b.e.f.ip6.arpa." MUST be sent to the IPv6 mDNS link-local multicast address FF02::FB.
			#- sent to udp port 5353
			#- generic clients may use "single-dns-object.local.", such as "sparrow.local."
			#- responses have IP TTL = 255 to check that packet originated on-lan

			#Multicast DNS, placed next to normal dns, out of numerical order
			if (dport == "5353") and ( (p['IP'].ttl == 1) or (p['IP'].ttl == 255) ):
				if ((not LiveUDPService.has_key(SrcClient)) or (LiveUDPService[SrcClient] == False)):
					LiveUDPService[SrcClient] = True
					if (dIP == "224.0.0.251"):
						ReportId("UC", sIP, "UDP_" + dport, "open", "mdns/broadcastclient")
					else:
						ReportId("UC", sIP, "UDP_" + dport, "open", "mdns/client")

					#Extract dns answers like with 53; change elif to if and add 5353 to ports on next if?
					#At the moment, no; scapy does not appear to parse 5353 as dns.
					#else:
					#	UnhandledPacket(p)
			#FIXME - add check for "if isinstance(p['DNS'],  whatevertype):	here and at all p[] accesses.
			elif (sport == "53") and (isinstance(p['DNS'], DNS)) and (p['DNS'].qr == 1):		#qr == 1 is a response
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					#FIXME - Also report the TLD from one of the query answers to show what it's willing to answer for?
					ReportId("US", sIP, "UDP_" + sport, "open", "dns/server")
				#Now we extract dns answers.  First, check that there's no dns error:
				if (p['DNS'].rcode == 0):			#No error
					DNSBlocks = [ ]
					CNAMERecs = [ ]				#We hold onto all cnames until we've processed all PTR's and A's here
					if (p['DNS'].ancount > 0):		#If we have at least one answer from the answer block, process it
						DNSBlocks.append(p[DNS].an)
					if (p['DNS'].arcount > 0):		#Likewise for the "additional" block
						DNSBlocks.append(p[DNS].ar)
					for OneAn in DNSBlocks:
						#Thanks to Philippe Biondi for showing me how to extract additional records.
						#Debug("Start dns extract" + str(p['DNS'].ancount))
						#OneAn = p[DNS].an
						#while OneAn is not NoPayload:		#This doesn't seem to stop at the end of the list; incorrect syntax.
						while isinstance(OneAn,DNSRR):		#Somewhat equivalent:	while not isinstance(an, NoPayload):
						
							#print "Type: " + str(type(OneAn))		#All of type scapy.DNSRR
							if (OneAn.rclass == 1) and (OneAn.type == 1):		#"IN" class and "A" type answer
								DNSIPAddr = OneAn.rdata
								DNSHostname = OneAn.rrname.lower()
								#Check new hostname to see if it's in the list.
								if (not DNSRecord.has_key(DNSIPAddr + ",A")) or (not(DNSHostname in DNSRecord[DNSIPAddr + ",A"])):
									ReportId("DN", DNSIPAddr, "A", DNSHostname, "")
							elif (OneAn.rclass == 1) and (OneAn.type == 2):			#"IN" class and "NS" answer
								pass							#Perhaps later
								#Like cnames, this is object -> nameserver hostname, so these would need to be queued like cnames until we're done with A's and PTR's.
							elif (OneAn.rclass == 1) and (OneAn.type == 5):			#"IN" class and "CNAME" answer
								CNAMERecs.append(OneAn)					#Remember the record; we'll process these after the PTR's and A's
							elif (OneAn.rclass == 1) and (OneAn.type == 6):			#"IN" class and "SOA" answer
								pass							#Not immediately useful, perhaps later
							elif (OneAn.rclass == 1) and (OneAn.type == 12):		#"IN" class and "PTR" type answer
																#For input of '182.111.59.66.in-addr.arpa.'  :
								DNSIPAddr = OneAn.rrname.replace(".in-addr.arpa.", "")		# '182.111.59.66'
								DNSIPAddr = DNSIPAddr.split('.')				# ['182', '111', '59', '66']
								DNSIPAddr.reverse()						# ['66', '59', '111', '182']
								DNSIPAddr = string.join(DNSIPAddr, '.')				# '66.59.111.182'
								#Check that we end up with a legal IPv4 address before continuing; we're getting garbage.
								if (re.search('^[1-9][0-9\.]*[0-9]$', DNSIPAddr) == None):
									Debug("Odd PTR rrname: " + OneAn.rrname)
								else:
									DNSHostname = OneAn.rdata.lower()
									if (not DNSRecord.has_key(DNSIPAddr + ",PTR")) or (not(DNSHostname in DNSRecord[DNSIPAddr + ",PTR"])):
										ReportId("DN", DNSIPAddr, "PTR", DNSHostname, "")
							elif (OneAn.rclass == 1) and (OneAn.type == 15):		#"IN" class and "MX" answer
								pass							#Possibly later
							elif (OneAn.rclass == 1) and (OneAn.type == 28):		#"IN" class and "AAAA" answer
								DNSIPAddr = OneAn.rdata.upper()
								DNSHostname = OneAn.rrname.lower()
								if (not DNSRecord.has_key(DNSIPAddr + ",AAAA")) or (not(DNSHostname in DNSRecord[DNSIPAddr + ",AAAA"])):
									ReportId("DN", DNSIPAddr, "AAAA", DNSHostname, "")

							#Move to the next DNS object in the "an" block
							OneAn = OneAn.payload
					for OneCNAME in CNAMERecs:		#Now that we have all A/PTR's, go back and turn cname records into pseudo-A's
						if isinstance(OneCNAME,DNSRR):
							Alias = OneCNAME.rrname.lower()
							Existing = OneCNAME.rdata.lower()
							if isFQDN(Alias) and isFQDN(Existing):
								if HostIPs.has_key(Existing):
									for OneIP in HostIPs[Existing]:				#Loop through each of the IPs for the canonical name, and
										if (not DNSRecord.has_key(OneIP + ",CNAME")) or (not(Alias in DNSRecord[OneIP + ",CNAME"])):
											ReportId("DN", OneIP, "CNAME", Alias, "")	#report them as kind-of A records for the Alias.
								#If we don't have a A/PTR record for "Existing", just ignore it.  Hopefully we'll get the Existing A/PTR in the next few answers, and will re-ask for the CNAME later, at which point we'll get a full cname record.
								#else:
								#	Debug("CNAME " + Alias + " -> " + Existing + " requested, but no IP's for the latter, skipping.")
							else:
								Debug("One of " + Alias + " and " + Existing + " isn't an FQDN, skipping cname processing.")
				elif (p['DNS'].rcode == 1):			#FormErr: server responding to an improperly formatted request
					pass
				elif (p['DNS'].rcode == 2):			#ServFail: domain exists, root nameservers list authoritative name servers, but authNS's won't answer queries
					pass
				elif (p['DNS'].rcode == 3):			#NXDOMAIN: root nameservers don't have any listing (domain doesn't exist or is on hold)
					pass
				elif (p['DNS'].rcode == 5):			#Query refused
					pass
				else:	#rcode indicates an error
					UnhandledPacket(p)
			elif (dport == "53") and (type(p['DNS']) == DNS) and (p['DNS'].qr == 0):	#dns query
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					LiveUDPClient[SrcClient] = True
					ReportId("UC", sIP, "UDP_" + dport, "open", "dns/client")
			elif (sport == "67") and (dport == "68"):		#Bootp/dhcp server talking to client
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "bootpordhcp/server")
			elif (sport == "68") and (dport == "67"):		#Bootp/dhcp client talking to server
				if (sIP != "0.0.0.0"):				#If the client is simply renewing an IP, remember it.
					if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "bootpordhcp/client")
				#else:						#If you want to record which macs are asking for addresses, do it here.
				#	pass
			elif (sport == "123") and (dport == "123") and (p['NTP'].stratum != ''):
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "ntp/generic")
			elif (dport == "123") and ( (dIP == "216.115.23.75") or (dIP == "216.115.23.76") or (dIP == "69.59.240.75") ):
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					LiveUDPClient[SrcClient] = True
					ReportId("UC", sIP, "UDP_" + dport, "open", "ntp/vonageclient")
			elif (sport == "123") and ( (sIP == "216.115.23.75") or (sIP == "216.115.23.76") or (sIP == "69.59.240.75") ):
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "ntp/vonageserver")
			elif (dport == "137"):			#netbios-ns
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (p['Ethernet'].dst.upper() == "FF:FF:FF:FF:FF:FF"):			#broadcast
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "netbios-ns/broadcastclient")
					elif (Payload != None) and (Payload.find('CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA') > -1):	#wildcard
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "netbios-ns/wildcardclient")
					else:
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "netbios-ns/unicastclient")
						UnhandledPacket(p)
			elif (sport == "500") and (dport == "500") and (p['ISAKMP'].init_cookie != ''):
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "isakmp/generic")
			elif (dport == "512"):			#BIFF
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('@') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "biff/client")
					else:
						UnhandledPacket(p)
			elif ( (dport == "1026") or (dport == "1027") or (dport == "1028") ):	#winpopup spam client
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and ( (Payload.find('Download Registry Update from:') > -1) or (Payload.find('CRITICAL ERROR MESSAGE! - REGISTRY DAMAGED AND CORRUPTED.') > -1) or (Payload.find('Your system registry is corrupted and needs to be cleaned immediately.') > -1) or (Payload.find('CRITICAL SYSTEM ERRORS') > -1) ):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "winpopup/spamclient")
					else:
						UnhandledPacket(p)
			elif (dport == "1434"):		#Probable mssql attack
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('Qh.dll') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "mssql/clientattack")
					else:
						UnhandledPacket(p)
			elif (sport == "1900") and (dport == "1900") and (dIP == "239.255.255.250"):		#SSDP
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('NOTIFY') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "ssdp/client")
					else:
						UnhandledPacket(p)
			elif (dport == "3865") and (dIP == "255.255.255.255"):		#XPL, http://wiki.xplproject.org.uk/index.php/Main_Page
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					LiveUDPClient[SrcClient] = True
					ReportId("UC", sIP, "UDP_" + dport, "open", "xpl/client")
			elif (sport == "5061") and (dport == "5061") and ( (dIP == "216.115.30.28") or (dIP == "69.59.227.77") or (dIP == "69.59.232.33") or (dIP == "69.59.240.84") ):		#Vonage SIP client
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('.vonage.net:5061 SIP/2.0') > -1):
						LiveUDPClient[SrcClient] = True
						SipMatch = SipPhoneMatch.search(Payload)
						if (SipMatch != None) and (len(SipMatch.groups()) >= 1):
							ReportId("UC", sIP, "UDP_" + dport, "open", "sip/vonage_client, phone number: " + SipMatch.group(1))
						else:
							ReportId("UC", sIP, "UDP_" + dport, "open", "sip/vonage_client")
					else:
						UnhandledPacket(p)
			elif (sport == "5061") and (dport == "5061") and ( (sIP == "216.115.30.28") or (sIP == "69.59.227.77") or (sIP == "69.59.232.33") or (sIP == "69.59.240.84") ):	#Vonage SIP server
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					if (Payload != None) and (Payload.find('.vonage.net:5061>') > -1):
						LiveUDPService[SrcService] = True
						ReportId("US", sIP, "UDP_" + sport, "open", "sip/vonage_server")
					else:
						UnhandledPacket(p)
			elif (sport == "6515") and (dport == "6514") and (dIP == "255.255.255.255"):		#mcafee ASaP broadcast, looking for a proxy out.  http://www.myasap.de/intl/EN/content/virusscan_asap/faq_new.asp
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('<rumor version=') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "asap/client")
					else:
						UnhandledPacket(p)
			elif ( (sport == "9052") or (sport == "9053") or (sport == "9054") ) and ( (sIP == "205.188.146.72") or (sIP == "205.188.157.241") or (sIP == "205.188.157.242") or (sIP == "205.188.157.243") or (sIP == "205.188.157.244") or (sIP == "64.12.51.145") or (sIP == "64.12.51.148") or (sIP == "149.174.54.131") ):	#Possibly AOL dns response
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					if (Payload != None) and (Payload.find('dns-01') > -1):
						LiveUDPService[SrcService] = True
						ReportId("US", sIP, "UDP_" + sport, "open", "aoldns/server")
					else:
						UnhandledPacket(p)
			elif (sport == "27005") and ( (dport == "27016") or (dport == "27017") ):				#Halflife client live game
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					LiveUDPClient[SrcClient] = True
					ReportId("UC", sIP, "UDP_" + dport, "open", "halflife/client")
			elif (dport == "27013") and (dIP == "207.173.177.12"):				#variable payload, so can't (Payload != None) and (Payload.find('Steam.exe') > -1)				#Halflife client
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					LiveUDPClient[SrcClient] = True
					ReportId("UC", sIP, "UDP_" + dport, "open", "halflife/client")
			elif (sport == "27013") and (sIP == "207.173.177.12"):							#halflife server
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "halflife/server")
			elif ( (sport == "27016") or (sport == "27017") ) and (dport == "27005"):				#halflife server live game
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "halflife/server")
			elif ( (dport == "27015") or (dport == "27016") or (dport == "27025") or (dport == "27026") ):		#Variable payload, so can't: (Payload != None) and (Payload.find('basic') > -1)	#Halflife client
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					LiveUDPClient[SrcClient] = True
					ReportId("UC", sIP, "UDP_" + dport, "open", "halflife/client")
			elif (dport == "27017") and ( (dIP == "69.28.148.250") or (dIP == "69.28.156.250") or (dIP == "72.165.61.161") or (dIP == "72.165.61.185") or (dIP == "72.165.61.186") or (dIP == "72.165.61.188") or (dIP == "68.142.64.164") or (dIP == "68.142.64.165") or (dIP == "68.142.64.166") ):	#Steamfriends client
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('VS01') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "steamfriends/client")
					else:
						UnhandledPacket(p)
			elif (sport == "27017") and ( (sIP == "69.28.148.250") or (sIP == "69.28.156.250") or (sIP == "72.165.61.161") or (sIP == "72.165.61.185") or (sIP == "72.165.61.186") or (sIP == "72.165.61.188") or (sIP == "68.142.64.164") or (sIP == "68.142.64.165") or (sIP == "68.142.64.166") ):	#Steamfriends server
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					if (Payload != None) and (Payload.find('VS01') > -1):
						LiveUDPService[SrcService] = True
						ReportId("US", sIP, "UDP_" + sport, "open", "steamfriends/server")
					else:
						UnhandledPacket(p)
			elif ( (sport == "21020") or (sport == "21250") or (sport == "27016") or (sport == "27017") or (sport == "27018") or (sport == "27030") or (sport == "27035") or (sport == "27040") or (sport == "28015") ):							#halflife server
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					if (Payload != None) and (Payload.find('Team Fortress') > -1):
						LiveUDPService[SrcService] = True
						ReportId("US", sIP, "UDP_" + sport, "open", "halflife/server")
					else:
						UnhandledPacket(p)
			elif (sport == "27019"):							#halflife server
				if ((not LiveUDPService.has_key(SrcService)) or (LiveUDPService[SrcService] == False)):
					LiveUDPService[SrcService] = True
					ReportId("US", sIP, "UDP_" + sport, "open", "halflife/server")
			elif ( (dport == "1265") or (dport == "20100") or (dport == "21550") or (dport == "27000") or (dport == "27017") or (dport == "27018") or (dport == "27019") or (dport == "27022") or (dport == "27030") or (dport == "27035") or (dport == "27050") or (dport == "27078") or (dport == "27080") or (dport == "28015") or (dport == "28100") or (dport == "45081") ):		#Halflife client
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('Source Engine Query') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "halflife/client")
					else:
						UnhandledPacket(p)
			elif (dport == "24441"):			#Pyzor
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('User:') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "pyzor/client")
					else:
						UnhandledPacket(p)
			#FIXME - interesting issue; the ttl<5 test will catch traceroutes coming into us, but not ones we're creating to go out.  Hmmm.
			elif ( (dport >= "33434") and (dport <= "33524") ) and (p['IP'].ttl <= 5):	#udptraceroute client
				if ((not LiveUDPClient.has_key(sIP + "UDP_33434")) or (LiveUDPClient[sIP + "UDP_33434"] == False)):
					LiveUDPClient[sIP + "UDP_33434"] = True
					ReportId("UC", sIP, "UDP_33434", "open", "udptraceroute/client")
			elif (dport == "40348"):
				if ((not LiveUDPClient.has_key(SrcClient)) or (LiveUDPClient[SrcClient] == False)):
					if (Payload != None) and (Payload.find('HLS') > -1):
						LiveUDPClient[SrcClient] = True
						ReportId("UC", sIP, "UDP_" + dport, "open", "halflife/client")
					else:
						UnhandledPacket(p)
			elif (p['IP'].frag > 0):
				UnhandledPacket(p)
			elif (sIP == "207.46.51.74") or (sIP == "65.55.251.10"):				#Bigfish.com - dns?
				UnhandledPacket(p)
			elif (sIP == "61.215.106.146"):				#junk
				UnhandledPacket(p)
			else:
				UnhandledPacket(p)
		else:
			Debug("Other IP protocol (" + str(p['IP'].src) + "->" + str(p['IP'].dst) + "): " + str(p['IP'].proto))
			UnhandledPacket(p)
	elif p['Ethernet'].type == 0x86DD:		#IPv6
		UnhandledPacket(p)
	else:
		print "Unregistered ethernet type:", p['Ethernet'].type
		UnhandledPacket(p)


def Usage():
	if (len(sys.argv) > 0):
		Debug(str(sys.argv[0]) + " command line options:")
	else:
		Debug("passer.py command line options:")
	Debug("[-h]\t\t\tShow this help screen.")
	Debug("[-i interfacename]\t\tread packets from a specific interface instead of all network interfaces.")
	Debug("[-r packetfile.pcap]\t\tread packets from a pcap file instead of from network interfaces.")
	Debug("[-l logfilename]\t\tsave all output in text format to this file as well.")
	Debug("[-u unhandledfilename]\t\tsave all unhandled packets to this pcap file.")
	Debug("['bpf filter']\t\tUse this bpf filter to limit packets seen (last parameter).")
	quit()


#======== Start of main code. ========

#Debug(str(len(sys.argv) - 1) + " params")

ParamPointer = 1
LogFilename = ''
UnhandledFilename = ''
PcapFilename = ''
InterfaceName = ''
bpfilter = ''
while (ParamPointer < len(sys.argv)):
	#Debug("Processing: " + sys.argv[ParamPointer])

	if (sys.argv[ParamPointer] == "-h"):
		Usage()
	elif (sys.argv[ParamPointer] == "-i"):
		if (ParamPointer + 1 >= len(sys.argv)):
			Debug("'-i' command line option requested, but no interface following it, exiting.")
			Usage()
		elif (PcapFilename != ''):
			print "Both '-i' and '-r' requested, exiting."
			Usage()
		else:
			InterfaceName = sys.argv[ParamPointer + 1]
			ParamPointer += 1
			#Debug("Interface name is " + str(InterfaceName))
	elif (sys.argv[ParamPointer] == "-l"):
		if (ParamPointer + 1 >= len(sys.argv)):
			Debug("'-l' command line option requested, but no filename following it, exiting.")
			Usage()
		else:
			LogFilename = sys.argv[ParamPointer + 1]
			ParamPointer += 1
			#Debug("Log file is " + str(LogFilename))
	elif (sys.argv[ParamPointer] == "-u"):
		if (ParamPointer + 1 >= len(sys.argv)):
			Debug("'-u' command line option requested, but no filename following it, exiting.")
			Usage()
		else:
			UnhandledFilename = sys.argv[ParamPointer + 1]
			ParamPointer += 1
			Debug("Unhandled file is " + str(UnhandledFilename))
	elif (sys.argv[ParamPointer] == "-r"):
		if (ParamPointer + 1 >= len(sys.argv)):
			Debug("'-r' command line option requested, but no filename following it, exiting.")
			Usage()
		elif (InterfaceName != ''):
			Debug("Both '-i' and '-r' requested, exiting.")
			Usage()
		else:
			PcapFilename = sys.argv[ParamPointer + 1]
			ParamPointer += 1
			#Debug("Pcap file is " + PcapFilename)
	elif (ParamPointer + 1 == len(sys.argv)):		#If there's a sole parameter left, that should be the bpfilter.
		bpfilter = sys.argv[ParamPointer]
	else:
		Debug("Too many parameters, exiting.")
		Usage()
	ParamPointer += 1

#FIXME - drop isfile check; could be named pipe or, i suppose, a device.  Perhaps test writable?
if (LogFilename != ''):		#and os.path.isfile(LogFilename):
	try:
		LogFile=open(LogFilename, 'a')
	except:
		Debug("Unable to append to " + LogFilename + ", no logging will be done.")
		LogFile = None
else:
	LogFile = None

if (UnhandledFilename != ''):
	try:
		UnhandledFile = PcapWriter(filename=UnhandledFilename)
	except:
		Debug("Unable to open " + UnhandledFilename + ", no unhandled packets will be saved.")
		UnhandledFile = None
else:
	UnhandledFile = None


Debug("BPFilter is " + bpfilter)
#Hmmm, bpfilter appears not to work.  It loads correctly into the variable, but the sniff command appears to ignore it.


if (not(os.path.isfile("/etc/p0f/p0f.fp"))):
	Debug("/etc/p0f/p0f.fp not found; please install p0f version 2 to enable OS fingerprinting.")
LoadMacData('/usr/share/ettercap/etter.finger.mac')
LoadMacData('/usr/local/share/nmap/nmap-mac-prefixes')
LoadMacData('/usr/local/share/wireshark/manuf')
#LoadMacData('/usr/local/share/ethereal/manuf')
LoadMacData('/usr/local/share/arp-scan/ieee-oui.txt')
if (len(EtherManuf) == 0):
	Debug("None of the default mac address listings found.  Please install ettercap, nmap, wireshark, and/or arp-scan.")
else:
	Debug(str(len(EtherManuf)) + " mac prefixes loaded.")

LoadNmapServiceFP('/usr/local/share/nmap/nmap-service-probes')
if (len(ServiceFPs) == 0):
	Debug("Can't locate /usr/local/share/nmap/nmap-service-probes.  Please install nmap to support more server descriptions.")
else:
	Debug("Fingerprints for " + str(len(ServiceFPs)) + " ports loaded.")

#FIXME - change to dictionary of compiled regexes?
SipPhoneMatch = re.compile('Contact: ([0-9-]+) <sip')



#To set scapy options:
#conf.verb = 0
#conf.iface = 'eth1'			#Default: every interface
#conf.nmap_base  = '/usr/share/nmap/nmap-os-fingerprints'
#conf.p0f_base   = '/etc/p0f.fp'
#conf.promisc = 1
conf.sniff_promisc = 1
conf.filter = bpfilter		#Neither this nor adding "filter=bpfilter" to each sniff line seems to actually apply the bpf.  Hmmm.


if (PcapFilename != ''):
	sniff(store=0, offline=PcapFilename, filter=bpfilter, prn=lambda x: processpacket(x))
elif (InterfaceName != ''):
	sniff(store=0, iface=InterfaceName, filter=bpfilter, prn=lambda x: processpacket(x))
else:
	sniff(store=0, filter=bpfilter, prn=lambda x: processpacket(x))
#To limit to the first 500 packets, add ", count=500" at the end of the "sniff" command inside the last paren




#Bill's notes to himself.
#To debug:
#p.show()
#scapy.ls(scapy.Ether)

#No longer needed
#MuteWarned = { }		#Boolean dictionary: if true for a given key, we've warned that we won't report this object any more.

#Former code to mute multiple IP's for a single mac:
#		Found = False
#		for Key in MacAddr.keys():
#			if (MacAddr[Key] == State):
#				Found=True
#				break
#		if Found:
#			if (not MuteWarned.has_key(State)):
#				Debug("Duplicate IPs found for " + State + ", no longer printing for it.")
#				MuteWarned[State] = True
#		else:

#if not IPCount.has_key(p['IP'].src):
#	IPCount[p['IP'].src] = 0
#IPCount[p['IP'].src] += 1

#TODO:
#- sql insertion
#- Identify routers/nics with >1 IP
#- fingerprint OS based on echo payloads
#- DHCP identification
#- for TS and TC; if we already have a T?_21 and the port in question is >=32768, tag as "potential ftp data"?
#- in arp capture section, ship off an "arp who-has" or "icmp echo" to that IP, wrong/fixed mac.  Passively
#  grab response later, look for mac, and record promisc nic.  Must have CLP to actively probe.  See scapy.promiscping for approach
#- extract, store, and use dns PTR replies so we can report hostnames.  :-)
#- reduce to a few dictionaries
#- pickle import on entry, export on ctrl-c or exit
#- try/except around live sniff
#- check for file readable before offlinepcapread
#- for DNS records, extract the TLD as column 4?  Prob not.
#- for every IP associated with a packet, append that packet to /path/to/a/b/c/d/a.b.c.d.pcap
#- normalize high ttl traceroute ports too
#- .find's to ignore 127.x.y.z rbl A records?
	# .zen.spamhaus.org.
	# .dnsbl.sorbs.net.
	# .multi.surbl.org.
	# .multi.uribl.com.
	# .dob.sibl.support-intelligence.net.
	# .fulldom.rfc-ignorant.org.
	# .bl.open-whois.org.
	# .combined.njabl.org.
	# .rhsbl.ahbl.org.
	# .list.dnswl.org.
#- broadcast IPs
#- check class types of objects before extracting fields to avoid:
#	File "/home/wstearns/med/programming/python/passer/passer.py", line 652, in processpacket
#	sport=str(p['UDP'].sport)
#	AttributeError: 'NoneType' object has no attribute 'sport'
#- extract all dns objects (A, PTR, and CNAME done.  AAAA(code 28) needed.  MX(code 15)?  NS(code 2)? SOA(code 6)?).	http://www.dns.net/dnsrd/rr.html
#- check for empty name in dns
#- block "localhost" as a name for anything but ::1 and 127.0.0.1

#Done:
#- New signatures from:
#	- pads-signature-list (appears to be an import of the nmap-service-probes anyways)
#	- nmap-service-probes (done)
#- Remove p/Skype VoIP data channel/ signature (done)
#- Replace "$N"'s in nmap descriptions with corresponding match groups (done)
#- Double "\"'s in re's to handle \b?  Doesn't appear to be needed; none of the nmap sigs use \b. (done)
#- check for *LiveClient.has_key and ... == True in front of every .find()/.match() (done)
#- check if /i and other regex flags
#- Use unreachables
#- restructure "p['...']" references
#- command line parsing
#- 2nd dns pass for additional records
#- make-hosts
#- lowercase all dns objects?
#- unhandled packet function
	#- function to handle interesting packets; queue 1024 of them to write out to pcap.
#- 3rd dns pass for CNAMES (keep track of _fully qualified hostnames_ from A and PTR, match all)


#Temporary code to load up a stub ServiceFPs
#ServiceFPs[80] = [ ]
#MatchTuple=('Apache', "http/apachewebserver")
#Above works just fine, but lets precompile regexes as they're being stored:
#"M" is needed so "^" and "$" work in a multiline payload block
#MatchTuple=(re.compile('^Server: Apache/', re.M), "http/apachewebserver")
#ServiceFPs[80].append(MatchTuple)
#print ServiceFPs
#Result:	{80: [('Apache', 'http/apachewebserver')]}

#Taken from the ack block, under NmapServiceDescription
						#Stub code to test ServiceFPs regex matching
						#if (sport == "80"):
						#	print "In regex block"
						#	MatchTuple=ServiceFPs[80][0]
						#	#CompiledRegex=re.compile(MatchTuple[0])
						#	#Above works just fine with non-compiled.  Let's precompile at insert time to save time - works fine :-D :
						#	CompiledRegex=MatchTuple[0]
						#	#MatchObject=CompiledRegex.search(Payload)
						#	#if (MatchObject.start > -1):		#Nope, "NoneType has no attribute "start""
						#	#if (MatchObject != None):
						#	#Simpler than above and works:
						#	if (CompiledRegex.search(Payload) != None):		#re.M flag only works at compile time, not here
						#		print "Test match found", MatchTuple[1]

#elif (string.hexdigits.find(line[0]) > -1) and (string.hexdigits.find(line[1]) > -1) ...:  #Nah.  :-)


#From LoadNmapServiceFP
#Fixed these regex issues above with replaces.
#elif (MatchString.find(' CDDBP server ') > -1) or (MatchString.find(' running FileZilla Server ') > -1) or (MatchString.find('220-SECURE FTP SERVER VERSION') > -1):
#	#Regex issue; "-" in [] character sets is not at the beginning or end"
#	pass



#>>> dir(p[0])
#['__class__', '__contains__', '__delattr__', '__dict__', '__div__',
#'__doc__', '__eq__', '__getattr__', '__getattribute__', '__getitem__',
#'__gt__', '__hash__', '__init__', '__iter__', '__len__', '__lt__',
#'__metaclass__', '__module__', '__mul__', '__ne__', '__new__',
#'__nonzero__', '__rdiv__', '__reduce__', '__reduce_ex__', '__repr__',
#'__rmul__', '__setattr__', '__str__', '__weakref__', 'add_payload',
#'add_underlayer', 'aliastypes', 'answers', 'build', 'build_payload',
#'build_ps', 'canvas_dump', 'command', 'copy', 'decode_payload_as',
#'default_fields', 'default_payload_class', 'display', 'dissect',
#'dissection_done', 'do_build', 'do_build_ps', 'do_dissect',
#'do_dissect_payload', 'do_init_fields', 'extract_padding', 'fields',
#'fields_desc', 'fieldtype', 'from_hexcap', 'get_field',
#'getfield_and_val', 'getfieldval', 'getlayer', 'guess_payload_class',
#'hashret', 'haslayer', 'hide_defaults', 'init_fields', 'initialized',
#'lastlayer', 'libnet', 'mysummary', 'name', 'overload_fields',
#'overloaded_fields', 'packetfields', 'payload', 'payload_guess',
#'pdfdump', 'post_build', 'post_dissect', 'post_dissection',
#'post_transforms', 'pre_dissect', 'psdump', 'remove_payload',
#'remove_underlayer', 'show', 'show2', 'show_indent', 'sprintf',
#'summary', 'time', 'underlayer']



#Success notes:
#
#>>> p[0].answers 
#<bound method Ether.answers of <Ether  dst=00:00:00:00:00:00
#src=00:00:00:00:00:00 type=IPv4 |<IP  version=4L ihl=5L tos=0xc0 len=108
#id=19421 flags= frag=0L ttl=64 proto=icmp chksum=0x2ff2 src=127.0.0.1
#dst=127.0.0.1 options='' |<ICMP  type=dest-unreach code=3 chksum=0x2bb9
#id=0x0 seq=0x0 |<IPerror  version=4L ihl=5L tos=0x0 len=80 id=0 flags=DF
#frag=0L ttl=64 proto=udp chksum=0x3c9b src=127.0.0.1 dst=127.0.0.1
#options='' |<UDPerror  sport=45279 dport=biff len=60 chksum=0xfe4f |<Raw 
#load='wstearns@1373933957:/home/wstearns/mail/bayes99-spam' |>>>>>>>
#
#>>> p[0].fields 
#{'src': '00:00:00:00:00:00', 'dst': '00:00:00:00:00:00', 'type': 2048}
#
#>>> p[0]['IP'].fields
#{'frag': 0L, 'src': '127.0.0.1', 'proto': 1, 'tos': 192, 'dst':
#'127.0.0.1', 'chksum': 12274, 'len': 108, 'options': '', 'version': 4L,
#'flags': 0L, 'ihl': 5L, 'ttl': 64, 'id': 19421}
#
#>>> p[0]['ICMP'].fields
#{'code': 3, 'type': 3, 'id': 0, 'seq': 0, 'chksum': 11193}
#
#>>> p[0]['IPerror'].fields
#Traceback (most recent call last):
#File "<stdin>", line 1, in <module>
#AttributeError: 'NoneType' object has no attribute 'fields'
#
#>>> p[0]['Raw'].fields
#{'load': 'wstearns@1373933957:/home/wstearns/mail/bayes99-spam'}
#
#>>> print p[0]['Raw']        
#wstearns@1373933957:/home/wstearns/mail/bayes99-spam

#help(ICMPerror)
#...


#From LoadNmapServiceFP
#Rest are replaced by the first two generic "[\w-" and "[\d-" rules
#MatchString=MatchString.replace("[\w-_.]","[\w_.-]")
#MatchString=MatchString.replace("[\w-.]","[\w.-]")
#MatchString=MatchString.replace("[\d-.]","[\d.-]")
#MatchString=MatchString.replace("[\w-_. ]","[\w_. -]")
#MatchString=MatchString.replace("[\w-_.@]","[\w_.@-]")
#MatchString=MatchString.replace("[\w-_.\s]","[\w_.\s-]")
#MatchString=MatchString.replace("[\w-_]","[\w_-]")
#MatchString=MatchString.replace("[\d-_.]","[\d_.-]")
#MatchString=MatchString.replace("[\w-_.)(/]","[\w_.)(/-]")
#MatchString=MatchString.replace("[\w-_+. ]","[\w_+. -]")
#MatchString=MatchString.replace("[\w-_.+]","[\w_.+-]")
#MatchString=MatchString.replace("[\w-_+. ()]","[\w_+. ()-]")
#MatchString=MatchString.replace("[\w-+.]","[\w+.-]")
#MatchString=MatchString.replace("[\w-.+]","[\w.+-]")
#MatchString=MatchString.replace("[\w-_./]","[\w_./-]")
#MatchString=MatchString.replace("[\w-+]","[\w+-]")
#MatchString=MatchString.replace("[\w-+/.]","[\w+/.-]")
#MatchString=MatchString.replace("[\w-_.:/]","[\w_.:/-]")
#MatchString=MatchString.replace("[\w-_.;]","[\w_.;-]")
#MatchString=MatchString.replace("[\d-/]","[\d/-]")
#MatchString=MatchString.replace("[\w-. ]","[\w. -]")


#From processpacket, icmp
		#p.show()
		#print p['Raw.load']
		#print p['ICMP.payload']			#Doesn't exist
		#172.27.1.99 == 0x AC 1B 01 63
		#print p				#Just gives a binary blob
		#scapy.dir(scapy.p)			#Can't seem to find the right syntax
		#print p.keys()				#Nope
		#help(p)				#interactive help on structures
		#print p.fields_desc			#Just Ether fields
		#print p.IP.__dict__			#Nope
		#print p['IP'].__dict__			#Like IP.__dict__, but focused on IP layer
		#print p['IPerror'].__dict__		#Fails, type None
		#print p['ICMP'].__dict__		#Focuses on ICMP
		#print p['IPerror.dst'], "unreachable."  #Just gives None unreachable
		#quit()
#else:
#	p.show()


#print p['ICMP.type'], p['ICMP.code']
##Nope print p['ICMP.payload.IP.proto']
#print p['Raw.load']	#OK
##print p['Raw.load.IP.proto']	#Nope
#print 'portcheck:' + str(p['UDPerror.sport']) + ":", p['IPerror.proto']
#It doesn't look like IPerror/UDPerror fields actually get values.  Hmmmmm.
#But oddly enough, p.show does seem to _show_ the values.  Hmmmm.

#Stripme once we have UDPerror fields
#sport=str(p['UDP.sport'])
#dport=str(p['UDP.dport'])
#Service = sIP + ",UDP_" + sport
#if (sport == "53") and (p['DNS.qr'] == 1):		#For some reason I can't check: (p.has_key('DNS.qr'))
#	if ((not LiveUDPService.has_key(Service)) or (LiveUDPService[Service] == False)):
#		LiveUDPService[Service] = True
#		ReportId("US", sIP, "UDP_" + sport, 'open', "dns/generic")

#To identify the type of an object: type(variable) or variable.__class__


#From UDP DNS section:
#Debug("There are " + str(len(p['DNS'].an)) + " answers in this packet.")		#Wrong; I think this gives the number of bytes.
#OrigDNSQuery = p['DNS'].qd.qname
#The entire an block is p['DNS'].an , try p['DNS'].an.show()
#This is of class DNSRR.  How do I get 2nd and further dns objects?
# p[0]['DNS'].an.show()   

# ###[ DNS Resource Record ]###
# rrname= 'www.stearns.org.'
# type= CNAME
# rclass= IN
# ttl= 38400
# rdlen= 0
# rdata= 'virtual.stearns.org.'

# ###[ DNS Resource Record ]###
# rrname= 'virtual.stearns.org.'
# type= A
# rclass= IN
# ttl= 38400
# rdlen= 0
# rdata= '66.59.111.182'

# ###[ DNS Resource Record ]###
# rrname= '182.111.59.66.in-addr.arpa.'
# type= PTR
# rclass= IN
# ttl= 15353
# rdlen= 0
# rdata= 'slartibartfast.pa.net.'

#|###[ DNS Resource Record ]###
#|  rrname= 'nuelig.com.'
#|  type= NS
#|  rclass= IN
#|  ttl= 172800
#|  rdlen= 0
#|  rdata= 'ns2.tenthingstodowiz.com.'

#|###[ DNS Resource Record ]###
#|  rrname= 'stearns.org.'
#|  type= SOA
#|  rclass= IN
#|  ttl= 38400
#|  rdlen= 0
#|  rdata= '\x0eslartibartfast\x02pa\x03net\x00\x04root\xc0)w\xa0\xda\xe5\x00\x00*0\x00\x00\x0e\x10\x006\xee\x80\x00\x00\x1c '
                                                                                    
