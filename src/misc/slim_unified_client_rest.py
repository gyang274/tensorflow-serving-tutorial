
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# python2
from urllib2 import urlopen
# python3
# from urllib.request import urlopen

import json
from multiprocessing.pool import ThreadPool

# Add tf_serving into PATH
import sys

sys.path.append(
  'slim_unified_client.runfiles/tf_serving'
)

import numpy as np
import tensorflow as tf

# This is a placeholder for a Google-internal import.
from grpc.beta import implementations
from google.protobuf import json_format, text_format
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2


def fetch_url(url):
  try:
    response = urlopen(url)
    return url, response.read(), None
  except Exception as e:
    return url, None, e


def application(environ, start_response):

  request_method = environ['REQUEST_METHOD'].upper()

  response_body = dict()

  if request_method == 'GET':

    response_body.update(
      {
        'service': 'slim-unified-client-rest',
        'message': 'No support on GET, please use POST.',
        'usage': {
          'endpoint': 'POST /',
          'payload': {
            'format': 'application/json',
            'body': {
              'host': 'optional, host for tensorflow serving model server, default "127.0.0.1"',
              'port': 'optional, port for tensorflow serving model server, default "9000"',
              'model_name': 'optional, tensorflow serving model name, default "slim_inception_resnet_v2"' +
                ', all available models: slim_inception_resnet_v2 at port 9000, and slim_inception_v4 at port 9090',
              'image_urls': 'required, image urls in list'
            }
          },
          'returns': {
            'classes': 'top 5 classes of each input image_urls, in shape `n x 5`',
            'scores': 'top 5 classes scores (probabilities) of each input image_urls, in shape `n x 5`',
            'prelogits': 'a numeric vector of 1536 of each input image_urls, in shape n x 1536' +
              ', this vector can be viewed as features of each input image_urls for transfer learning or etc.'
          }
        }
      }
    )

  if request_method == 'POST':

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:

      request_body_size = int(environ.get('CONTENT_LENGTH', 0))

      # the request body is expected to be json
      request_body = json.loads(
        environ['wsgi.input'].read(request_body_size)
      )

      # connect to tfs-slim
      host = request_body.get('host', '127.0.0.1')
      port = request_body.get('port', '9000')
      model_name = request_body.get('model_name', 'slim_inception_resnet_v2')
      image_urls = request_body.get('image_urls', [])

      print('host, port:', host + ':' + port)
      print('model_name:', model_name)
      print('image_urls:', image_urls)

      assert len(image_urls) > 0, "payload should contains a image_urls as a list of image urls."

      # fetch image urls into bytes, in parallel
      image_fetch_results = ThreadPool(128).map(fetch_url, image_urls)
      image_bytes = [
        result[1] for result in image_fetch_results if result[2] is None
      ]
      # for result in image_fetch_results:
      #   if result[2] is not None:
      #     print('Error in Fetch URL: {}'.format(result[2]))

      # establish a stub with tensorflow serving service
      channel = implementations.insecure_channel(host, int(port))
      stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
      request = predict_pb2.PredictRequest()
      request.model_spec.name = model_name
      request.model_spec.signature_name = 'predict_images'
      request.inputs['images'].CopyFrom(
        tf.contrib.util.make_tensor_proto(
          image_bytes, shape=[len(image_bytes)]
        )
      )
      result = stub.Predict(request, 60.0)  # 60 secs timeout

      # post-processing the result protobuf into json

      # stringVal have to go the hard way
      result_classes_tensorproto = text_format.MessageToString(
        result.outputs['classes']
      )
      result_classes_tensorproto = result_classes_tensorproto.strip().split('\n')
      result_classes_value = [
        x.split(": ")[1][1:-1] for x in result_classes_tensorproto if 'string_val' in x
      ]  # use ...[1:-1] to remove double qoute around synset names
      # assume in classes are in 2 dims
      result_classes_shape = [
        int(x.split(": ")[1]) for x in result_classes_tensorproto if 'size' in x
      ]
      assert len(result_classes_shape) == 2
      result_classes = [
        result_classes_value[i:i+result_classes_shape[1]] for i in range(0, len(result_classes_value), result_classes_shape[1])
      ]

      # floatVal is able to go the easy way
      result_scores_tensorproto = json_format.MessageToDict(
        result.outputs['scores']
      )
      result_scores_value = result_scores_tensorproto['floatVal']
      result_scores_shape = [
        int(x['size']) for x in result_scores_tensorproto['tensorShape']['dim']
      ]
      result_scores = np.reshape(
        result_scores_value, result_scores_shape
      ).tolist()

      # prelogits as image feature for further development
      result_prelogits_tensorproto = json_format.MessageToDict(
        result.outputs['prelogits']
      )
      result_prelogits_value = result_prelogits_tensorproto['floatVal']
      result_prelogits_shape = [
        int(x['size']) for x in result_prelogits_tensorproto['tensorShape']['dim']
      ]
      result_prelogits = np.reshape(
        result_prelogits_value, result_prelogits_shape
      ).tolist()

      response_body.update(
        {
          'data': {
            'image_urls': [
              x for x, y in zip(image_urls, image_fetch_results) if y[2] is None
            ],
            'classes': result_classes,
            'scores': result_scores,
            'prelogits': result_prelogits
          },
          'message': {
            'image_urls_fetch_failed': [
              x for x, y in zip(image_urls, image_fetch_results) if y[2] is not None
            ]
          }
        }
      )

    except Exception as e:

      response_body.update(
        {
          'error': {
            'type': str(type(e)),
            'args': str(e.args)
          }
        }
      )

  # convert response body into str
  response_body = json.dumps(response_body)

  # construct start_response with status, and response headers
  status = '200 OK'

  response_headers = [
    ('Content-Type', 'application/json'),
    ('Content-Length', str(len(response_body)))
  ]

  start_response(status, response_headers)

  # return: wrap response body into a list
  return [response_body]

