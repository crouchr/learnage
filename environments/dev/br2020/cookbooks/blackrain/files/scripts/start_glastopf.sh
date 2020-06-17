echo "Starting latest version of Glastofp honeypot..."
docker run \
--name glastopf \
-i -t \
-p 8888:80 \
registry:5000/glastopf
