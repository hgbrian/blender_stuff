import bpy, math, os, re, random

deg2rad = 2*math.pi/360.0
scn = bpy.context.scene
scn.render.alpha_mode = 'TRANSPARENT'
scn.cycles.film_transparent = True
scn.cursor_location = (0,0,0)

#--------------------------------------------------------------
# Delete everything for starting over
#

# Always try to start in OBJECT mode
if bpy.context.mode != "OBJECT":
    bpy.ops.object.mode_set(mode='OBJECT')

for obtype in ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER'):    
    bpy.ops.object.select_by_type(type=obtype)
    bpy.ops.object.delete()


#--------------------------------------------------------------
full_path_to_file = "/Users/briann/Dropbox/projects/blender_map/usmap.lores.example_colors.fixed.nobox.svg"
bpy.ops.import_curve.svg(filepath=full_path_to_file)

states = "Mississippi,Oklahoma,Wyoming,Minnesota,Illinois,Arkansas,New Mexico,Indiana,Maryland,Louisiana,Idaho,Tennessee,Arizona,Iowa,Michigan,Kansas,Utah,Virginia,Oregon,Connecticut,Montana,New Hampshire,Massachusetts,West Virginia,South Carolina,California,Wisconsin,Vermont,Georgia,North Dakota,Pennsylvania,Florida,Hawaii,Kentucky,Alaska,Nebraska,Missouri,Ohio,Alabama,Rhode Island,South Dakota,Colorado,New Jersey,Washington,North Carolina,New York,District of Columbia,Texas,Nevada,Delaware,Maine".split(',')

#--------------------------------------------------------------
# Materials
def make_materials_img():
  mats = {}
  for state in states:
    imgpath = os.path.expanduser('/Users/briann/Downloads/red.png')
    tex = bpy.data.textures.new('ColorTex', type = 'IMAGE')
    tex.image = bpy.data.images.load(imgpath)
    
    mat = bpy.data.materials.new('TexMat')
    #mat.use_shadeless = True # bad
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    #mtex.use_map_color_diffuse = True 
    mats[state] = mat
  return mats

def make_color(name, diffuse, specular, alpha):
  mat = bpy.data.materials.new(name)
  mat.diffuse_color = diffuse
  mat.diffuse_shader = 'LAMBERT' 
  mat.diffuse_intensity = 1.0 
  mat.specular_color = specular
  mat.specular_shader = 'COOKTORR'
  mat.specular_intensity = 0.5
  mat.alpha = 0
  mat.ambient = 1
  return mat

def make_materials(colors):
  mats = {}
  alpha = {"Hawaii":0, "Alaska":0}
  for state in states:
    mats[state] = make_color(state, colors[state], (.5,.5,.5), 1)
  return mats


#--------------------------------------------------------------
def make_camera():
  bpy.ops.object.lamp_add(type="POINT", radius=1, location=(-1,1,2))
  ob = bpy.context.object
  ob.name = "light1"
  ob.data.shadow_method = 'RAY_SHADOW'
  ob.data.shadow_soft_size = 3
  ob.data.shadow_ray_samples = 15

  bpy.ops.object.lamp_add(type="POINT", radius=1, location=(-.5,.5,1))
  ob = bpy.context.object
  ob.name = "light2"
  ob.data.shadow_method = 'RAY_SHADOW'
  ob.data.shadow_soft_size = 3
  ob.data.shadow_ray_samples = 15

  bpy.ops.object.camera_add(location=(.5,-.25,2), rotation=(0*deg2rad,0,0))
  ob = bpy.context.object
  ob.name = 'camera1'
  bpy.context.scene.camera = ob


#--------------------------------------------------------------
def make_map(inExtrd, textob, hide_ah=True):
  bpy.ops.object.select_all(action='DESELECT')
  n = 0
  for ob in bpy.data.objects:
    if re.match(r'^Curve', ob.name): # curve object
      try: state = states[n]
      except: print("ERROR", ob.name)
      
      n += 1
      ob.select = True
      if hide_ah and state in ("Alaska", "Hawaii"):
          ob.hide_render = True
      ob.data.dimensions = '2D'
      ob.data.splines[0].use_cyclic_u = True
      ob.data.extrude = .01 + random.random()*.004 #data[state]*.01
      ob.data.materials.append(mats[state])
  
  bpy.context.scene.cursor_location = (0,0,0)
  bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  bpy.ops.transform.translate(value=(0,0,.01/2))
  bpy.ops.transform.resize(value=(3.75,3.75,3)) #, constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
  if textob: textob.select = True
  bpy.ops.transform.rotate(value=-30*deg2rad, axis=(1,0,0))

#--------------------------------------------------------------
# Text
def make_text(txt):
  bpy.ops.object.select_all(action='DESELECT')
  bpy.ops.object.text_add(location=(0,0,0)) 
  ob = bpy.context.object
  ob.data.body = txt
  ob.data.extrude = .1
  bpy.ops.object.convert(target='MESH', keep_original=False)

  mat = make_color("black", (.3, .3, .3), (.5, .5, .5), 1)
  ob.data.materials.append(mat)

  bpy.ops.transform.resize(value=(.13, .13, .13))
  bpy.ops.transform.rotate(axis=(1,0,0), value=45*deg2rad  )
  bpy.ops.transform.translate(value=(0.1,-.3,.05) )

  return ob
#--------------------------------------------------------------

colors = {}
data = {}
for state in states:
    data[state] = random.random()*.5
    colors[state] = (.95, .95, .95)

make_camera()
mats = make_materials(colors)
#textob = make_text("733 biobanks")
make_map(data, None)

