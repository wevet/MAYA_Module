# MAYA_Module
MAYA Modules

### Animation Retarget Module
Maya_Modules/Animation\
Use the install.mel by drad&drop.

### Animation Mirror Module
Maya_Modules/Animation/Mirror\
Use the install.mel by drad&drop.

### Animation Exporter Batch
Maya_Modules/Misc/Batch_Exporter

### FiceRig Setup Tool
Maya_Modules/Modules/FaceRigger\
Use the install.mel by drad&drop.

### noise_deformer.py
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

### auto_rig.py
![auto_rig](Demo/Rigging_Tool.png)
```python

import auto_rig
import importlib
importlib.reload(auto_rig)
auto_rig.create_main_window()

```

