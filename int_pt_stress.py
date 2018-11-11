# This script serves to convert integration point data (von Mises stresses and PEEQ) from CalculiX dat file to vtk file.
# Mesh data are taken from inp file.
# All 3D, 2D and 1D elements are supported.
# When some elements have more integration points than others, zeros are written in place of missing values.
#
# CalculiX saves stresses and PEEQ to dat file for the given element set
# *EL PRINT, ELSET=EALL
# S, PEEQ
#
# Inputs

file_name = "Box_Mesh"  # file name without extension
write_all_integration_points = True  # if all integration point data should be written to vtk file

# Script
import math

# function importing inp mesh consisting of nodes, 3D, 2D, and 1D elements
def import_inp(file_name):
    nodes = {}  # dict with nodes position

    class Elements():
        seg2 = {}
        seg3 = {}
        tria3 = {}
        tria6 = {}
        quad4 = {}
        quad8 = {}
        tetra4 = {}
        tetra10 = {}
        hexa8 = {}
        hexa20 = {}
        penta6 = {}
        penta15 = {}
    model_definition = True
    domains = {}
    read_domain = False
    read_node = False
    elm_category = []
    elm_2nd_line = False
    elset_generate = False

    f = open(file_name + ".inp", "r")
    line = "\n"
    include = ""
    while line != "":
        if include:
            line = f_include.readline()
            if line == "":
                f_include.close()
                include = ""
                line = f.readline()
        else:
            line = f.readline()
        if line.strip() == '':
            continue
        elif line[0] == '*':  # start/end of a reading set
            if line[0:2] == '**':  # comments
                continue
            if line[:8].upper() == "*INCLUDE":
                start = 1 + line.index("=")
                include = line[start:].strip().strip('"')
                f_include = open(include, "r")
                continue
            read_node = False
            elm_category = []
            elm_2nd_line = False
            read_domain = False
            elset_generate = False

        # reading nodes
        if (line[:5].upper() == "*NODE") and (model_definition is True):
            read_node = True
        elif read_node is True:
            line_list = line.split(',')
            number = int(line_list[0])
            x = float(line_list[1])
            y = float(line_list[2])
            z = float(line_list[3])
            nodes[number] = [x, y, z]

        # reading elements
        elif line[:8].upper() == "*ELEMENT":
            current_elset = ""
            line_list = line[8:].split(',')
            for line_part in line_list:
                if line_part.split('=')[0].strip().upper() == "TYPE":
                    elm_type = line_part.split('=')[1].strip().upper()
                elif line_part.split('=')[0].strip().upper() == "ELSET":
                    current_elset = line_part.split('=')[1].strip()

            if elm_type in ["B21", "B31", "B31R", "T2D2", "T3D2"]:
                elm_category = Elements.seg2
                number_of_nodes = 2
            elif elm_type in ["B32", "B32R", "T3D3"]:
                elm_category = Elements.seg3
                number_of_nodes = 3
            elif elm_type in ["S3", "CPS3", "CPE3", "CAX3", "M3D3"]:
                elm_category = Elements.tria3
                number_of_nodes = 3
            elif elm_type in ["S6", "CPS6", "CPE6", "CAX6", "M3D6"]:
                elm_category = Elements.tria6
                number_of_nodes = 6
            elif elm_type in ["S4", "S4R", "CPS4", "CPS4R", "CPE4", "CPE4R", "CAX4", "CAX4R", "M3D4", "M3D4R"]:
                elm_category = Elements.quad4
                number_of_nodes = 4
            elif elm_type in ["S8", "S8R", "CPS8", "CPS8R", "CPE8", "CPE8R", "CAX8", "CAX8R", "M3D8", "M3D8R"]:
                elm_category = Elements.quad8
                number_of_nodes = 8
            elif elm_type == "C3D4":
                elm_category = Elements.tetra4
                number_of_nodes = 4
            elif elm_type == "C3D10":
                elm_category = Elements.tetra10
                number_of_nodes = 10
            elif elm_type in ["C3D8", "C3D8R", "C3D8I"]:
                elm_category = Elements.hexa8
                number_of_nodes = 8
            elif elm_type in ["C3D20", "C3D20R", "C3D20RI"]:
                elm_category = Elements.hexa20
                number_of_nodes = 20
            elif elm_type == "C3D6":
                elm_category = Elements.penta6
                number_of_nodes = 6
            elif elm_type == "C3D15":
                elm_category = Elements.penta15
                number_of_nodes = 15

        elif elm_category != []:
            line_list = line.split(',')
            if elm_2nd_line is False:
                en = int(line_list[0])  # element number
                elm_category[en] = []
                pos = 1
                if current_elset:  # save en to the domain
                    try:
                        domains[current_elset].add(en)
                    except KeyError:
                        domains[current_elset] = {en}
            else:
                pos = 0
                elm_2nd_line = False
            for nn in range(pos, pos + number_of_nodes - len(elm_category[en])):
                try:
                    enode = int(line_list[nn])
                    elm_category[en].append(enode)
                except(IndexError, ValueError):
                    elm_2nd_line = True
                    break

        # reading domains from elset
        elif line[:6].upper() == "*ELSET":
            line_split_comma = line.split(",")
            if "=" in line_split_comma[1]:
                name_member = 1
                try:
                    if "GENERATE" in line_split_comma[2].upper():
                        elset_generate = True
                except IndexError:
                    pass
            else:
                name_member = 2
                if "GENERATE" in line_split_comma[1].upper():
                    elset_generate = True
            member_split = line_split_comma[name_member].split("=")
            current_elset = member_split[1].strip()
            try:
                domains[current_elset]
            except KeyError:
                domains[current_elset] = set()
            if elset_generate is False:
                read_domain = True
        elif read_domain is True:
            for en in line.split(","):
                en = en.strip()
                if en.isdigit():
                    domains[current_elset].add(int(en))
                elif en.isalpha():  # else: en is name of a previous elset
                    domains[current_elset].update(domains[en])
        elif elset_generate is True:
            line_split_comma = line.split(",")
            try:
                if line_split_comma[3]:
                    en_generated = list(range(int(line_split_comma[0]), int(line_split_comma[1]) + 1,
                                              int(line_split_comma[2])))
            except IndexError:
                en_generated = list(range(int(line_split_comma[0]), int(line_split_comma[1]) + 1))
            domains[current_elset].update(en_generated)

        elif line[:5].upper() == "*STEP":
            model_definition = False
    f.close()

    msg = "\nNumber of recognized entities\n"
    msg += ("nodes  : %.f\nSEG2   : %.f\nSEG3   : %.f\nTRIA3  : %.f\nTRIA6  : %.f\nQUAD4  : %.f\nQUAD8  : %.f\n"
            "TETRA4 : %.f\nTETRA10: %.f\nHEXA8  : %.f\nHEXA20 : %.f\nPENTA6 : %.f\nPENTA15: %.f\n"
            % (len(nodes), len(Elements.seg2), len(Elements.seg3), len(Elements.tria3), len(Elements.tria6),
               len(Elements.quad4), len(Elements.quad8), len(Elements.tetra4), len(Elements.tetra10),
               len(Elements.hexa8), len(Elements.hexa20), len(Elements.penta6), len(Elements.penta15)))
    print(msg)
    return nodes, Elements


