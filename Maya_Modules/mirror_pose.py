"""
説明
    コントローラを左右にミラーリングするツール
    またはポーズを反転させるツール

インストール方法
    1. mirror_pose.pyをMayaのscriptsフォルダに配置します。
    2. Pythonスクリプトエディタで、次のコードをコピーします。
    from mirror_pose import Mirror_Pose_Window_Manager
    mirror_pose.show_dialog()

使用方法
1. "mirror axis" ドロップダウンメニューで、ミラー軸の方向を選択します。

2. "direction "ドロップダウンメニューで、ミラーリングしたい方向を選択します。
    デフォルトでは、次のように動作します。
    -大文字のLとR
    -小文字のLとR
    -Lf と Rt
    命名規則がデフォルトの場合は、手順4へ進んでください。

3. 左側の命名規則を記入してください。
   左側の命名規則を "left naming convention "テキストボックスに、右側の命名規則を "right naming convention "テキストボックスに記入してください。
   右側の命名規則を "right naming convention "テキストボックスに記入してください。

4. ミラー "ボタンをクリックします。

"""


import sys
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.OpenMaya as om


class OperationType(object):
    left_to_right = "Left to Right"
    right_to_left = "Right to Left"
    flip = "Flip"
    flip_to_frame = "Flip to Frame"
    mirror_middle = "Mirror Middle"
    selected = "Selected"
    not_selected = "Not Selected"


