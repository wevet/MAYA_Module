import maya.cmds as cmds


def get_uv_coordinates_from_selected_edges():
    selected_edges = cmds.ls(selection=True, flatten=True)
    if not selected_edges:
        print("No edges selected.")
        return

    uv_data = {}
    for edge in selected_edges:
        uv_coords = cmds.polyListComponentConversion(edge, toUV=True)
        uv_list = cmds.ls(uv_coords, flatten=True)

        if not uv_list or len(uv_list) < 2:
            print(f"No UVs found for edge {edge}")
            continue

        # UV座標を取得
        uv_positions = [cmds.polyEditUV(uv, query=True) for uv in uv_list]
        unique_uv_positions = list(dict.fromkeys([tuple(uv) for uv in uv_positions]))  # 重複排除

        # エッジに対応するUV座標を記録
        uv_data[edge] = unique_uv_positions
        print(f"Edge {edge}: UV Coordinates {unique_uv_positions}")

    return uv_data


get_uv_coordinates_from_selected_edges()
