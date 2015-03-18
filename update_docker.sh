echo "Building new Docker image."
sudo docker build -t chenclee/sandbox ./sandbox/
echo "Retrieving installed Docker images."
sudo docker images
