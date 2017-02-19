# quick macro to create labels of nodes or elements
# code is not efficient - it takes long time to create labels of mesh with more then few nodes (elements)

from PySide import QtGui, QtCore
import FreeCAD
import Draft

# parameters
font_size = 14
text_color = (0.0000, 0.0000, 0.0000)

class CreateLabelsInput(QtGui.QMainWindow):
    """"""
    def __init__(self):
        super(CreateLabelsInput, self).__init__()
        self.initUI()
    def initUI(self):
        self.result = userCancelled
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(250, 250, 300, 180)
        self.setWindowTitle("Create Labels")
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # create comments
        self.label1 = QtGui.QLabel(" Insert node(element) numbers or let free to take all: ", self)
        self.label1.setFixedWidth(300)
        self.label1.move(0, 0)
        self.label2 = QtGui.QLabel(" (e.g. 1, 2, 10:12 means numbers 1, 2, 10, 11, 12)", self)
        self.label2.setFixedWidth(300)
        self.label2.move(0, 30)
        self.label3 = QtGui.QLabel(" (warning: more then few labels take long to create)", self)
        self.label3.setFixedWidth(300)
        self.label3.move(0, 60)
        # text input field
        self.textInput = QtGui.QLineEdit(self)
        self.textInput.setFixedWidth(300)
        self.textInput.move(0, 90)
        pushButton1 = QtGui.QPushButton('Node labels', self)
        pushButton1.clicked.connect(self.onPushButton1)
        pushButton1.move(0, 120)
        pushButton2 = QtGui.QPushButton('Element labels', self)
        pushButton2.clicked.connect(self.onPushButton2)
        pushButton2.move(100, 120)
        # cancel button
        cancelButton = QtGui.QPushButton('Cancel', self)
        cancelButton.clicked.connect(self.onCancel)
        cancelButton.move(0, 150)
        self.show()
    def onPushButton1(self):  # nodes
        user_input = self.textInput.text()
        [selection_name, mesh_object] = get_selection()
        numbers_to_label = input_read(user_input)
        create_node_labels(selection_name, mesh_object, numbers_to_label)
    def onPushButton2(self):  # elements
        user_input = self.textInput.text()
        [selection_name, mesh_object] = get_selection()
        numbers_to_label = input_read(user_input)
        create_element_labels(selection_name, mesh_object, numbers_to_label)
    def onCancel(self):
            self.result = userCancelled
            self.close()


def get_selection():
    try:
        selection = FreeCADGui.Selection.getSelection()
        selection_name = selection[0].Name
    except IndexError:
        QtGui.QMessageBox.critical(None, "Missing selection", "FEM mesh object needs to be selected.")
    try:
        mesh_object = App.ActiveDocument.getObject(selection_name).FemMesh
    except AttributeError:
        QtGui.QMessageBox.critical(None, "Selection object error", "FEM mesh object needs to be selected.")
    return selection_name, mesh_object


def input_read(user_input):
    words = user_input.replace(",", " ")
    words = words.split()
    numbers_to_label = []
    for w in range(len(words)):
        if words[w].find(":") == -1:
            numbers_to_label.append(int(words[w]))
        else:
            splitted = words[w].split(":")
            numbers_to_label.append(int(splitted[0]))
            for i in range(int(splitted[1]) - int(splitted[0])):
                numbers_to_label.append(int(splitted[0]) + i + 1)
    return numbers_to_label


def nn_label(mesh_object, group, nn):
    a = Draft.makeText([str(nn)], point=mesh_object.Nodes[nn])
    a.ViewObject.Justification = "Center"
    a.ViewObject.DisplayMode = "Screen"
    a.ViewObject.FontSize = font_size
    a.ViewObject.TextColor = text_color
    group.addObject(a)


def create_node_labels(selection_name, mesh_object, numbers_to_label):
    group = App.ActiveDocument.addObject("App::DocumentObjectGroup", selection_name + "_node_numbers")
    if numbers_to_label:
        for nn in numbers_to_label:
            nn_label(mesh_object, group, nn)
    else:
        for nn in mesh_object.Nodes:
            nn_label(mesh_object, group, nn)


def en_label(mesh_object, group, en):
    position = [0, 0, 0]
    denominator = len(mesh_object.getElementNodes(en))
    for nn in mesh_object.getElementNodes(en):
        position[0] += mesh_object.Nodes[nn][0] / denominator
        position[1] += mesh_object.Nodes[nn][1] / denominator
        position[2] += mesh_object.Nodes[nn][2] / denominator
    a = Draft.makeText([str(en)], Draft.Vector(position))
    a.ViewObject.Justification = "Center"
    a.ViewObject.DisplayMode = "Screen"
    a.ViewObject.FontSize = font_size
    a.ViewObject.TextColor = text_color
    group.addObject(a)


def create_element_labels(selection_name, mesh_object, numbers_to_label):
    group = App.ActiveDocument.addObject("App::DocumentObjectGroup", selection_name + "_element_numbers")
    if numbers_to_label:
        for en in numbers_to_label:
            en_label(mesh_object, group, en)
    else:
        for en in mesh_object.Volumes + mesh_object.Faces + mesh_object.Edges:
            en_label(mesh_object, group, en)

# Constant definitions
userCancelled = "Cancelled"
# open dialog window
CreateLabelsInput()
