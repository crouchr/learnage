echo "Starting latest version of Netflow container..."
docker run -d \
--name netflow \
-i -t \
registry:5000/netflow:1.0.0

