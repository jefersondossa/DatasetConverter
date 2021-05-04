"""
Created on Mon May 3 2021

@author: jefersondossa
"""

# This program reads a .vtu file (converted from a .GRDECL dataset) and
# extracts the boundary information to write a .geo file and generate 
# a new mesh in Gmsh.

import numpy as np
import collections

fileVTU = 'SPE9.vtu'
#fileVTU = 'IRAP_1005.vtu'

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

# Maps Vertex and Edge nodes
for i in range(numNodes):
    if (len(InvIncidence[i]) == 1): VertexNodes.append(i)
    if (len(InvIncidence[i]) == 2): EdgeNodes.append(i)

#Writing .GEO file
GEO = open('file.geo','w')
GEO.write('size = 1.0;\n')

countPoints = 0
#Vertex Points
for i in range(len(VertexNodes)):
    node = VertexNodes[i]  
    GEO.write('Point(' + str(countPoints) + ') = {' + \
              str(Coordinates[node,0]) + ', ' + str(Coordinates[node,1]) + \
              ', ' + str(Coordinates[node,2]) + ', size};\n')
    countPoints += 1
#Edge Points
for i in range(len(EdgeNodes)):
    node = EdgeNodes[i]  
    GEO.write('Point(' + str(countPoints) + ') = {' + \
              str(Coordinates[node,0]) + ', ' + str(Coordinates[node,1]) + \
              ', ' + str(Coordinates[node,2]) + ', size};\n')
    countPoints += 1

#Lines - Always connect two vertex, passing through the edge nodes
countLines = 0
auxLines = collections.defaultdict(list)

#for i in range(len(VertexNodes)):
##    GEO.write('Spline(' + str(countPoints) + ') = {')
#    auxLines[countLines].append(VertexNodes[i])
#   
#    for j in range(8):
#        neighborNode = Connectivity[InvIncidence[VertexNodes[i]],j][0]
#        el = InvIncidence[VertexNodes[i]][0]
#        if (len(InvIncidence[neighborNode]) == 2):
#            for k in range(len(InvIncidence[neighborNode])):
#                if InvIncidence[neighborNode][k] in EdgeNodes:
#                    a = int(EdgeNodes.index(InvIncidence[neighborNode][k]))
#                    print("AAA", a)    
#            
#    print(auxLines[countLines])
#    countLines += 1
#    
#    
    
    
    
    
    
    
    


