#!/usr/bin/python

SPAMHOLE_IP  = "192.168.1.61"
GLASTO_IP    = "192.168.1.62"
HONEYD_IP    = "192.168.1.63"
KIPPO_IP     = "192.168.1.64"
NEPENTHES_IP = "192.168.1.65"
AMUN_IP      = "192.168.1.66"
DIONAEA_IP   = "192.168.1.68"

def getHpotIP(ip) :
    
#    if ip == SPAMHOLE_IP :
#        return "SPAMHOLE","6"
#    elif ip == GLASTO_IP :
#        return "GLASTOPF","4"
#    elif ip == HONEYD_IP :
#        return "HONEYD","1"
#    elif ip == KIPPO_IP :
#        return "KIPPO","2"
#    elif ip == NEPENTHES_IP :
#        return "NEPENTHES","5"
#    elif ip == AMUN_IP :
#        return "AMUN","3"
#    elif ip == DIONAEA_IP :
#        return "DIONAEA","7"
#    else:
#        return "NETFLOW","0"

    if ip == SPAMHOLE_IP :
        return "SPAMHOLE"
    elif ip == GLASTO_IP :
        return "GLASTOPF"
    elif ip == HONEYD_IP :
        return "HONEYD"
    elif ip == KIPPO_IP :
        return "KIPPO"
    elif ip == NEPENTHES_IP :
        return "NEPENTHES"
    elif ip == AMUN_IP :
        return "AMUN"
    elif ip == DIONAEA_IP :
        return "DIONAEA"
    else:
        return "NETWORK"
                