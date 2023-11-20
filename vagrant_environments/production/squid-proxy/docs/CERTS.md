# Generate Squid SSL certs
ref : http://wiki.squid-cache.org/ConfigExamples/Intercept/SslBumpExplicit

- SSH into the squid proxy
```
$ openssl req -new -newkey rsa:2048 -sha256 -days 365 -nodes -x509 -extensions v3_ca -keyout myCA.pem  -out myCA.pem
```
