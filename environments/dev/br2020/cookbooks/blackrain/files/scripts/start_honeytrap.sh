echo "Starting latest version of honeytrap honeypot..."
docker run \
--name honeytrap \
-i -t \
registry:5000/honeytrap
