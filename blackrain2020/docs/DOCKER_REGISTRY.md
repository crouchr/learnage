Storing BR2020 Docker images
============================
Docker Registry is a free means to store retrieve images

Unclear if Jfrog OSS supports docker images
Note : https://stackoverflow.com/questions/58049331/does-jfrog-artifactory-oss-provides-private-docker-registry

Hence go with Docker Registry...

info : https://docs.docker.com/registry/

$ docker run -d -p 5000:5000 --name registry registry:2

Tag your image so it points to your registry
$ docker image tag ubuntu localhost:5000/myfirstimage

Push the image to your registry
$ docker push localhost:5000/myfirstimage

Pull it back
$ docker pull localhost:5000/myfirstimage

Stop registry and remove all data
$ docker container stop registry && docker container rm -v registry

