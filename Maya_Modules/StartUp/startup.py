# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.utils
import os
import sys

# 確認メッセージ
print("✅ startup.py is being executed!")

# `sys.path` に `FH_Tools` を追加
fh_tools_path = "C:/Users/waltz/Documents/MAYA_Module/Maya_Modules/StartUp"
if fh_tools_path not in sys.path:
    sys.path.append(fh_tools_path)
    print(f"✅ {fh_tools_path} を sys.path に追加しました。")

# 各ツールのディレクトリを `sys.path` に追加
TOOL_DIRS = [
    os.path.join(fh_tools_path, "Animation"),
    os.path.join(fh_tools_path, "VertexColor"),
    os.path.join(fh_tools_path, "RampTexture"),
    os.path.join(fh_tools_path, "UV"),
    os.path.join(fh_tools_path, "T2M"),
]

for tool_dir in TOOL_DIRS:
    if tool_dir not in sys.path:
        sys.path.append(tool_dir)
        print(f"✅ {tool_dir} を sys.path に追加しました。")


# シェルフ作成関数
def create_shelf():
    shelf_name = "WV_Custom"

    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name)

    #cmds.shelfLayout(shelf_name, parent="ShelfLayout")
    cmds.setParent("ShelfLayout")
    cmds.shelfLayout(shelf_name)

    tools = [
        {
            "label": "Character ToolKit",
            "command": "import Animation.Animation_Exporter as AE\nimport importlib\nimportlib.reload(AE)\nmain_window = AE.show_main_window()",
            "icon": os.path.join(fh_tools_path, "Animation", "icon", "tool_icon.png"),
            "annotation": "Character Exporter"
        },
        {
            "label": "Vertex Color",
            "command": "import VertexColor.Custom_Vertex_Color as CVC\nimport importlib\nimportlib.reload(CVC)\nmain_window = CVC.show_main_window()",
            "icon": os.path.join(fh_tools_path, "VertexColor", "icon", "tool_icon.png"),
            "annotation": "Vertex Color"
        },
        {
            "label": "Ramp Texture",
            "command": "import RampTexture.Ramp_Texture_Creator as RTC\nimport importlib\nimportlib.reload(RTC)\nmain_window = RTC.show_main_window()",
            "icon": os.path.join(fh_tools_path, "RampTexture", "icon", "tool_icon.png"),
            "annotation": "Ramp Texture Create"
        },
        {
            "label": "UVEdge",
            "command": "import UV.UV_Edge_Exporter as EE\nimport importlib\nimportlib.reload(EE)\nmain_window = EE.show_main_window()",
            "icon": os.path.join(fh_tools_path, "UV", "icon", "tool_icon.png"),
            "annotation": "UV Edge Exporter"
        },
        {
            "label": "T2M",
            "command": "import T2M.T2M_ToolKit as T2M\nimport importlib\nimportlib.reload(T2M)\nmain_window = T2M.show_main_window()",
            "icon": os.path.join(fh_tools_path, "T2M", "icon", "tool_icon.png"),
            "annotation": "T2M"
        }
    ]

    # 各ツールをシェルフに追加
    for tool in tools:
        cmds.shelfButton(
            parent=shelf_name,
            annotation=tool["annotation"],
            label=tool["label"],
            command=tool["command"],
            image=tool["icon"].replace("\\", "/"),
            sourceType="python"
        )

maya.utils.executeDeferred("create_shelf()")