# reading integration point von Mises stresses and PEEQ from dat file
def import_int_pt(file_name):
    f = open(file_name + ".dat", "r")
    last_time_stress = "initial"
    last_time_peeq = "initial"
    time_stress = 0  # step time for von Mises stress
    time_peeq = 0  # step time for peeq
    von_Mises_step = {}  # dict of von Mises stresses in all analysis steps
                    #{time1: {en1: [int.pt.1, int.pt.2, ...], en2: [...], ...}, time2: {...}, ...}
    peeq_step = {}  # dict of PEEQ in all analysis steps, similar structure as von_Mises_step
    read_stresses = 0
    read_peeq = 0

    for line in f:
        line_split = line.split()
        if line.replace(" ", "") == "\n":
            if read_stresses == 1:
                von_Mises_step[time_stress][en_last] = list(von_Mises_int_pt)
            if read_peeq == 1:
                peeq_step[time_peeq][en_last] = list(peeq_int_pt)
            read_stresses -= 1
            read_peeq -= 1
            von_Mises_int_pt = []
            peeq_int_pt = []
            en_last = None

        elif line[:9] == " stresses":
            read_stresses = 2
            if last_time_stress != line_split[-1]:
                time_stress = float(line_split[-1])
                von_Mises_step[time_stress] = {}
                last_time_stress = line_split[-1]
        elif line[:26] == " equivalent plastic strain":
            read_peeq = 2
            if last_time_peeq != line_split[-1]:
                time_peeq = float(line_split[-1])
                peeq_step[time_peeq] = {}
                last_time_peeq = line_split[-1]

        elif read_stresses == 1:
            en = int(line_split[0])
            if en_last != en:
                if en_last:
                    von_Mises_step[time_stress][en_last] = list(von_Mises_int_pt)
                    von_Mises_int_pt = []
                en_last = en
            sxx = float(line_split[2])
            syy = float(line_split[3])
            szz = float(line_split[4])
            sxy = float(line_split[5])
            sxz = float(line_split[6])
            syz = float(line_split[7])
            von_Mises_int_pt.append(math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2
                                              + 6 * (sxy ** 2 + syz ** 2 + sxz ** 2))))

        elif read_peeq == 1:
            en = int(line_split[0])
            if en_last != en:
                if en_last:
                    peeq_step[time_peeq][en_last] = list(peeq_int_pt)
                    peeq_int_pt = []
                en_last = en
            peeq = float(line_split[2])
            peeq_int_pt.append(peeq)

    if read_stresses == 1:
        von_Mises_step[time_stress][en_last] = list(von_Mises_int_pt)
    if read_peeq == 1:
        peeq_step[time_peeq][en_last] = list(peeq_int_pt)
    f.close()
    return von_Mises_step, peeq_step


