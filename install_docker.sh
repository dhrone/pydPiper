echo 'Installing Docker from the convenience script\n'
curl -sSL https://get.docker.com | sh

echo 'Now removing the engine so we can downgrade to one that currently works on Raspberry Pi\n' 
sudo apt-get purge -y docker-ce
sudo apt-get autoremove -y 
sudo rm -rf /var/lib/docker # This deletes all images, containers, and volumes

echo 'Reinstalling an older version\n'
sudo apt-get install -y --force-yes docker-ce=17.10.0~ce-0~raspbian

echo 'Enabling docker\n'
sudo usermod -aG docker volumio
sudo systemctl enable docker
sudo systemctl start docker
sudo docker pull dhrone/pydpiper:v0.31-alpha

echo 'Testing docker\n'
sudo docker run armhf/hello-world
