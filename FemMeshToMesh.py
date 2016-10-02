import FreeCADGui
from PySide import QtGui
import Mesh

__title__ = "FemMesh to Mesh converter"
__Comment__ = "Macro converts FemMesh to Mesh through VisibleElementFaces"
__Help__ = "Select FemMesh and run the macro"
__author__ = "Frantisek Loeffelmann "
__date__ = "02/10/2016"


def extend_by_triangle(i, j, k):
    triangle = [input_mesh.getNodeById(element_nodes[i]),
                input_mesh.getNodeById(element_nodes[j]),
                input_mesh.getNodeById(element_nodes[k])]
    return output_mesh.extend(triangle)


selection = FreeCADGui.Selection.getSelection()
if not selection:
    QtGui.QMessageBox.critical(None, "femmesh2mesh", "FemMesh object has to be selected!")
    assert selection, "FemMesh object has to be selected!"

selection_name = selection[0].Name
try:
    input_mesh = App.ActiveDocument.getObject(selection_name).FemMesh
except AttributeError:
    QtGui.QMessageBox.critical(None, "femmesh2mesh", "FemMesh object has to be selected!")
    assert selection, "FemMesh object has to be selected!"

visible_faces = Gui.ActiveDocument.getObject(selection_name).VisibleElementFaces
output_mesh = []
for [element, face] in visible_faces:
    element_nodes = input_mesh.getElementNodes(element)
    if element in input_mesh.Faces:
        if len(element_nodes) in [3, 6]:  # tria3 or tria6 (ignoring mid-nodes)
            extend_by_triangle(0, 1, 2)
        elif len(element_nodes) in [4, 8]:  # quad4 or quad8 (ignoring mid-nodes)
            extend_by_triangle(0, 1, 2)
            extend_by_triangle(2, 3, 0)

    else:  # element in input_mesh.volumes:
        if len(element_nodes) in [4, 10]:  # tetra4 or tetra10 (ignoring mid-nodes)
            if face == 1:
                extend_by_triangle(0, 1, 2)
            elif face == 2:
                extend_by_triangle(0, 3, 1)
            elif face == 3:
                extend_by_triangle(1, 3, 2)
            elif face == 4:
                extend_by_triangle(2, 3, 0)
        elif len(element_nodes) in [8, 20]:  # hexa8 or hexa20 (ignoring mid-nodes)
            if face == 1:
                extend_by_triangle(0, 1, 2)
                extend_by_triangle(2, 3, 0)
            elif face == 2:
                extend_by_triangle(4, 7, 6)
                extend_by_triangle(6, 5, 4)
            elif face == 3:
                extend_by_triangle(0, 4, 5)
                extend_by_triangle(5, 1, 0)
            elif face == 4:
                extend_by_triangle(1, 5, 6)
                extend_by_triangle(6, 2, 1)
            elif face == 5:
                extend_by_triangle(2, 6, 7)
                extend_by_triangle(7, 3, 2)
            elif face == 6:
                extend_by_triangle(3, 7, 4)
                extend_by_triangle(4, 0, 3)
        elif len(element_nodes) in [6, 15]:  # penta6 or penta15 (ignoring mid-nodes)
            if face == 1:
                extend_by_triangle(0, 1, 2)
            elif face == 2:
                extend_by_triangle(3, 5, 4)
            elif face == 3:
                extend_by_triangle(0, 3, 4)
                extend_by_triangle(4, 1, 0)
            elif face == 4:
                extend_by_triangle(1, 4, 5)
                extend_by_triangle(5, 2, 1)
            elif face == 5:
                extend_by_triangle(2, 5, 3)
                extend_by_triangle(3, 0, 2)
        elif len(element_nodes) in [5, 13]:  # pyra5 or pyra13 (ignoring mid-nodes)
            if face == 1:
                extend_by_triangle(0, 1, 2)
                extend_by_triangle(2, 3, 0)
            elif face == 2:
                extend_by_triangle(0, 4, 1)
            elif face == 3:
                extend_by_triangle(1, 4, 2)
            elif face == 4:
                extend_by_triangle(2, 4, 3)
            elif face == 5:
                extend_by_triangle(3, 4, 0)

if output_mesh:
    obj = Mesh.Mesh(output_mesh)
    Mesh.show(obj)
