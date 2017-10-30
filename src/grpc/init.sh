#!/usr/bin/env bash
tensorflow_model_server \
    --model_name=slim_inception_resnet_v2 \
    --model_base_path=/app/tf_servables/slim/inception-resnet-v2 \
    --port=9000 &

tensorflow_model_server \
    --model_name=slim_inception_v4 \
    --model_base_path=/app/tf_servables/slim/inception-v4 \
    --port=9090 &

bin/bash

