# run using vagrant user - no need for sudo
docker run -d \
-p 9000:9000 \
--name portainer \
-v /var/run/docker.sock:/var/run/docker.sock \
portainer/portainer \
-H unix:///var/run/docker.sock
