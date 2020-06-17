echo "Starting Glastofp honeypot..."
docker run --name glastopf \
-i -t crouchr:glastopf \
-p 8888:80
