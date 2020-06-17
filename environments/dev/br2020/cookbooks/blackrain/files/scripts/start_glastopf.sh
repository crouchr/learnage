echo "Starting latest version of Glastofp honeypot..."
docker run -d \
--name glastopf \
-i -t \
-p 8888:80 \
registry:5000/glastopf:1.0.0
