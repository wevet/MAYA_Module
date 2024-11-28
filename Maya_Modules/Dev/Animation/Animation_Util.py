# -*- coding: utf-8 -*-

import sys
import os
import maya.cmds as cmds


class AnimationUtil:

    @staticmethod
    def all_import_reference():
        """
        すべてのリファレンスをインポート（マージ）
        """
        # すべてのリファレンスノードを取得
        references = cmds.ls(references=True)
        for ref in references:
            try:
                # 各リファレンスのファイルパスを取得
                filename = cmds.referenceQuery(ref, filename=True)

                # ファイルパスが無効な場合をスキップ
                if not filename or not cmds.file(filename, query=True, exists=True):
                    print(f"Skipped invalid or non-existent file: {filename}")
                    continue

                cmds.file(filename, importReference=True)
                print(f"Imported reference: {filename}")

            except RuntimeError as e:
                print(f"Error importing reference {ref}: {e}")
            except Exception as e:
                print(f"Unexpected error with reference '{ref}': {e}")
        print("All references processed.")


    @staticmethod
    def remove_namespace():
        """
        すべての名前空間を削除します（"UI" と "shared" を除く）。
        """
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True) or []  # 名前空間リストを取得
        namespaces = [ns for ns in namespaces if ns not in ["UI", "shared"]]  # "UI" と "shared" を除外

        for namespace in namespaces:
            try:
                # 名前空間内のノードをルートに移動
                cmds.namespace(force=True, moveNamespace=(namespace, ":"))
                # 名前空間を削除
                cmds.namespace(removeNamespace=namespace)
                print(f"Removed namespace: {namespace}")
            except RuntimeError as e:
                print(f"Error removing namespace {namespace}: {e}")


    @staticmethod
    def reload_current_scene_without_saving():
        """
        現在開いているシーンを保存せずに再読み込みする。
        """
        current_scene = cmds.file(query=True, sceneName=True)
        if not current_scene:
            print("There are currently no open scenes.")
            return

        try:
            cmds.file(current_scene, open=True, force=True)
            print(f"Reloaded the scene without saving it.: {current_scene}")
        except Exception as e:
            print(f"An error occurred while reloading the scene: {e}")


    @staticmethod
    def toggle_plugin_scanner(enable=True):
        if enable:
            if not cmds.pluginInfo('MayaScannerCB', query=True, loaded=True):
                try:
                    cmds.loadPlugin('MayaScannerCB')
                    print("Plugin MayaScannerCB has been enable.")
                except RuntimeError as e:
                    print(f"Failed to disable plugin MayaScannerCB : {e}")
        else:
            if cmds.pluginInfo('MayaScannerCB', query=True, loaded=True):
                try:
                    cmds.unloadPlugin('MayaScannerCB')
                    print("Plugin MayaScannerCB has been disabled.")
                except RuntimeError as e:
                    print(f"Failed to disable plugin MayaScannerCB : {e}")


    @staticmethod
    def find_rig_root_node(index=0):
        # Hide the 'rig' nodes
        root_nodes = cmds.ls("|rig*", type="transform")

        if root_nodes:
            for top_node in root_nodes:
                try:
                    cmds.setAttr(f"{top_node}.visibility", index)
                    print(f"Node '{top_node}' has been hidden.")
                except RuntimeError as e:
                    print(f"Error hiding node '{top_node}': {e}")
        else:
            print("Warning: No top-level nodes matching '|rig*' exist in the scene.")


    @staticmethod
    def remove_namespace_prefix(prefix):
        """
        Remove namespaces from root_node, connector, and their children for the given prefix.
        Args:
            prefix (str): The namespace prefix to remove (e.g., "LTN").

        Returns:
            dict: A dictionary with original names as keys and new names as values for restoring.
        """
        restore_data = {}

        # Define target nodes (root_node and connector)
        root_node = f"{prefix}:output"
        connector_node = f"{prefix}:connector"

        def recursive_rename(node):
            """
            Recursively process a node and its children to remove namespaces.
            Args:
                node (str): The node to process.
            """
            if not cmds.objExists(node):
                print(f"WARNING: Node '{node}' does not exist. Skipping.")
                return

            # Process children first (recursive step)
            children = cmds.listRelatives(node, children=True, fullPath=True) or []
            for child in children:
                recursive_rename(child)

            # Process the current node
            base_name = node.split(":")[-1]
            if not cmds.objExists(base_name):
                restore_data[node] = base_name
                cmds.rename(node, base_name)
            else:
                print(f"WARNING: Name conflict for node '{node}'. Skipping rename.")

        # Process the root and connector nodes
        recursive_rename(root_node)
        recursive_rename(connector_node)

        print("Namespaces removed. Restore data prepared.")
        return restore_data


    @staticmethod
    def restore_namespace(restore_data):
        """
        Restore namespaces for nodes using the provided restore_data dictionary.
        Args:
            restore_data (dict): A dictionary with new names as keys and original names as values.
        """
        for new_name, original_name in restore_data.items():
            if cmds.objExists(new_name):
                try:
                    cmds.rename(new_name, original_name)
                    print(f"Restored '{new_name}' to '{original_name}'.")
                except RuntimeError as e:
                    print(f"Failed to restore '{new_name}' to '{original_name}': {e}")
            else:
                print(f"WARNING: Node '{new_name}' no longer exists. Skipping restoration.")

        print("Namespaces restored successfully.")

