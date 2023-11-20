# Generate Squid SSL certs
ref : https://elatov.github.io/2019/01/using-squid-to-proxy-ssl-sites/

- SSH into the squid proxy
```
$ openssl req -new -newkey rsa:2048 -sha256 -days 365 -nodes -x509 -extensions v3_ca -keyout squid-ca-key.pem -out squid-ca-cert.pem
$ cat squid-ca-cert.pem squid-ca-key.pem >> squid-ca-cert-key.pem
```
