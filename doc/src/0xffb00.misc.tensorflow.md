## Tensorflow

### Restore slim checkpoint and View graphdef

```
- ../misc/restore_checkpoint_and_view_graphdef.ipynb
...
import os
import sys

import numpy as np
import tensorflow as tf

slim = tf.contrib.slim

# add slim models into path and load slim models
sys.path.append(
    '../serving/tf_models/research/slim/'
)

from nets import inception

from IPython.display import clear_output, Image, display, HTML

# creating TensorFlow session and loading the model
ckpt = '../serving/tf_checkpoints/slim/inception-resnet-v2/inception_resnet_v2_2016_08_30.ckpt'

graph = tf.Graph()
sess = tf.InteractiveSession(graph=graph)

# define graph from ckpt
images = tf.placeholder(
    tf.float32, shape = [32, 299, 299, 3], name="images"
)

with slim.arg_scope(
    inception.inception_resnet_v2_arg_scope()
):
    # inception resnet models
    logits, _ = inception.inception_resnet_v2(
        images, num_classes=1001, is_training=False
    )

init_fn = slim.assign_from_checkpoint_fn(
    ckpt, slim.get_model_variables('InceptionResnetV2')
)
    
init_fn(sess)

# Helper functions for TF Graph visualization

def strip_consts(graph_def, max_const_size=32):
    """Strip large constant values from graph_def."""
    strip_def = tf.GraphDef()
    for n0 in graph_def.node:
        n = strip_def.node.add() 
        n.MergeFrom(n0)
        if n.op == 'Const':
            tensor = n.attr['value'].tensor
            size = len(tensor.tensor_content)
            if size > max_const_size:
                tensor.tensor_content = tf.compat.as_bytes("<stripped %d bytes>"%size)
    return strip_def
  
def rename_nodes(graph_def, rename_func):
    res_def = tf.GraphDef()
    for n0 in graph_def.node:
        n = res_def.node.add() 
        n.MergeFrom(n0)
        n.name = rename_func(n.name)
        for i, s in enumerate(n.input):
            n.input[i] = rename_func(s) if s[0]!='^' else '^'+rename_func(s[1:])
    return res_def
  
def show_graph(graph_def, max_const_size=32):
    """Visualize TensorFlow graph."""
    if hasattr(graph_def, 'as_graph_def'):
        graph_def = graph_def.as_graph_def()
    strip_def = strip_consts(graph_def, max_const_size=max_const_size)
    code = """
        <script>
          function load() {{
            document.getElementById("{id}").pbtxt = {data};
          }}
        </script>
        <link rel="import" href="https://tensorboard.appspot.com/tf-graph-basic.build.html" onload=load()>
        <div style="height:600px">
          <tf-graph-basic id="{id}"></tf-graph-basic>
        </div>
    """.format(data=repr(str(strip_def)), id='graph'+str(np.random.rand()))
  
    iframe = """
        <iframe seamless style="width:800px;height:620px;border:0" srcdoc="{}"></iframe>
    """.format(code.replace('"', '&quot;'))
    display(HTML(iframe))
    
show_graph(graph_def=graph)
...
```