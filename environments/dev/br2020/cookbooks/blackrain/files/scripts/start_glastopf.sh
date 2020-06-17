echo "Starting Glastofp honeypot..."
docker run --name glastopf \
-i -t cicd:glastopf \
-p 8888:80
