FROM ubuntu:16.04

LABEL maintainer="Guang Yang <gyang274@gmail.com>"

RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        git \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        mlocate \
        pkg-config \
        python-dev \
        python-numpy \
        python-pip \
        software-properties-common \
        swig \
        zip \
        zlib1g-dev \
        libcurl3-dev \
        openjdk-8-jdk\
        openjdk-8-jre-headless \
        wget \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /
WORKDIR /

# Set up grpc
RUN pip install mock grpcio

# Set up bazel
ENV BAZELRC /root/.bazelrc

# Install the most recent bazel release
ENV BAZEL_VERSION 0.7.0

RUN mkdir /bazel && \
    cd /bazel && \
    curl -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

# Setup tensorflow_model_server
RUN echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list && \
    curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add - && \
    apt-get update && apt-get install tensorflow-model-server

# tf.contrib.util.make_tensor_proto in /app/rest/slim_unified_client_rest.py
RUN pip install tensorflow

# Set up uwsgi
# RUN curl http://uwsgi.it/install | bash -s default /usr/bin/uwsgi && \
#     rm -rf uwsgi_latest_from_installer && \
#     rm -rf uwsgi_latest_from_installer.tar.gz
RUN apt-get install -y \
        uwsgi-core \
        uwsgi-plugin-python \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the model servables directory contents into the container at /app
COPY ./tf_servables /app/tf_servables

# Copy the init script into the container at /app
COPY ./init.sh /app/init.sh

# Copy the rest api service script into the container at /app
COPY ./tensorflow_serving /app/tensorflow_serving
COPY ./slim_unified_client_rest.py /app/slim_unified_client_rest.py
COPY ./slim_unified_client_rest.ini /app/slim_unified_client_rest.ini

# Setup EXPOSE
EXPOSE 9090
EXPOSE 9000

EXPOSE 80

# Setup ENTRYPOINT
ENTRYPOINT ["/bin/bash", "/app/init.sh"]

