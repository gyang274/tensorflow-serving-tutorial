# tensorflow-serving-tutorial

A step by step guide on how to use tensorflow serving to serve a tensorflow model. These steps are illustrated with google's slim models, e.g., inception-v4, inception-resnet-v2, via tensorflow serving. And the result served models with gRPC and REST services are wrapped into a docker image for further development. Read the step by step guide at this [`gh-pages`](https://gyang274.github.io/tensorflow-serving-tutorial/)

## Quick Start

### Docker Run Image

```
$ docker run -p 80:80 -d gyang274/yg-tfs-slim:rest
```

### REST API

- check usage: `GET /`

```
# endpoint: GET /
#  - returns: usage

$ curl -X GET 127.0.0.1:80
```

- main endpoint: `POST /`

```
# endpoint: POST /
#  - payload:
#    - host: optional, host for tensorflow serving model server, default "127.0.0.1",
#    - port: optional, port for tensorflow serving model server, default "9000",
#    - model_name: optional, tensorflow serving model name, default "slim_inception_resnet_v2",
#        all available models: slim_inception_resnet_v2 at port 9000, and slim_inception_v4 at port 9090',
#    - image_urls: required, image urls in list
#  - returns:
#    - classes: top 5 classes of each input image_urls, in shape `n x 5`
#    - scores: top 5 classes scores (probabilities) of each input image_urls, in shape `n x 5`,
#    - prelogits: a numeric vector of 1536 of each input image_urls, in shape `n x 1536`, 
#        this vector can be viewed as features of each input image_urls for transfer learning or etc.

$ curl -X POST 127.0.0.1:80 -d '{
    "image_urls": [
        "https://upload.wikimedia.org/wikipedia/commons/d/d9/First_Student_IC_school_bus_202076.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Labrador_Retriever_portrait.jpg/1200px-Labrador_Retriever_portrait.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/fd/Qantas_a380_vh-oqa_takeoff_heathrow_arp.jpg"
    ]
}'
```

- note

```
# note: the rest api expected a valid json as payload, so it might need to remove line breaks and make the post data in 
# one line, since the terminal might interpret line breaks as `\n` and add it into payload which causes invalid json.

$ curl -X POST 127.0.0.1:80 -d '{"image_urls": ["https://upload.wikimedia.org/wikipedia/commons/d/d9/First_Student_IC_school_bus_202076.jpg","https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Labrador_Retriever_portrait.jpg/1200px-Labrador_Retriever_portrait.jpg","https://upload.wikimedia.org/wikipedia/commons/f/fd/Qantas_a380_vh-oqa_takeoff_heathrow_arp.jpg"]}'
```

### Test the REST API via Python

```
import requests

response = requests.post(
  url="http://127.0.0.1:80",
  json={
    "image_urls": [
      "https://upload.wikimedia.org/wikipedia/commons/d/d9/First_Student_IC_school_bus_202076.jpg",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Labrador_Retriever_portrait.jpg/1200px-Labrador_Retriever_portrait.jpg",
      "https://upload.wikimedia.org/wikipedia/commons/f/fd/Qantas_a380_vh-oqa_takeoff_heathrow_arp.jpg"
    ]
  }
)

print(response.json())
```

## Step by Step Guide

This [`gh-pages`](https://gyang274.github.io/tensorflow-serving-tutorial/) includes a step by step on how to make these docker images from the begining. 

## GitHub Repository

This [github repository](https://github.com/gyang274/tensorflow-serving-tutorial) includes all source codes.

