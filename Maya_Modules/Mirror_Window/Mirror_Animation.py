# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from functools import partial

#処理させたいノードのルートをあらかじめ選択して実行する前提で、選択からジョイントのルートを取得

rootNode = cmds.ls(sl = True)[0]
mel.eval('GoToBindPose;')

jointList = cmds.ls(rootNode, dag=True, type='joint')

inputLocList = []
culNodeList = []

outputLocDict = {}
outputOffsetList = []

#各ジョイントごとの処理
for j in jointList:
    #あらかじめ反転対象のジョイントを探しておく
    mirrorJoint = j
    if '_L' in j:
        mirrorJoint = j.replace('_L', '_R')
    elif '_R' in j:
        mirrorJoint = j.replace('_R', '_L')
    #ミラー対象が見当たらなければ処理をスキップ
    if not mirrorJoint in jointList:
        continue

    print(mirrorJoint)
    #各ジョイントごとにTransformノードを作り、コンストレインで接続
    loc = cmds.createNode('transform')
    inputLocList.append(loc)

    #反転ベクトルを生成するためのノード群を作成
    rotateMatrix = cmds.createNode('composeMatrix')
    aimVectorNode = cmds.createNode('composeMatrix')
    upVectorNode = cmds.createNode('composeMatrix')

    aimVectorMatrix = cmds.createNode('multMatrix')
    upVectorMatrix = cmds.createNode('multMatrix')

    aimVectorDecomposeMatrix = cmds.createNode('decomposeMatrix')
    upVectorDecomposeMatrix = cmds.createNode('decomposeMatrix')

    mirrorAimVector = cmds.createNode('floatMath')
    mirrorUpVector = cmds.createNode('floatMath')

    getBendAxisAngle = cmds.createNode('angleBetween')
    getRollAxisAngle = cmds.createNode('angleBetween')

    getBendQuat = cmds.createNode('axisAngleToQuat')
    getRollQuat = cmds.createNode('axisAngleToQuat')

    getBendMatrix = cmds.createNode('composeMatrix')
    getBendedOrgUpVector = cmds.createNode('multMatrix')
    bendedUpVectorDecomposeMatrix = cmds.createNode('decomposeMatrix')

    quatCul = cmds.createNode('quatProd')
    quatToE = cmds.createNode('quatToEuler')

    mirrorPosNode = cmds.createNode('floatMath')

    culNodeList.extend(
        [rotateMatrix, aimVectorNode, upVectorNode, aimVectorMatrix, upVectorMatrix, aimVectorDecomposeMatrix, upVectorDecomposeMatrix,
         mirrorAimVector, mirrorUpVector, getBendAxisAngle, getRollAxisAngle, getBendQuat, getRollQuat, getBendMatrix, getBendedOrgUpVector,
         bendedUpVectorDecomposeMatrix, quatCul, quatToE, mirrorPosNode])

    #反転マトリクスのノード構築
    cmds.connectAttr('{}.rotate'.format(loc), '{}.inputRotate'.format(rotateMatrix))

    #aimVector/upVectorの定義
    cmds.setAttr('{}.inputTranslate'.format(aimVectorNode), 1.0, 0.0, 0.0)
    cmds.setAttr('{}.inputTranslate'.format(upVectorNode), 0.0, 1.0, 0.0)
    cmds.connectAttr('{}.outputMatrix'.format(aimVectorNode), '{}.matrixIn[0]'.format(aimVectorMatrix))
    cmds.connectAttr('{}.outputMatrix'.format(upVectorNode), '{}.matrixIn[0]'.format(upVectorMatrix))
    cmds.connectAttr('{}.outputMatrix'.format(rotateMatrix), '{}.matrixIn[1]'.format(aimVectorMatrix))
    cmds.connectAttr('{}.outputMatrix'.format(rotateMatrix), '{}.matrixIn[1]'.format(upVectorMatrix))
    cmds.connectAttr('{}.matrixSum'.format(aimVectorMatrix), '{}.inputMatrix'.format(aimVectorDecomposeMatrix))
    cmds.connectAttr('{}.matrixSum'.format(upVectorMatrix), '{}.inputMatrix'.format(upVectorDecomposeMatrix))
    cmds.connectAttr('{}.outputTranslateX'.format(aimVectorDecomposeMatrix), '{}.floatA'.format(mirrorAimVector))
    cmds.connectAttr('{}.outputTranslateX'.format(upVectorDecomposeMatrix), '{}.floatA'.format(mirrorUpVector))

    #ベクトル反転floatMathノードの値を操作
    cmds.setAttr('{}.floatB'.format(mirrorAimVector), -1.0)
    cmds.setAttr('{}.floatB'.format(mirrorUpVector), -1.0)
    cmds.setAttr('{}.operation'.format(mirrorAimVector), 2)
    cmds.setAttr('{}.operation'.format(mirrorUpVector), 2)

    #bend成分のベクトル接続
    cmds.connectAttr('{}.outFloat'.format(mirrorAimVector), '{}.vector2X'.format(getBendAxisAngle))
    cmds.connectAttr('{}.outputTranslateY'.format(aimVectorDecomposeMatrix), '{}.vector2Y'.format(getBendAxisAngle))
    cmds.connectAttr('{}.outputTranslateZ'.format(aimVectorDecomposeMatrix), '{}.vector2Z'.format(getBendAxisAngle))

    #aimVectorの規定値を現在のvector2の値から一時的にコネクションして切断し、値を設定する。
    cmds.connectAttr('{}.vector2'.format(getBendAxisAngle), '{}.vector1'.format(getBendAxisAngle))
    cmds.disconnectAttr('{}.vector2'.format(getBendAxisAngle), '{}.vector1'.format(getBendAxisAngle))

    #Roll成分のベクトル接続 ※vector1はまだ。
    cmds.connectAttr('{}.outFloat'.format(mirrorUpVector), '{}.vector2X'.format(getRollAxisAngle))
    cmds.connectAttr('{}.outputTranslateY'.format(upVectorDecomposeMatrix), '{}.vector2Y'.format(getRollAxisAngle))
    cmds.connectAttr('{}.outputTranslateZ'.format(upVectorDecomposeMatrix), '{}.vector2Z'.format(getRollAxisAngle))

    #Quaternion取得
    cmds.connectAttr('{}.axis'.format(getBendAxisAngle), '{}.inputAxis'.format(getBendQuat))
    cmds.connectAttr('{}.angle'.format(getBendAxisAngle), '{}.inputAngle'.format(getBendQuat))
    cmds.connectAttr('{}.axis'.format(getRollAxisAngle), '{}.inputAxis'.format(getRollQuat))
    cmds.connectAttr('{}.angle'.format(getRollAxisAngle), '{}.inputAngle'.format(getRollQuat))

    #Roll成分の回転基準のベクトルを計算
    cmds.connectAttr('{}.outputQuat'.format(getBendQuat), '{}.inputQuat'.format(getBendMatrix))
    cmds.setAttr('{}.useEulerRotation'.format(getBendMatrix), False)
    cmds.connectAttr('{}.outputMatrix'.format(upVectorNode), '{}.matrixIn[0]'.format(getBendedOrgUpVector))
    cmds.connectAttr('{}.outputMatrix'.format(getBendMatrix), '{}.matrixIn[1]'.format(getBendedOrgUpVector))
    cmds.connectAttr('{}.matrixSum'.format(getBendedOrgUpVector), '{}.inputMatrix'.format(bendedUpVectorDecomposeMatrix))

    #upVectorの回転計算の基準ベクトルVector1にコネクション
    cmds.connectAttr('{}.outputTranslate'.format(bendedUpVectorDecomposeMatrix), '{}.vector1'.format(getRollAxisAngle))

    #出力用のノードのコネクション
    #出力用ノードはオフセット用ノードとあらかじめ二重構造にしておく
    outputNode_offset = cmds.createNode('transform')
    outputOffsetList.append(outputNode_offset)
    outputNode = cmds.createNode('transform')
    cmds.parent(outputNode, outputNode_offset)
    outputLocDict[j] = outputNode

    cmds.connectAttr('{}.outputQuat'.format(getBendQuat), '{}.input1Quat'.format(quatCul))
    cmds.connectAttr('{}.outputQuat'.format(getRollQuat), '{}.input2Quat'.format(quatCul))
    cmds.connectAttr('{}.outputQuat'.format(quatCul), '{}.inputQuat'.format(quatToE))

    #接続はoffsetノードの方に。
    #回転出力の接続
    cmds.connectAttr('{}.outputRotate'.format(quatToE), '{}.r'.format(outputNode_offset))

    #移動成分の反転接続
    cmds.connectAttr('{}.tx'.format(loc), '{}.floatA'.format(mirrorPosNode))
    cmds.setAttr('{}.floatB'.format(mirrorPosNode), -1.0)
    cmds.setAttr('{}.operation'.format(mirrorPosNode), 2)

    cmds.connectAttr('{}.outFloat'.format(mirrorPosNode), '{}.tx'.format(outputNode_offset))
    cmds.connectAttr('{}.ty'.format(loc), '{}.ty'.format(outputNode_offset))
    cmds.connectAttr('{}.tz'.format(loc), '{}.tz'.format(outputNode_offset))

    #出力用ノードは、あらかじめ検索しておいた反転対象ノードと位置・向きを合わせておく
    cmds.delete(cmds.pointConstraint(mirrorJoint, outputNode))
    cmds.delete(cmds.orientConstraint(mirrorJoint, outputNode))

    #移動・回転に0.0をセットすることで初期位置に戻れるようにoffsetノードを用意
    cmds.pointConstraint(j, loc)
    cmds.orientConstraint(j, loc, mo=True)

st = cmds.playbackOptions(q=True, min=True)
et = cmds.playbackOptions(q=True, max=True)
cmds.bakeResults(outputOffsetList, sm=True, t=(st, et), at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

for node in inputLocList:
    if cmds.objExists(node):
        cmds.delete(node)
for node in culNodeList:
    if cmds.objExists(node):
        cmds.delete(node)

for j in jointList:
    scsJoint = j
    if 'Left' in j:
        scsJoint = j.replace('Left', 'Right')
    elif 'Right' in j:
        scsJoint = j.replace('Right', 'Left')
    if not scsJoint in outputLocDict.keys():
        continue
    cmds.pointConstraint(outputLocDict[scsJoint], j)
    cmds.orientConstraint(outputLocDict[scsJoint], j)

#反転アニメーションをベイク
cmds.bakeResults(jointList, sm=True, t=(st, et), at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
#不要になったoutputノード群は削除
cmds.delete(outputOffsetList)