# sub-function to write vtk mesh
def vtk_mesh(file_name, nodes, Elements):
    f = open(file_name + "_int_pt.vtk", "w")
    f.write("# vtk DataFile Version 3.0\n")
    f.write("Integration point von Mises stresses and PEEQ from dat file on mesh from inp file.\n")
    f.write("ASCII\n")
    f.write("DATASET UNSTRUCTURED_GRID\n")

    # nodes
    associated_nodes = set()
    for nn_lists in (list(Elements.seg2.values()) + list(Elements.seg3.values()) + list(Elements.tria3.values())
                     + list(Elements.tria6.values()) + list(Elements.quad4.values()) + list(Elements.quad8.values())
                     + list(Elements.tetra4.values()) + list(Elements.tetra10.values()) + list(Elements.penta6.values())
                     + list(Elements.penta15.values()) + list(Elements.hexa8.values())
                     + list(Elements.hexa20.values())):
        associated_nodes.update(nn_lists)
    associated_nodes = sorted(associated_nodes)
    # node renumbering table for vtk format which does not jump over node numbers and contains only associated nodes
    nodes_vtk = [None for _ in range(max(nodes.keys()) + 1)]
    nn_vtk = 0
    for nn in associated_nodes:
        nodes_vtk[nn] = nn_vtk
        nn_vtk += 1

    f.write("\nPOINTS " + str(len(associated_nodes)) + " float\n")
    line_count = 0
    for nn in associated_nodes:
        f.write("{} {} {} ".format(nodes[nn][0], nodes[nn][1], nodes[nn][2]))
        line_count += 1
        if line_count % 2 == 0:
            f.write("\n")
    f.write("\n")

    # elements
    number_of_elements = (len(Elements.seg2) + len(Elements.seg3) + len(Elements.tria3) + len(Elements.tria6)
                          + len(Elements.quad4) + len(Elements.quad8) + len(Elements.tetra4) + len(Elements.tetra10)
                          + len(Elements.penta6) + len(Elements.penta15) + len(Elements.hexa8) + len(Elements.hexa20))
    en_all = (list(Elements.seg2.keys()) + list(Elements.seg3.keys()) + list(Elements.tria3.keys())
              + list(Elements.tria6.keys()) + list(Elements.quad4.keys()) + list(Elements.quad8.keys())
              + list(Elements.tetra4.keys()) + list(Elements.tetra10.keys()) + list(Elements.penta6.keys())
              + list(Elements.penta15.keys()) + list(Elements.hexa8.keys()) + list(Elements.hexa20.keys()))
              # defines vtk element numbering from 0

    size_of_cells = (3 * len(Elements.seg2) + 4 * len(Elements.seg3) + 4 * len(Elements.tria3)
                     + 7 * len(Elements.tria6) + 5 * len(Elements.quad4) + 9 * len(Elements.quad8)
                     + 5 * len(Elements.tetra4) + 11 * len(Elements.tetra10) + 7 * len(Elements.penta6)
                     + 16 * len(Elements.penta15) + 9 * len(Elements.hexa8) + 21 * len(Elements.hexa20))
    f.write("\nCELLS " + str(number_of_elements) + " " + str(size_of_cells) + "\n")

    def write_elm(elm_category, node_length):
        for en in elm_category:
            f.write(node_length)
            for nn in elm_category[en]:
                f.write(" " + str(nodes_vtk[nn]) + " ")
            f.write("\n")

    write_elm(Elements.seg2, "2")
    write_elm(Elements.seg3, "3")
    write_elm(Elements.tria3, "3")
    write_elm(Elements.tria6, "6")
    write_elm(Elements.quad4, "4")
    write_elm(Elements.quad8, "8")
    write_elm(Elements.tetra4, "4")
    write_elm(Elements.tetra10, "10")
    write_elm(Elements.penta6, "6")
    write_elm(Elements.penta15, "15")
    write_elm(Elements.hexa8, "8")
    write_elm(Elements.hexa20, "20")

    f.write("\nCELL_TYPES " + str(number_of_elements) + "\n")
    cell_types = ("3 " * len(Elements.seg2) + "21 " * len(Elements.seg3) + "5 " * len(Elements.tria3)
                  + "22 " * len(Elements.tria6) + "9 " * len(Elements.quad4) + "23 " * len(Elements.quad8)
                  + "10 " * len(Elements.tetra4) + "24 " * len(Elements.tetra10) + "13 " * len(Elements.penta6)
                  + "26 " * len(Elements.penta15) + "12 " * len(Elements.hexa8) + "25 " * len(Elements.hexa20))
    line_count = 0
    for char in cell_types:
        f.write(char)
        if char == " ":
            line_count += 1
            if line_count % 30 == 0:
                f.write("\n")
    f.write("\n")

    f.write("\nCELL_DATA " + str(number_of_elements) + "\n")

    f.close()
    return en_all


