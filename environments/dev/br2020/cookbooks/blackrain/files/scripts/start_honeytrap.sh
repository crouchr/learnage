echo "Starting latest version of Honeytrap honeypot..."
docker run -d \
--name honeytrap \
-i -t \
registry:5000/honeytrap:1.0.0