def maya_main_menu():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class Mirror_Pose_Window_Manager(QtWidgets.QDialog):

    dialog_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = Mirror_Pose_Window_Manager()
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()

    def __init__(self, parent=maya_main_menu()):
        super(Mirror_Pose_Window_Manager, self).__init__(parent)
        self.setWindowTitle("Mirror Pose - 1.0.1")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowMaximizeButtonHint)
        self.geometry = None
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.mirror_axis_cb = QtWidgets.QComboBox()
        self.mirror_axis_cb.addItems(["X", "Y", "Z"])
        self.mirror_axis_cb.setToolTip("Mirror axis direction")
        self.operation_cb = QtWidgets.QComboBox()
        self.operation_cb.addItems(
            [
                OperationType.left_to_right,
                OperationType.right_to_left,
                OperationType.flip,
                OperationType.flip_to_frame,
                OperationType.mirror_middle,
                OperationType.selected,
                OperationType.not_selected,
            ]
        )

        self.operation_cb.setToolTip(
            "Mirror operation:\n\n"
            "Left to Right: Set right controllers to same values as the left\n"
            "Right to Left: Set left controllers to same values as the right\n"
            "Flip: Flips the entire pose\n"
            "Flip to Frame: Flips the entire pose to specified frame\n"
            "Mirror Middle: Flips the middle controllers\n"
            "Selected: Mirrors the selected controllers to opposite side\n"
            "Not Selected: Flips all controllers that is not selected\n"
        )

        self.mirror_frame_dsb = QtWidgets.QDoubleSpinBox()
        self.mirror_frame_dsb.setRange(-1000000, 1000000)
        self.mirror_frame_dsb.setDecimals(1)
        self.mirror_frame_dsb.setValue(self.get_min_time())
        self.mirror_frame_dsb.setSingleStep(1)
        self.mirror_frame_dsb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.mirror_frame_dsb.setVisible(False)

        self.left_to_right_rb = QtWidgets.QRadioButton("Left To Right")
        self.left_to_right_rb.setChecked(True)
        self.right_to_left_rb = QtWidgets.QRadioButton("Right To Left")
        self.flip_rb = QtWidgets.QRadioButton("Flip")
        self.left_to_right_rb.setVisible(False)
        self.right_to_left_rb.setVisible(False)
        self.flip_rb.setVisible(False)

        self.mirror_options_seperator = QtWidgets.QFrame()
        self.mirror_options_seperator.setFrameShape(QtWidgets.QFrame.HLine)
        self.mirror_options_seperator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.left_ctrl_name_le = QtWidgets.QLineEdit()
        self.left_ctrl_name_le.setToolTip("Enter custom naming convention for left controllers.\n" "By default works with 'L', 'l' and 'Lf'")
        self.right_ctrl_name_le = QtWidgets.QLineEdit()
        self.right_ctrl_name_le.setToolTip("Enter custom naming convention for right controllers.\n" "By default works with 'R', 'r' and 'Rt'")
        self.mirror_btn = QtWidgets.QPushButton("Mirror")
        self.mirror_btn.setToolTip("Mirror controllers based on settings above")
        self.link_seperator = QtWidgets.QFrame()
        self.link_seperator.setFrameShape(QtWidgets.QFrame.HLine)
        self.link_seperator.setFrameShadow(QtWidgets.QFrame.Sunken)

    def create_layout(self):
        side_to_opp_rb_layout = QtWidgets.QHBoxLayout()
        side_to_opp_rb_layout.addWidget(self.left_to_right_rb)
        side_to_opp_rb_layout.addWidget(self.right_to_left_rb)
        side_to_opp_rb_layout.addWidget(self.flip_rb)

        mirror_options_layout = QtWidgets.QFormLayout()
        mirror_options_layout.addRow("Mirror Axis:", self.mirror_axis_cb)
        mirror_options_layout.addRow("Operation:", self.operation_cb)
        mirror_options_layout.addRow("", self.mirror_frame_dsb)
        mirror_options_layout.addRow("", side_to_opp_rb_layout)

        naming_convention_layout = QtWidgets.QFormLayout()
        naming_convention_layout.addRow("Left Naming Convention:", self.left_ctrl_name_le)
        naming_convention_layout.addRow("Right Naming Convention:", self.right_ctrl_name_le)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.mirror_btn)
        link_layout = QtWidgets.QHBoxLayout()
        link_layout.addWidget(self.link_btn)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addLayout(mirror_options_layout)
        main_layout.addWidget(self.mirror_options_seperator)
        main_layout.addLayout(naming_convention_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.link_seperator)
        main_layout.addLayout(link_layout)
        main_layout.addStretch()

    def create_connections(self):
        self.operation_cb.currentTextChanged.connect(self.on_operation_change)
        self.mirror_btn.clicked.connect(self.mirror_control)
        self.link_btn.clicked.connect(self.open_url)

    def get_mirror_axis(self):
        """
        Returns:
            Returns the current text in the Mirror Axis Combo Box
        """
        return self.mirror_axis_cb.currentText()

    def get_operation(self):
        """
        Returns:
            Returns the current text in the Operation Combo Box
        """
        return self.operation_cb.currentText()

    def get_left_name(self):
        """
        Returns:
            Returns the userdefined naming convention for the left controller
        """
        return self.left_ctrl_name_le.text()

    def get_right_name(self):
        """
        Returns:
            Returns the userdefined naming convention for the right controller
        """
        return self.right_ctrl_name_le.text()

    def get_vectors_dominating_axis(self, vector):
        """
        Description:
            Getting what axis a vector is pointing the most to

        Args:
            vector: is a xyz list of 3 float values

        Returns:
            A string containing an axis. The axis can also be negative

        """
        # Making positive numbers
        denominator = 0
        for value in vector:
            # Making values positive,
            # so the denominator will be all values added togther
            value = abs(value)
            denominator += value
        percentage_strengt = []
        for value in vector:
            # Making value positive
            # in order to to get a strengt relative to the other axis
            value = abs(value)
            strengt = value / denominator
            percentage_strengt.append(strengt)
        # Finding the axis with the highest percentage.
        # Since the percentage_strengt is a xyz list.
        # We can use the index to find xyz.
        index = percentage_strengt.index(max(percentage_strengt))
        if index == 0:
            dominating_axis = "-X" if vector[0] < 0 else "X"
        elif index == 1:
            dominating_axis = "-Y" if vector[1] < 0 else "Y"
        elif index == 2:
            dominating_axis = "-Z" if vector[2] < 0 else "Z"
        else:
            dominating_axis = "-X" if vector[0] < 0 else "X"
        return dominating_axis

    def get_min_time(self):
        return cmds.playbackOptions(minTime=True, query=True)

    def get_max_time(self):
        return cmds.playbackOptions(maxTime=True, query=True)

    def get_flip_frame(self):
        """
        Returns:
            Returns the userdefined value in frame double spin box
        """
        return self.mirror_frame_dsb.value()

    def get_vector_data(self, ctrl_list):
        """
        Description:
            Finds the vector of all controllers and storing it in a dictionary

        Args:
            ctrl_list: A list of all controllers

        Returns:
            Returns a dictionay with controllers as keys and its different
            axis vectors as its value
        """
        vector_dict = {}
        cur_pos = {}
        # Storing the current position of the ctrl,
        # to get vector data in neutral position
        for ctrl in ctrl_list:
            cur_pos[ctrl] = self.get_attribute_data([ctrl])
            self.rotate_ctrl_to_zero(ctrl)
        for ctrl in ctrl_list:
            # getting controller vector in neutral position
            vector_dict[ctrl] = {}
            world_mat = cmds.xform(ctrl, matrix=True, worldSpace=True, query=True)
            # Rounding the values in the world matrix
            for i, value in enumerate(world_mat):
                rounded_value = round(value, 3)
                world_mat[i] = rounded_value
            vector_dict[ctrl]["x_axis"] = world_mat[0:3]
            vector_dict[ctrl]["y_axis"] = world_mat[4:7]
            vector_dict[ctrl]["z_axis"] = world_mat[8:11]
        # Setting ctrl back to its position
        for ctrl in ctrl_list:
            self.rotate_ctrl_to_data(ctrl, cur_pos[ctrl])
        return vector_dict

    def get_attribute_data(self, ctrl_list):
        """
        Description:
            Gets the data on the keyable attributes visible in the channelbox
            of all controllers

        Args:
            ctrl_list: A list of controllers

        Returns:
            Returns a dictionay with controllers as keys and its keyable
            attributes visible in the channelbox as its values
        """
        data = {}
        for ctrl in ctrl_list:
            # Getting data from controller and putting it in a dictionary
            data[ctrl] = {}
            # Checking if there exist attributes
            attributes = cmds.listAttr(ctrl, keyable=True, unlocked=True)
            if attributes:
                for attr in attributes:
                    # Seeing if attribute has incoming connection,
                    # and there cannot be modified
                    source_con = cmds.listConnections(
                        "{}.{}".format(ctrl, attr),
                        source=True,
                        destination=False,
                    )
                    # Checking if source connenction is a key
                    key_source = cmds.listConnections(
                        "{}.{}".format(ctrl, attr),
                        source=True,
                        type="animCurve",
                    )
                    if not source_con:
                        # Getting the value on the controller
                        # and storing it in data dict
                        value = cmds.getAttr("{}.{}".format(ctrl, attr))
                        # Only store data if int or float type
                        if type(value) == int or type(value) == float:
                            data[ctrl][attr] = value
                    elif key_source:
                        # Getting the value on the controller
                        # and storing it in data dict
                        value = cmds.getAttr("{}.{}".format(ctrl, attr))
                        # Only store data if int or float type
                        if type(value) == int or type(value) == float:
                            data[ctrl][attr] = value
        return data

    def get_selected_controls(self, ctrl_list, left_ctrl_list, right_ctrl_list, middle_ctrl_list):
        """
        Description:
            Gets what controllers are selected in the viewport

        Args:
            ctrl_list: A list of all controllers
            left_ctrl_list: A list of all left controllers
            right_ctrl_list: A list of all right controllers
            middle_ctrl_list: A list of all middle controllers

        Returns:
            Returns a nested list with the selected controllers
        """
        sel_controls = cmds.ls(selection=True)
        left_sel_controls = []
        right_sel_controls = []
        middle_sel_controls = []
        for sel_ctrl in sel_controls:
            if sel_ctrl in ctrl_list:
                if sel_ctrl in middle_ctrl_list:
                    middle_sel_controls.append(sel_ctrl)
                elif sel_ctrl in left_ctrl_list:
                    left_sel_controls.append(sel_ctrl)
                elif sel_ctrl in right_ctrl_list:
                    right_sel_controls.append(sel_ctrl)
        return [left_sel_controls, right_sel_controls, middle_sel_controls]

    def get_mirror_axis_dominent_vector(self, mirror_axis, x_dominating, y_dominating, z_dominating):
        """
        Args:
            mirror_axis: A string with the mirror axis
            x_dominating: String with what world axis the x axis is pointing to
            y_dominating: String with what world axis the y axis is pointing to
            z_dominating: String with what world axis the z axis is pointing to

        Returns:
            Returns what xyz axis pointing in the mirror axis
        """
        # Finding what axis is pointing the most to the mirror axis
        if (mirror_axis == x_dominating
            or "-{}".format(mirror_axis) == x_dominating
        ):
            mirror_attr = "X"
        elif (
            mirror_axis == y_dominating
            or "-{}".format(mirror_axis) == y_dominating
        ):
            mirror_attr = "Y"
        elif (
            mirror_axis == z_dominating
            or "-{}".format(mirror_axis) == z_dominating
        ):
            mirror_attr = "Z"
        # 実際はこのelseは必要ない
        # ただし、2つの軸が等しい間隔で配置されていると問題が発生することがある
        else:
            mirror_attr = mirror_axis
        return mirror_attr

    def set_time(self, time):
        cmds.currentTime(time)

    def remove_items_from_list(self, ctrl_list, items):
        """
        Args:
            ctrl_list: A list of controllers
            items: A list of controllers

        Returns:
            Returns a list with the items in items list removed from ctrl_list
        """
        for item in items:
            ctrl_list.remove(item)
        return ctrl_list

    def on_operation_change(self):
        """
        Description:
            Sets various widgets to visible and not visible depending on what
            the user has selected in the operation combo box
        """
        text = self.get_operation()
        if text == "Flip to Frame":
            self.mirror_frame_dsb.setVisible(True)
        else:
            self.mirror_frame_dsb.setVisible(False)
        if text == "Not Selected":
            self.left_to_right_rb.setVisible(True)
            self.right_to_left_rb.setVisible(True)
            self.flip_rb.setVisible(True)
        else:
            self.left_to_right_rb.setVisible(False)
            self.right_to_left_rb.setVisible(False)
            self.flip_rb.setVisible(False)

    def rotate_ctrl_to_zero(self, ctrl):
        """
        Description:
            Sets rotation of controller to zero
        Args:
            ctrl: A controller
            Auto key: Boolean to disable auto key
        """
        for attr in ["X", "Y", "Z"]:
            if cmds.listAttr("{}.rotate{}".format(ctrl, attr), keyable=True, unlocked=True):
                auto_key = cmds.autoKeyframe(state=True, query=True)
                if auto_key:
                    cmds.autoKeyframe(state=False)
                cmds.setAttr("{}.rotate{}".format(ctrl, attr), 0)
                if auto_key:
                    cmds.autoKeyframe(state=True)

    def rotate_ctrl_to_data(self, ctrl, data):
        """
        Description:
            Sets rotation of controller to what is specified in data
        Args:
            ctrl: A controller
            data: A dictionary containing controllers with rotation as values
            Auto key: Boolean to disable auto key
        """
        for attr in ["X", "Y", "Z"]:
            if "rotate{}".format(attr) in data[ctrl].keys():
                auto_key = cmds.autoKeyframe(state=True, query=True)
                if auto_key:
                    cmds.autoKeyframe(state=False)
                cmds.setAttr("{}.rotate{}".format(ctrl, attr), data[ctrl]["rotate{}".format(attr)])
                if auto_key:
                    cmds.autoKeyframe(state=True)

    def no_nurbs_in_scene(self):
        """
        Description:
            Error if there is no nurbsCurves or nurbsSurfaces in the scene
        """
        om.MGlobal.displayError("Couldn't find nurbsCurve or nurbsSurface in scene.")

    def split_string(self, name, split):
        """
        Description:
            Splits a controller name in the places defined in split
        Args:
            name: A string of the name of a controller
            split: A string with the places the name should be split
        """
        split_list = name.split(split)
        # Getting the lengt of the split name
        lengt = len(split_list) - 1
        # Making a list of the different combinations of names
        return_dict = {}
        return_dict["index"] = []
        return_dict["string"] = []

        # Iterating over the length to get the correct amount of item in the list
        for i in range(lengt):
            string = ""
            index = None
            # Iterating over the split name to resample the name
            for x, item in enumerate(split_list):
                string += item
                # Skip adding the side_str
                # if the two for loops are on same iteration
                # also don't add the side_str at the end
                if i == x:
                    index = len(string)
                    return_dict["index"].append(index)
                if not i == x and x != lengt:
                    string += split
            # In case the same letter is next to each other
            # like the word 'belly' would split 'bel' 'y' and 'be' 'ly'
            # and when reassembled it would give very on both
            if not string in return_dict["string"]:
                return_dict["string"].append(string)
        return return_dict

    def is_even(self, number):
        """
        Args:
            number: An number can be integre or float
        Return:
            Returns True if the number is even, retuns False if number is odd
        """
        return (number % 2) == 0

    def is_mirror_same_as_dominants(self, mirror_axis, dominent, opp_dominent):
        """
        Args:
            mirror_axis: The usedefined mirror axis
            dominent: The dominent axis of the controller
            opp_dominent: The dominent axis of the opposite controller
        Return:
            Returns a True if the dominent and opposite domient axis
            is the same. And also the same as the mirror axis, no matter
            if the dominent axis is positive or negative.
        """
        return (
            mirror_axis == dominent
            and mirror_axis == opp_dominent
            or "-{}".format(mirror_axis) == dominent
            and "-{}".format(mirror_axis) == opp_dominent
        )

    def is_dominants_same_and_not_mirror(self, mirror_axis, dominent, opp_dominent):
        """
        Args:
            mirror_axis: The usedefined mirror axis
            dominent: The dominent axis of the controller
            opp_dominent: The dominent axis of the opposite controller

        Return:
            Returns a True if the dominent and opposite domient axis
            is the same. And they are not the same as the mirror axis,
            no matter if the dominent axis is positive or negative.
        """
        pos_mirror = dominent == opp_dominent and not dominent == mirror_axis
        neg_mirror = dominent == opp_dominent and not dominent == "-{}".format(
            mirror_axis
        )
        # Returning False if any of the two statement is False
        if not pos_mirror or not neg_mirror:
            return False
        else:
            return True

    def reassemble_ctrl_name(self, name, side, index):
        """
        Args:
            name: The name of the controller without the side
            side: The side naming convention
            index: Defines the place the side should be put in the name

        Return:
            Returns the name of the controller including the side
        """
        # Creating the name of the ctrl
        ctrl_name = ""
        for i, letter in enumerate(name):
            # If the index and i is the same
            # then that is where the side should be
            if i == index:
                ctrl_name += side
            ctrl_name += letter
            # If the index and len of name is the same
            # then the side is at the end of the name
            if len(name) == index and i + 1 == index:
                ctrl_name += side
        return ctrl_name

    def get_controllers(self, side_con=["L", "R", "l", "r", "Lf", "Rt"]):
        """
        Args:
            side_con: A list of naming conventions for the sides.
                This list must have the same naming convention next
                to eachother with the right name being the higher index.
                We have when upper ("L") is used the left is at index 0
                and the right ("R") is one above at index 1.
                When lower naming is used left is at index 2, with the
                right being one above at index 3. So left must always be
                an even number and right must always an odd number one higher.

        Return: Returns a dictionary with keys for left, right, middle and all
            controllers. Also returns a pair dictionary that contains what
            controllers is a pair in the sense of what is the left side and
            what is the right side. And then the pair is assigned a number.
        """
        # Finding all the nurb curves to get the shape node on the controllers
        nurbs_curve_list = cmds.ls(type="nurbsCurve")
        nurbs_surface_list = cmds.ls(type="nurbsSurface")
        if nurbs_surface_list:
            for nurb in nurbs_surface_list:
                nurbs_curve_list.append(nurb)
        shape_list = nurbs_curve_list

        ctrl_list = []
        left_ctrl_list = []
        right_ctrl_list = []
        middle_ctrl_list = []
        str_combinations = []
        return_dict = {}
        pair_dict = {}
        pair_dict["controls"] = {}
        pair_dict["pairNumber"] = {}
        pair_number = 0

        # Iterating over all the shapes
        for shape in shape_list:
            parent = cmds.listRelatives(shape, parent=True)[0]
            # Seeing if there are multiple controllers with the same name
            dub_names = cmds.ls(parent, exactType="transform")
            for ctrl in dub_names:
                clash_name = ctrl.rsplit("|", 1)[-1]

                if not ctrl in ctrl_list:
                    # Seeing if the controller got a keyable attributes,
                    # otherwise there is no reason to mirror the controls
                    if cmds.listAttr(ctrl, keyable=True):
                        ctrl_list.append(ctrl)
                        # Making the assumption that every rigger
                        # is using either "L", "l", "R" or "r" to define side
                        # this list can also be expanded with Lf and Rt if wished
                        for i, side in enumerate(side_con):
                            # if the ctrl == clash name, then there
                            # is not a clahsing name
                            if ctrl == clash_name:
                                names = self.split_string(ctrl, side)
                            else:
                                names = self.split_string(clash_name, side)
                            if names:
                                for name in names["string"]:
                                    # If the name is in the sting combination
                                    # then it means that when splitting the
                                    # left and right side it has
                                    # resultet in the same string
                                    # Therefore the current ctrl
                                    # is a right controller
                                    if name in str_combinations:
                                        # Finding what index the split string
                                        # name that is both left and right side is.
                                        index_dict = names["string"].index(name)
                                        # Using that to get where
                                        # in the string the left right name is
                                        index = names["index"][index_dict]

                                        # Creating the name of the controllers
                                        even = self.is_even(i)
                                        if even:
                                            right_side = side_con[i + 1]
                                            left_side = side_con[i]
                                        else:
                                            right_side = side_con[i]
                                            left_side = side_con[i - 1]
                                        right_ctrl = self.reassemble_ctrl_name(name, right_side, index)
                                        left_ctrl = self.reassemble_ctrl_name(name, left_side, index)
                                        if ctrl == clash_name:
                                            if (
                                                not right_ctrl
                                                in right_ctrl_list
                                            ):
                                                right_ctrl_list.append(right_ctrl)
                                            if not left_ctrl in left_ctrl_list:
                                                left_ctrl_list.append(left_ctrl)
                                            pair_dict["controls"][
                                                right_ctrl
                                            ] = pair_number
                                            pair_dict["controls"][
                                                left_ctrl
                                            ] = pair_number
                                            pair_dict["pairNumber"][
                                                pair_number
                                            ] = [
                                                left_ctrl,
                                                right_ctrl,
                                            ]
                                            pair_number += 1
                                        else:
                                            left_dubs = cmds.ls(left_ctrl, exactType="transform")
                                            right_dubs = cmds.ls(right_ctrl, exactType="transform")
                                            for left_dub, right_dub in zip(
                                                left_dubs, right_dubs
                                            ):
                                                pair_dict["controls"][
                                                    left_dub
                                                ] = pair_number
                                                pair_dict["controls"][
                                                    right_dub
                                                ] = pair_number
                                                pair_dict["pairNumber"][
                                                    pair_number
                                                ] = [
                                                    left_dub,
                                                    right_dub,
                                                ]
                                                pair_number += 1
                                                if (
                                                    not left_dub
                                                    in left_ctrl_list
                                                ):
                                                    left_ctrl_list.append(left_dub)
                                                if (
                                                    not right_dub
                                                    in right_ctrl_list
                                                ):
                                                    right_ctrl_list.append(right_dub)
                                    else:
                                        # Adding the name to a list,
                                        # to check if right side matches
                                        str_combinations.append(name)

        for ctrl in ctrl_list:
            if not ctrl in right_ctrl_list and not ctrl in left_ctrl_list:
                middle_ctrl_list.append(ctrl)
        return_dict["left"] = left_ctrl_list
        return_dict["right"] = right_ctrl_list
        return_dict["middle"] = middle_ctrl_list
        return_dict["all"] = ctrl_list
        return_dict["pair"] = pair_dict
        return return_dict

    def mirror_side_ctrl(self, ctrl_list, data, mirror_axis, pair_dict, vector_data):
        """
        Description:
            Mirrors controller from one side to the opposite (opp)
        Args:
            ctrl_list: A list of controllers
            data: A dictionary containing controllers with its keyable
                attributes visible in the channelbox as its values
            mirror_axis: A string of what is the mirror axis
            pair_dict: A dictionary with the controllers and opposite
                controllers set in pairs
            vector_data: a dictionary containing the vectors of the axis on
                all the controllers
        """

        for ctrl in ctrl_list:
            # Getting pair number
            pair_number = pair_dict["controls"][ctrl]
            for pair_ctrl in pair_dict["pairNumber"][pair_number]:
                if not pair_ctrl == ctrl:
                    opp_ctrl = pair_ctrl
            # Getting the direction of the axis on controller
            x_axis = vector_data[ctrl]["x_axis"]
            y_axis = vector_data[ctrl]["y_axis"]
            z_axis = vector_data[ctrl]["z_axis"]

            # Getting the direction of the axis on opposite controller
            opp_x_axis = vector_data[opp_ctrl]["x_axis"]
            opp_y_axis = vector_data[opp_ctrl]["y_axis"]
            opp_z_axis = vector_data[opp_ctrl]["z_axis"]

            for attr in data[ctrl].keys():
                value = data[ctrl][attr]
                x_dominating = self.get_vectors_dominating_axis(x_axis)
                y_dominating = self.get_vectors_dominating_axis(y_axis)
                z_dominating = self.get_vectors_dominating_axis(z_axis)
                opp_x_dominating = self.get_vectors_dominating_axis(opp_x_axis)
                opp_y_dominating = self.get_vectors_dominating_axis(opp_y_axis)
                opp_z_dominating = self.get_vectors_dominating_axis(opp_z_axis)

                # Finding what axis is pointing the most to the mirror axis
                mirror_attr = self.get_mirror_axis_dominent_vector(
                    mirror_axis,
                    x_dominating,
                    y_dominating,
                    z_dominating,
                )

                if attr.__contains__("scale"):
                    cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                # Seeing if the controller has the
                # exact same orientation in the world
                elif (
                    x_dominating == opp_x_dominating
                    and y_dominating == opp_y_dominating
                    and z_dominating == opp_z_dominating
                ):
                    # The rotation on the mirror axis should be the same
                    if attr.__contains__("rotate{}".format(mirror_attr)):
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                    # The rotation on the other axis should be the negative value
                    elif attr.__contains__("rotate"):
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    # The translation on the mirror axis
                    # should be the negative value
                    elif attr.__contains__("translate{}".format(mirror_attr)):
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    # The translation on the other axis should be the same
                    else:
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                elif attr.__contains__("translate"):
                    # Checking if both of the dominant axis matches the mirror axis
                    # this will get joints mirrored with behavior
                    if self.is_mirror_same_as_dominants(mirror_axis, x_dominating, opp_x_dominating):
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    elif self.is_mirror_same_as_dominants(mirror_axis, y_dominating, opp_y_dominating):
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    elif self.is_mirror_same_as_dominants(mirror_axis, z_dominating, opp_z_dominating):
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    # Checking if the dominant axis matches,
                    # since if it has the same axis it will need the same value
                    # and the other axis need to be negative
                    elif x_dominating == opp_x_dominating:
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                        elif attr.__contains__("X"):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                        else:
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    elif y_dominating == opp_y_dominating:
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                        elif attr.__contains__("Y"):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                        else:
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    elif z_dominating == opp_z_dominating:
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                        elif attr.__contains__("Z"):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                        else:
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                    else:
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                elif attr.__contains__("rotate"):
                    if self.is_dominants_same_and_not_mirror(mirror_axis, x_dominating, opp_x_dominating):
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                        elif attr.__contains__("X"):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                        else:
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                    elif self.is_dominants_same_and_not_mirror(mirror_axis, y_dominating, opp_y_dominating):
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                        elif attr.__contains__("Y"):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                        else:
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                    elif self.is_dominants_same_and_not_mirror(mirror_axis, z_dominating, opp_z_dominating):
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                        elif attr.__contains__("Z"):
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), -value)
                        else:
                            cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                    else:
                        cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)
                else:
                    cmds.setAttr("{}.{}".format(opp_ctrl, attr), value)

    def mirror_middle_ctrl(self, ctrl_list, data, mirror_axis, vector_data):
        """
        Description:
            Flips the middle controllers

        Args:
            ctrl_list: A list of middle controllers
            data: A dictionary containing controllers with its keyable
                attributes visible in the channelbox as its values
            mirror_axis: A string of what is the mirror axis
            vector_data: a dictionary containing the vectors of the axis on
                all the controllers
        """
        for ctrl in ctrl_list:
            # Getting the direction of the axis on middle controller
            # Getting the direction of the axis on controller
            x_axis = vector_data[ctrl]["x_axis"]
            y_axis = vector_data[ctrl]["y_axis"]
            z_axis = vector_data[ctrl]["z_axis"]

            for attr in data[ctrl].keys():
                value = data[ctrl][attr]
                x_dominating = self.get_vectors_dominating_axis(x_axis)
                y_dominating = self.get_vectors_dominating_axis(y_axis)
                z_dominating = self.get_vectors_dominating_axis(z_axis)
                # Finding what axis is pointing the most to the mirror axis
                mirror_attr = self.get_mirror_axis_dominent_vector(mirror_axis, x_dominating, y_dominating, z_dominating)
                if attr.__contains__("translate"):
                    if attr.__contains__(mirror_attr):
                        cmds.setAttr("{}.{}".format(ctrl, attr), -value)
                    else:
                        pass
                elif attr.__contains__("rotate"):
                    if attr.__contains__(mirror_attr):
                        cmds.setAttr("{}.{}".format(ctrl, attr), value)
                    else:
                        cmds.setAttr("{}.{}".format(ctrl, attr), -value)

    def flip_frame(self, left_ctrl_list, right_ctrl_list, middle_ctrl_list, data, pair_dict, mirror_axis, vector_data):
        """
        Description:
            Flips all the controllers
        Args:
            left_ctrl_list: A list of all left controllers
            right_ctrl_list: A list of all right controllers
            middle_ctrl_list: A list of all middle controllers
            data: A dictionary containing controllers with its keyable
                attributes visible in the channelbox as its values
            pair_dict: A dictionary with the controllers and opposite
                controllers set in pairs
            mirror_axis: A string of what is the mirror axis
            vector_data: a dictionary containing the vectors of the axis on
                all the controllers
        """
        self.mirror_side_ctrl(ctrl_list=left_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data)
        self.mirror_side_ctrl(ctrl_list=right_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data)
        self.mirror_middle_ctrl(middle_ctrl_list, data, mirror_axis, vector_data)

    def mirror_control(self):
        """
        Description:
            This is here the controllers are found and are mirrored
        """
        cmds.undoInfo(openChunk=True)
        left_naming = self.get_left_name()
        right_naming = self.get_right_name()
        if not left_naming and not right_naming:
            side_con = ["L", "R", "l", "r", "Lf", "Rt"]
        elif not left_naming and right_naming:
            om.MGlobal.displayError("There is inputted {} in right naming convention. " "Therefore left naming convention " "also needs an input".format(right_naming))
            return
        elif left_naming and not right_naming:
            om.MGlobal.displayError("There is inputted {} in left naming convention. " "Therefore right naming convention " "also needs an input".format(left_naming))
            return
        else:
            side_con = [left_naming, right_naming]

        controls = self.get_controllers(side_con)
        left_ctrl_list = controls["left"]
        right_ctrl_list = controls["right"]
        middle_ctrl_list = controls["middle"]
        ctrl_list = controls["all"]
        pair_dict = controls["pair"]
        vector_data = self.get_vector_data(ctrl_list)

        if not ctrl_list:
            self.no_nurbs_in_scene()
            return

        mirror_axis = self.get_mirror_axis()
        data = self.get_attribute_data(ctrl_list)

        operation = self.get_operation()
        if operation == OperationType.left_to_right:
            self.mirror_side_ctrl(ctrl_list=left_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data)
        elif operation == OperationType.right_to_left:
            self.mirror_side_ctrl(ctrl_list=right_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data)
        elif operation == OperationType.flip:
            self.flip_frame(left_ctrl_list, right_ctrl_list, middle_ctrl_list, data, pair_dict, mirror_axis, vector_data)
        elif operation == OperationType.flip_to_frame:
            self.set_time(self.get_flip_frame())
            self.flip_frame(left_ctrl_list, right_ctrl_list, middle_ctrl_list, data, pair_dict, mirror_axis, vector_data)
        elif operation == OperationType.mirror_middle:
            self.mirror_middle_ctrl(middle_ctrl_list, data, mirror_axis, vector_data)
        elif operation == OperationType.selected:
            (
                left_sel_controls,
                right_sel_controls,
                middle_sel_controls,
            ) = self.get_selected_controls(ctrl_list, left_ctrl_list, right_ctrl_list, middle_ctrl_list)

            if not left_sel_controls and not right_sel_controls and not middle_sel_controls:
                om.MGlobal.displayError("No controller is selected")
                return
            if left_sel_controls:
                self.mirror_side_ctrl(
                    ctrl_list=left_sel_controls,
                    data=data,
                    mirror_axis=mirror_axis,
                    pair_dict=pair_dict,
                    vector_data=vector_data,
                )
            if right_sel_controls:
                self.mirror_side_ctrl(
                    ctrl_list=right_sel_controls,
                    data=data,
                    mirror_axis=mirror_axis,
                    pair_dict=pair_dict,
                    vector_data=vector_data,
                )
            if middle_sel_controls:
                self.mirror_middle_ctrl(middle_sel_controls, data, mirror_axis, vector_data)
        elif operation == OperationType.not_selected:
            (
                left_sel_controls,
                right_sel_controls,
                middle_sel_controls,
            ) = self.get_selected_controls(ctrl_list, left_ctrl_list, right_ctrl_list, middle_ctrl_list)
            removed_left_ctrl_list = self.remove_items_from_list(left_ctrl_list, left_sel_controls)
            removed_right_ctrl_list = self.remove_items_from_list(right_ctrl_list, right_sel_controls)
            removed_middle_ctrl_list = self.remove_items_from_list(middle_ctrl_list, middle_sel_controls)

            if self.left_to_right_rb.isChecked():
                if removed_left_ctrl_list:
                    self.mirror_side_ctrl(
                        ctrl_list=removed_left_ctrl_list,
                        data=data,
                        mirror_axis=mirror_axis,
                        pair_dict=pair_dict,
                        vector_data=vector_data,
                    )
                if removed_middle_ctrl_list:
                    self.mirror_middle_ctrl(
                        removed_middle_ctrl_list,
                        data,
                        mirror_axis,
                        vector_data,
                    )
            elif self.right_to_left_rb.isChecked():
                if removed_right_ctrl_list:
                    self.mirror_side_ctrl(
                        ctrl_list=removed_right_ctrl_list,
                        data=data,
                        mirror_axis=mirror_axis,
                        pair_dict=pair_dict,
                        vector_data=vector_data,
                    )
                if removed_middle_ctrl_list:
                    self.mirror_middle_ctrl(
                        removed_middle_ctrl_list,
                        data,
                        mirror_axis,
                        vector_data,
                    )
            elif self.flip_rb.isChecked():
                self.flip_frame(
                    removed_left_ctrl_list,
                    removed_right_ctrl_list,
                    removed_middle_ctrl_list,
                    data,
                    pair_dict,
                    mirror_axis,
                    vector_data,
                )

            if not left_sel_controls and not right_sel_controls and not middle_sel_controls:
                om.MGlobal.displayWarning("No controller is selected")
        if not left_ctrl_list and not right_ctrl_list:
            om.MGlobal.displayWarning("Couldn't find side controllers. " "Every controller behave as a middle controller.")
        cmds.undoInfo(closeChunk=True)

    def open_url(self):
        pass

    def showEvent(self, e):
        super(Mirror_Pose_Window_Manager, self).showEvent(e)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, Mirror_Pose_Window_Manager):
            super(Mirror_Pose_Window_Manager, self).closeEvent(e)
            self.geometry = self.saveGeometry()


if __name__ == "__main__":
    global mirror_control
    try:
        mirror_control.close()
        mirror_control.deleteLater()
    except:
        pass

    mirror_control = Mirror_Pose_Window_Manager()
    mirror_control.show()

