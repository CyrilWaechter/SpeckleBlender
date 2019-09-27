import bpy, bmesh, struct
from bpy_speckle.util import find_key_case_insensitive

def add_vertices(smesh, bmesh, scale=1.0):
    
    sverts = find_key_case_insensitive(smesh, "vertices")

    if sverts:
        if len(sverts) > 0:
            for i in range(0, len(sverts), 3):
                bmesh.verts.new((float(sverts[i]) * scale, float(sverts[i + 1]) * scale, float(sverts[i + 2]) * scale))  
        
    bmesh.verts.ensure_lookup_table()  

def add_faces(smesh, bmesh):
    
    sfaces = find_key_case_insensitive(smesh, "faces")

    if sfaces:
        if len(sfaces) > 0:
            i = 0
            while (i < len(sfaces)):
                if (sfaces[i] == 0):
                    i += 1
                    f = bmesh.faces.new((bmesh.verts[int(sfaces[i])], bmesh.verts[int(sfaces[i + 1])], bmesh.verts[int(sfaces[i + 2])]))
                    f.smooth = True
                    i += 3
                elif (sfaces[i] == 1):
                    i += 1
                    f = bmesh.faces.new((bmesh.verts[int(sfaces[i])], bmesh.verts[int(sfaces[i + 1])], bmesh.verts[int(sfaces[i + 2])], bmesh.verts[int(sfaces[i + 3])]))
                    f.smooth = True
                    i += 4
                else:
                    print("Invalid face length.\n" + str(sfaces[i]))
                    break   
            
            bmesh.faces.ensure_lookup_table()
            bmesh.verts.index_update()     

def add_colors(smesh, bmesh):

    colors = []
    scolors = find_key_case_insensitive(smesh, "colors")

    if scolors:
        if len(scolors) > 0:

            for i in range(0, len(scolors)):
                col = int(scolors[i])
                (a, r, g, b) = [int(x) for x in struct.unpack("!BBBB", struct.pack("!i", col))]
                colors.append((float(r) / 255.0, float(g) / 255.0, float(b) / 255.0, float(a) / 255.0)) 

        # Make vertex colors
        if len(scolors) == len(bmesh.verts):
            color_layer = bmesh.loops.layers.color.new("Col")

            for face in bmesh.faces:
                for loop in face.loops:
                    loop[color_layer] = colors[loop.vert.index]

def add_uv_coords(smesh, bmesh):

    sprops = find_key_case_insensitive(smesh, "properties")
    if sprops:
        texKey = ""
        if 'texture_coordinates' in sprops.keys():
            texKey = 'texture_coordinates'
        elif 'TextureCoordinates' in sprops.keys():
            texKey = "TextureCoordinates"

        if texKey != "":

            try:
                decoded = base64.b64decode(sprops[texKey]).decode("utf-8")
                s_uvs = decoded.split()
                  
                if int(len(s_uvs) / 2) == len(bmesh.verts):
                    for i in range(0, len(s_uvs), 2):
                        uv.append((float(s_uvs[i]), float(s_uvs[i+1])))
                else:
                    print (len(s_uvs) * 2)
                    print (len(bmesh.verts))
                    print ("Failed to match UV coordinates to vert data.")
            except:
                pass

            del smesh['properties'][texKey]


def to_bmesh(speckle_mesh, blender_mesh, name="SpeckleMesh", scale=1.0):

    bm = bmesh.new()

    add_vertices(speckle_mesh, bm, scale)
    add_faces(speckle_mesh, bm)
    add_colors(speckle_mesh, bm)
    add_uv_coords(speckle_mesh, bm)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(blender_mesh)
    bm.free()

    return blender_mesh


def import_mesh(speckle_mesh, scale=1.0, name=None):
    if not name:
        name = speckle_mesh.get("geometryHash")
        if not name:
            name = speckle_mesh['_id']

    if name in bpy.data.meshes.keys():
        mesh = bpy.data.meshes[name]
    else:
        mesh = bpy.data.meshes.new(name=name)

    to_bmesh(speckle_mesh, mesh, name, scale)

    return mesh
