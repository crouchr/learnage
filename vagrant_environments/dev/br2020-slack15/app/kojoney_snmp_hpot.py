#!/usr/bin/python
#
#SNMPv2-MIB::sysDescr.0 = STRING: Cisco IOS Software, 7200 Software (C7200-SPSERVICESK9-M), Version 12.4(11)T1, RELEASE SOFTWARE (fc5)
#Technical Support: http://www.cisco.com/techsupport
#Copyright (c) 1986-2007 by Cisco Systems, Inc.
#Compiled Thu 25-Jan-07 19:57 by prod_rel_team
#SNMPv2-MIB::sysObjectID.0 = OID: SNMPv2-SMI::enterprises.9.1.222
#SNMPv2-MIB::sysUpTime.0 = Timeticks: (3413221624) 395 days, 1:10:16.24
#SNMPv2-MIB::sysContact.0 = STRING: "Slaptijack" 
#SNMPv2-MIB::sysName.0 = STRING: ROUTER.slaptijack.com
#SNMPv2-MIB::sysLocation.0 = STRING: USA
#SNMPv2-MIB::sysServices.0 = INTEGER: 78
#SNMPv2-MIB::sysORLastChange.0 = Timeticks: (0) 0:00:00.00
#SNMPv2-MIB::sysORLastChange.0 = No more variables left in this MIB View (It is past the end of the MIB tree)

# redirect stderr to a file 
# python kojoney_snmpd.py &> junk.txt &


import sys

from pysnmp.entity import engine, config
from pysnmp.carrier.asynsock.dgram import udp
#from pysnmp.carrier.asynsock.dgram import udp6
from pysnmp.entity.rfc3413 import cmdrsp, context

from pysnmp import debug
#from mysnmp_debug import debug
#sys.stderr = open('kojoney_snmpd.log', 'w')
debug.setLogger(debug.Debug('all'))
#sys.stderr = open('kojoney_snmpd.log', 'w')
#fpout = open("snmpd.log","w")
#debug.Debug.defaultPrinter = fpout

# Create SNMP engine with autogenernated engineID and pre-bound
# to socket transport dispatcher
snmpEngine = engine.SnmpEngine()

# Setup UDP over IPv4 transport endpoint
#config.addSocketTransport(snmpEngine,udp.domainName,udp.UdpSocketTransport().openServerMode(('127.0.0.1', 161)))
config.addSocketTransport(snmpEngine,udp.domainName,udp.UdpSocketTransport().openServerMode(('192.168.1.68', 161)))
                
# Setup UDP over IPv6 transport endpoint
#config.addSocketTransport(
#    snmpEngine,
#    udp6.domainName,
#    udp6.Udp6Transport().openServerMode(('::1', 161))
#    )
                
# Create and put on-line my managed object
sysDescr, = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('SNMPv2-MIB', 'sysDescr')
MibScalarInstance, = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.importSymbols('SNMPv2-SMI', 'MibScalarInstance')
#sysDescrInstance = MibScalarInstance(sysDescr.name, (0,), sysDescr.syntax.clone('Example Command Responder'))
DESCR="Cisco IOS Software, 7200 Software (C7200-SPSERVICESK9-M), Version 12.4(11)T1, RELEASE SOFTWARE (fc5) Technical Support: http://www.cisco.com/techsupport Copyright (c) 1986-2007 by Cisco Systems, Inc. Compiled Thu 25-Jan-07 19:57 by prod_rel_team"  
sysDescrInstance = MibScalarInstance(sysDescr.name, (0,), sysDescr.syntax.clone(DESCR))
snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder.exportSymbols('PYSNMP-EXAMPLE-MIB', sysDescrInstance=sysDescrInstance)  # creating MIB
                        
# v1/2 setup
config.addV1System(snmpEngine, 'test-agent', 'public')
                        
# v3 setup
#                        config.addV3User(
#                            snmpEngine, 'test-user',
#                                config.usmHMACMD5AuthProtocol, 'authkey1',
#                                    config.usmDESPrivProtocol, 'privkey1'
#                                        )
                                            
# VACM setup
config.addContext(snmpEngine, '')
config.addRwUser(snmpEngine, 1, 'test-agent', 'noAuthNoPriv', (1,3,6)) # v1
config.addRwUser(snmpEngine, 2, 'test-agent', 'noAuthNoPriv', (1,3,6)) # v2c
#config.addRwUser(snmpEngine, 3, 'test-user', 'authPriv', (1,3,6)) # v3
                                           
# SNMP context
snmpContext = context.SnmpContext(snmpEngine)
                                            
# Apps registration
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)
snmpEngine.transportDispatcher.jobStarted(1) # this job would never finish
snmpEngine.transportDispatcher.runDispatcher()
                                            