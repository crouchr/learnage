echo "Starting latest version of Cowrie honeypot..."
docker run -d \
--name cowrie \
-i -t \
registry:5000/cowrie:1.0.0


