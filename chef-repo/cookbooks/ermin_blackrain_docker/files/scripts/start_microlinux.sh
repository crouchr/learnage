echo "Starting latest version of microlinux container..."
docker run -d \
--name microlinux \
-i -t \
registry:5000/microlinux:1.0.0

