Docker Registry
===============
See https://docs.docker.com/registry/
The Registry is a stateless, highly scalable server side application that stores and lets you distribute Docker images. The Registry is open-source
You should use the Registry if you want to:

    tightly control where your images are being stored
    fully own your images distribution pipeline
    integrate image storage and distribution tightly into your in-house development workflow

API is here : https://docs.docker.com/registry/spec/api/

Easy examples
-------------
To get a list of the images in the registry :
`curl http://192.168.1.109:5000/v2/_catalog`
```json
{"repositories":["gold-centos7","rev-proxy"]}
```

To get a list of tags for a given image `amun` :
`curl http://192.168.1.109:5000/v2/rev-proxy/tags/list`
```json
{

    "name": "rev-proxy",
    "tags": [
        "1.0.0"
    ]

}
```

Pushing an image to the registry
--------------------------------
```bash
$ docker push registry:5000/rev-proxy:1.0.0
```
OR (push as latest)
```bash
$ docker push registry:5000/rev-proxy
```

Pulling an image from the registry
----------------------------------
```bash
 docker pull registry:5000/rev-proxy:1.0.0
```
