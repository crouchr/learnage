# This is used during development so that don't need to keep running Chef
# Extend this to actually pull 'latest' when pipeline support semantic versioning
echo "Pulling latest containers..."
sudo docker pull registry:5000/amun:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/cowrie:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/glastopf:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/honeytrap:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/p0f2:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/netflow:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/microlinux:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/scantools:1.0.0
echo "-----------------------------------"
sudo docker pull registry:5000/dionaea:1.0.0

