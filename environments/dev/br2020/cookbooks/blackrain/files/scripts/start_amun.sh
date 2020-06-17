echo "Starting AMUN honeypot..."
docker run --name amun \
-i -t crouchr:amun \
-p 135:135 -p 139:139 -p 445:445 -p 62001:62001 -p 62002:62002 -p 62003:62003

# SSH into a running container - no need for SSHd on the container at all
# docker exec -it glastopf ash
