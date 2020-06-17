# run using vagrant user - no need for sudo
docker run -d \
--name cadvisor \
-p 8080:8080 \
--volume /:/rootfs:ro \
--volume /var/run:/var/run:rw \
--volume /sys:/sys:ro \
--volume /var/lib/docker:/var/lib/docker:ro \
--restart on-failure:10 \
gcr.io/google-containers/cadvisor:v0.36.0
