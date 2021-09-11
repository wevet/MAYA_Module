# MAYA_Module
MAYA Sample Sources
using IDE PyCharm


## noise_deformer.py
![deformer](Demo/NoiseDeformer.png)
```python

import maya.cmds as cmds
deformer_name = "NoiseDeformer"
plugin_settings = cmds.pluginInfo(deformer_name, q=True, settings=True)
if not plugin_settings[0]:
    cmds.loadPlugin(deformer_name + ".py")
cmds.polyPlane(w=50, h=50, sw=100, sh=100)
cmds.deformer(type=deformer_name)

```


