# This must be run as root
# This does not work - UI fires up but issue with tthe docker.sock
docker run -d \
-p 9000:9000 \
-v /var/run/docker.sock:/var/run/docker.sock \
portainer/portainer \
-H unix://var/run/docker.sock
