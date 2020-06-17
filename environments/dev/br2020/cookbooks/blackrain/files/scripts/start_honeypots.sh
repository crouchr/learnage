echo "Starting AMUN honeypot..."
docker run -i -t crouchr:amun -p 135:135 -p 139:139 -p 445:445 -p 62001:62001 -p 62002:62002 -p 62003:62003

echo "Starting Glastofp honeypot..."
docker run -i -t crouchr:glastopf -p 8888:80

# SSH into a running container
# docker exec -it glastopf ash
