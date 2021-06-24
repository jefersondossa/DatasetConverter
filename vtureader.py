"""
Created on Mon May 3 2021

@author: jefersondossa
"""

# This program reads a .vtu file (converted from a .GRDECL dataset) and
# extracts the boundary information to write a .geo file and generate 
# a new mesh in Gmsh.

import numpy as np
import collections

#fileVTU = 'SPE9.vtu'
fileVTU = 'IRAP_1005.vtu'

VTU = open(fileVTU)
numElements = 0
numNodes = 0

# Reads VTU file and stores node and connectivity information
for line in VTU:
    if line.startswith('    <Piece'):
        a = line.split('\"')
        numElements = int(a[1])
        numNodes = int(a[3])
        Coordinates = np.zeros((numNodes*3), dtype=np.double)
        Connectivity = np.zeros((numElements*8), dtype=np.int)
    if 'Coordinates' in line:
        line = next(VTU)
        count = 0
        while True:
            if '/DataArray' in line:
                break
            else:
                a = line.split()
                for j in range(len(a)):
                    Coordinates[12*count+j] = float(a[j])
                count += 1
            line = next(VTU)
    if 'connectivity' in line:
        line = next(VTU)
        count = 0
        while True:
            if '/DataArray' in line:
                break
            else:
                a = line.split()
                for j in range(len(a)):
                    Connectivity[12*count+j] = int(a[j])
                count += 1
            line = next(VTU)

Connectivity = np.reshape(Connectivity, (-1, 8))
Coordinates = np.reshape(Coordinates, (-1, 3))
InvIncidence = collections.defaultdict(list)

# Inverse Incidence
for i in range(numElements):
    for j in range(8):
        InvIncidence[Connectivity[i,j]].append(i)

VertexNodes = []
EdgeNodes = []
VertexElements = []

# Maps Vertex and Edge nodes
for i in range(numNodes):
    if (len(InvIncidence[i]) == 1): VertexNodes.append(i)
    if (len(InvIncidence[i]) == 2): EdgeNodes.append(i)

#Writing .GEO file
GEO = open('file.geo','w')
GEO.write('size = 1.0;\n')

#Vertex Points
for i in range(len(VertexNodes)):
    node = VertexNodes[i]
    VertexElements.append(InvIncidence[VertexNodes[i]])
    GEO.write('Point(' + str(node) + ') = {' + \
              str(Coordinates[node,0]) + ', ' + str(Coordinates[node,1]) + \
              ', ' + str(Coordinates[node,2]) + ', size};\n')
#Edge Points
for i in range(len(EdgeNodes)):
    node = EdgeNodes[i]  
    GEO.write('Point(' + str(node) + ') = {' + \
              str(Coordinates[node,0]) + ', ' + str(Coordinates[node,1]) + \
              ', ' + str(Coordinates[node,2]) + ', size};\n')

#Lines - Always connect two vertex, passing through the edge nodes
countLines = 0
auxLines = collections.defaultdict(list)
for i in range(len(VertexNodes)):
    elVertex = InvIncidence[VertexNodes[i]]
#    print("i",i)
    for j in range(8):
#        print("j",j)
        neighborNode = Connectivity[elVertex,j][0]
        el = elVertex
        if ((len(InvIncidence[neighborNode]) == 2) or \
            (len(InvIncidence[neighborNode]) == 1)) and \
            (neighborNode != VertexNodes[i]):
            auxLines[countLines].append(VertexNodes[i])
            auxLines[countLines].append(neighborNode)
            count = 0
            while not (neighborNode in VertexNodes) and count < 62000:
                count += 1
#                print("while",i,j,neighborNode,count)
                neighborNodePrev = neighborNode
                elNeighbor = list(set(InvIncidence[neighborNodePrev])-set(el))
                el = elNeighbor
                if len(elNeighbor) == 0: break
                if (el in VertexElements):
                    aux = list(set(Connectivity[elNeighbor[0],:]) & \
                               set(VertexNodes))
                    auxLines[countLines].append(aux[0])
                    break;
                else:
                    for k in range(8):
                        neighborNode = Connectivity[elNeighbor[0],k]
                        if ((len(InvIncidence[neighborNode]) == 2) or \
                            (len(InvIncidence[neighborNode]) == 1)) and \
                            (not neighborNode in auxLines[countLines]):
                                auxLines[countLines].append(neighborNode)
                                break
            countLines += 1

#Verify duplicate lines
dupLines = np.zeros(len(auxLines), dtype=np.int)
for i in range(len(auxLines)):
    for j in range(i+1,len(auxLines),1):
        if len(list(set(auxLines[i])-set(auxLines[j]))) == 0:
            dupLines[i] = j

#Write lines in .geo file        
for i in range(len(auxLines)):
    if (dupLines[i] == 0):
        GEO.write('Line(' + str(i) + ') = {' + str(auxLines[i][0]))
        for k in range(1,len(auxLines[i]),1):
            GEO.write(', ' + str(auxLines[i][k]))    
        GEO.write('};\n')

    
    
    
    
    
    
    


