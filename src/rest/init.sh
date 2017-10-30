#!/usr/bin/env bash
tensorflow_model_server \
    --model_name=slim_inception_resnet_v2 \
    --model_base_path=/app/tf_servables/slim/inception-resnet-v2 \
    --port=9000 &

tensorflow_model_server \
    --model_name=slim_inception_v4 \
    --model_base_path=/app/tf_servables/slim/inception-v4 \
    --port=9090 &

mkdir /run/uwsgi

chown www-data:www-data /run/uwsgi

chmod 0666 /run/uwsgi

uwsgi --http-socket :80 --ini /app/slim_unified_client_rest.ini &

bin/bash

