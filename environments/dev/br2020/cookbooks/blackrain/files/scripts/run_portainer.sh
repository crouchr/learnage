# This can be run as vagrant
docker run -d \
-p 9000:9000 \
-name portainer \
-v /var/run/docker.sock:/var/run/docker.sock \
portainer/portainer \
-H unix:///var/run/docker.sock
