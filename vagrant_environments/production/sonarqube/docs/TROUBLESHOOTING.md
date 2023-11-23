

# Smoke check PostgresSQL
```
netstat -tulpn | grep 5432
```

# SonarQube service log
tail -f /opt/sonarqube/logs/sonar.log

# Web Server logs
tail -f /opt/sonarqube/logs/web.log

# ElasticSearch logs
tail -f /opt/sonarqube/logs/es.log

# Compute Engine logs
tail -f /opt/sonarqube/logs/ce.log

# SonarQube Initial Login Information
```
    URL: http://sonar.ermin.lan
    User: admin
    Password: admin
```