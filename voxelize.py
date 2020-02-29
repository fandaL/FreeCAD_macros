# Macro to create numpy array with 0-1 values for filled-empty voxels from mesh
# Principle:
#    1) fill voxels which contain mesh nodes, i.e. mesh boundary voxels
#    2) determine empty voxels out of the mesh by going neighbour by neighbour from bounding-box to mesh boundary voxels
#    3) fill remaining voxels which was left inside the mesh
# Note: algorithm will fail if input mesh is rough
#
# How to use:
#    define voxel_size
#    select mesh object in FreeCAD and run this code
#    output is numpy array: voxels
#    ref_point contains coordinates of the bounding box corner

import numpy as np

# INPUTS

voxel_size = 1.0

# CODE

selection = FreeCADGui.Selection.getSelection()
selection_name = selection[0].Name
input_mesh = App.ActiveDocument.getObject(selection_name).Mesh

mesh_box = [input_mesh.BoundBox.XLength,
            input_mesh.BoundBox.YLength,
            input_mesh.BoundBox.ZLength]
ref_point = [input_mesh.BoundBox.XMin,
             input_mesh.BoundBox.YMin,
             input_mesh.BoundBox.ZMin]

voxels = np.zeros([int(mesh_box[0] // voxel_size) + 1,
                        int(mesh_box[1] // voxel_size) + 1,
                        int(mesh_box[2] // voxel_size) + 1])

for p in input_mesh.Points:
    x_pos = int((p.x - ref_point[0]) // voxel_size)
    y_pos = int((p.y - ref_point[1]) // voxel_size)
    z_pos = int((p.z - ref_point[2]) // voxel_size)
    voxels[x_pos, y_pos, z_pos] = 1

# # debugging - create point for each boundary voxel - time consuming for more than few voxels
# import Draft
# for x_pos in range(voxels.shape[0]):
#     for y_pos in range(voxels.shape[1]):
#         for z_pos in range(voxels.shape[2]):
#             if voxels[x_pos, y_pos, z_pos] == 1:
#                 x = x_pos * voxel_size + voxel_size / 2 + ref_point[0]
#                 y = y_pos * voxel_size + voxel_size / 2 + ref_point[1]
#                 z = z_pos * voxel_size + voxel_size / 2 + ref_point[2]
#                 Draft.makePoint(x, y, z)

def get_neighbours(x_pos, y_pos, z_pos):
    """add neighbouring voxels if voxel was 0"""
    try:
        neighbours.remove((x_pos, y_pos, z_pos))
    except KeyError:  # box-boundary voxels not in neighbours
        pass
    if voxels[x_pos, y_pos, z_pos] == 0:
        voxels[x_pos, y_pos, z_pos] = -1
        for xx, yy, zz in [[x_pos + 1, y_pos, z_pos],
                           [x_pos - 1, y_pos, z_pos],
                           [x_pos, y_pos + 1, z_pos],
                           [x_pos, y_pos - 1, z_pos],
                           [x_pos, y_pos, z_pos + 1],
                           [x_pos, y_pos, z_pos - 1]]:  # six direct neighbours, not diagonal voxels
            try:
                if voxels[xx, yy, zz] == 0:
                    neighbours.add((xx, yy, zz))
            except IndexError:
                pass
    return

# find empty voxels outside the mesh
# go through box-boundary voxels
neighbours = set ()
for x_pos in [0, voxels.shape[0] - 1]:
    for y_pos in range(voxels.shape[1]):
        for z_pos in range(voxels.shape[2]):
            get_neighbours(x_pos, y_pos, z_pos)

for y_pos in [0, voxels.shape[1] - 1]:
    for x_pos in range(voxels.shape[0]):
        for z_pos in range(voxels.shape[2]):
            get_neighbours(x_pos, y_pos, z_pos)

for z_pos in [0, voxels.shape[2] - 1]:
    for x_pos in range(voxels.shape[0]):
        for y_pos in range(voxels.shape[1]):
            get_neighbours(x_pos, y_pos, z_pos)

while neighbours:
    neighbours_locked = neighbours.copy()
    for x_pos, y_pos, z_pos in neighbours_locked:
        get_neighbours(x_pos, y_pos, z_pos)

# fill inner voxels
for pos, val in np.ndenumerate(voxels):
    if val == 0:  # inner voxel
        voxels[pos] = 1
    elif val == -1:  # outer empty voxel
        voxels[pos] = 0

# # debugging - create point for each voxel - time consuming for more than few voxels
# import Draft
# for x_pos in range(voxels.shape[0]):
#     for y_pos in range(voxels.shape[1]):
#         for z_pos in range(voxels.shape[2]):
#             if voxels[x_pos, y_pos, z_pos] == 1:
#                 x = x_pos * voxel_size + voxel_size / 2 + ref_point[0]
#                 y = y_pos * voxel_size + voxel_size / 2 + ref_point[1]
#                 z = z_pos * voxel_size + voxel_size / 2 + ref_point[2]
#                 Draft.makePoint(x, y, z)
