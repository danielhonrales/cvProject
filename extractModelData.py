import os.path
from OpenGL.GL import *
from OpenGL.GLU import *

def extractModelData(filePath):
        
    basePath = filePath.removesuffix('.obj')
    #modelVerticesPath = basePath + "-vertices.txt"
    #modelTexturesPath = basePath + "-textures.txt"
    #modelNormalsPath = basePath + "-normals.txt"
    verticesPath = basePath + "-vertices.txt"
    vtPath = basePath + "-vt.txt"
    vn = basePath + "-vn.txt"
    vertexIndicesPath = basePath + "-vertexIndices.txt"
    uvIndicesPath = basePath + "-uvIndices.txt"
    normalIndicesPath = basePath + "-normalIndices.txt"
    
    vertices = []
    vt = []
    vn = []
    vertexIndices = []
    uvIndices = []
    normalIndices = []
    
    # Check if model info files exist
    if not os.path.isfile(verticesPath) or not os.path.isfile(vertexIndicesPath):
        
        # Create new model info files
        with open(filePath) as file:
            # Read through file
            for line in file:
                line = line.rstrip("\r\n")
                line = list(line.split(' '))
                type = line[0]
                
                # Add values to associated list
                if type == 'v':
                    values = [float(value) for value in line[1:]]
                    vertices.append(values)
                elif type == 'vn':
                    values = [float(value) for value in line[1:]]
                    vn.append(values)
                elif type == 'vt':
                    values = [float(value) for value in line[1:]]
                    vt.append(values)
                elif type == 'f':
                    indexGroups = line[1:]
                    faceVertexIndices = []
                    faceUvIndices = []
                    faceNormalIndices = []
                    for i in range(len(indexGroups)):
                        indices = [int(value) for value in list(indexGroups[i].split('/'))]
                        faceVertexIndices.append(indices[0])
                        faceUvIndices.append(indices[1])
                        faceNormalIndices.append(indices[2])
                    
                    vertexIndices.append(faceVertexIndices)
                    uvIndices.append(faceUvIndices)
                    normalIndices.append(faceNormalIndices)
                    
                    
        # Index faces
        #modelVertices = indexVertices(vertices, vertexIndices)
        #modelTextures = indexVertices(vt, uvIndices)
        #modelNormals = indexVertices(vn, normalIndices)
            
        # Write vertex and face file
        #writeListToFile(modelVerticesPath, modelVertices)
        #writeListToFile(modelTexturesPath, modelTextures)
        #writeListToFile(modelNormalsPath, modelNormals)
        writeListToFile(verticesPath, vertices)
        writeListToFile(vertexIndicesPath, vertexIndices) 
            
    else:
        # Read existing model info files
        #modelVertices = readFileToList(modelVerticesPath)
        #modelTextures = readFileToList(modelTexturesPath)
        #modelNormals = readFileToList(modelNormalsPath)
        vertices = readFileToList(verticesPath)
        vertexIndices = readFileToList(vertexIndicesPath, True)
        
    return vertices, vertexIndices

def indexVertices(vertices, indices):
    indexed = []
    for index in indices:
        indexed.append(vertices[index - 1]) # index starts at 1
    return indexed
 
def writeListToFile(filePath, list):
    with open(filePath, 'w+') as file:
        for line in list:
            file.write(f'{line}\n')

def readFileToList(filePath, index=False):
    outputList = []
    with open(filePath, 'r') as file:
        for line in file:
            values = list(line.strip('][\n').split(', '))
            if index:
                converted = [int(value) for value in values]
            else: 
                converted = [float(value) for value in values]
            outputList.append(converted)
    return outputList