def append_vtk_scalars(file_name, en_all, von_Mises_step, peeq_step):
    f = open(file_name + "_int_pt.vtk", "a")

    # calculix element id
    f.write("\nSCALARS ccx_element_number float\n")
    f.write("LOOKUP_TABLE default\n")
    line_count = 0
    for en in en_all:
        f.write(str(en) + " ")
        line_count += 1
        if line_count % 30 == 0:
            f.write("\n")
    f.write("\n")

    def write_scalars(var_name, var):
        f.write("\nSCALARS " + var_name + " float\n")
        f.write("LOOKUP_TABLE default\n")
        line_count = 0
        for en in en_all:
            try:
                f.write(str(var[en]) + " ")
            except KeyError:  # write 0 when data are not defined for the element
                f.write("0 ")
            line_count += 1
            if line_count % 30 == 0:
                f.write("\n")
        f.write("\n")

    # von Mises stresses
    for t in von_Mises_step:
        von_Mises_int_pt_max = {}
        von_Mises_int_pt = {}
        for en in von_Mises_step[t]:
            von_Mises_int_pt_max[en] = max(von_Mises_step[t][en])
            for int_pt in range(len(von_Mises_step[t][en])):
                try:
                    von_Mises_int_pt[int_pt][en] = von_Mises_step[t][en][int_pt]
                except KeyError:
                    von_Mises_int_pt[int_pt] = {}
                    von_Mises_int_pt[int_pt][en] = von_Mises_step[t][en][int_pt]
        write_scalars("time" + str(t) + "_von_Mises_int_pt_max", von_Mises_int_pt_max)
        if write_all_integration_points:
            for int_pt in von_Mises_int_pt:
                write_scalars("time" + str(t) + "_von_Mises_int_pt_" + str(int_pt + 1), von_Mises_int_pt[int_pt])
    # again the same for PEEQ
    for t in peeq_step:
        peeq_int_pt_max = {}
        peeq_int_pt = {}
        for en in peeq_step[t]:
            peeq_int_pt_max[en] = max(peeq_step[t][en])
            for int_pt in range(len(peeq_step[t][en])):
                try:
                    peeq_int_pt[int_pt][en] = peeq_step[t][en][int_pt]
                except KeyError:
                    peeq_int_pt[int_pt] = {}
                    peeq_int_pt[int_pt][en] = peeq_step[t][en][int_pt]
        write_scalars("time" + str(t) + "_peeq_int_pt_max", peeq_int_pt_max)
        if write_all_integration_points:
            for int_pt in peeq_int_pt:
                write_scalars("time" + str(t) + "_peeq_int_pt_" + str(int_pt + 1), peeq_int_pt[int_pt])
    f.close()


# read mesh
[nodes, Elements] = import_inp(file_name)

# read integration point data
[von_Mises_step, peeq_step] = import_int_pt(file_name)

# vtk output
en_all = vtk_mesh(file_name, nodes, Elements)
append_vtk_scalars(file_name, en_all, von_Mises_step, peeq_step)
print(file_name + "_int_pt.vtk created")
