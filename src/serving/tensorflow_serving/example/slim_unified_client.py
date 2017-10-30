# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

#!/usr/bin/env python2.7

"""Send image_urls to tensorflow_model_server loaded with slim model.
"""

from __future__ import print_function

import urllib2

from multiprocessing.pool import ThreadPool

# This is a placeholder for a Google-internal import.

from grpc.beta import implementations
import tensorflow as tf

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2


tf.app.flags.DEFINE_string(
  'server', 'localhost:9000', 'PredictionService host:port'
)
tf.app.flags.DEFINE_string(
  'model_name', '', 'Tensorflow Serving Model Name'
)
tf.app.flags.DEFINE_string(
  'image_urls', '', 'URL to image in JPEG format, comma separated URLs.'
)
FLAGS = tf.app.flags.FLAGS


def fetch_url(url):
    try:
        response = urllib2.urlopen(url)
        return url, response.read(), None
    except Exception as e:
        return url, None, e

def main(_):
  host, port = FLAGS.server.split(':')
  channel = implementations.insecure_channel(host, int(port))
  stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
  # Send request
  # See prediction_service.proto for gRPC request/response details.
  image_urls = FLAGS.image_urls.split(',')
  image_fetch_results = ThreadPool(128).map(fetch_url, image_urls)
  image_bytes = [
    result[1] for result in image_fetch_results if result[2] is None
  ]
  for result in image_fetch_results:
    if result[2] is not None:
      print('Error in Fetch URL: {}'.format(result[2]))
  request = predict_pb2.PredictRequest()
  request.model_spec.name = FLAGS.model_name
  request.model_spec.signature_name = 'predict_images'
  request.inputs['images'].CopyFrom(
    tf.contrib.util.make_tensor_proto(
      image_bytes, shape=[len(image_bytes)]
    )
  )
  result = stub.Predict(request, 60.0)  # 60 secs timeout
  print(result)


if __name__ == '__main__':
  tf.app.run()

