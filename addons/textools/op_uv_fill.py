import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv
from . import utilities_ui

class op(bpy.types.Operator):
	bl_idname = "uv.textools_uv_fill"
	bl_label = "Fill"
	bl_description = "Fill UV selection to UV canvas"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		
		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True
	
	def execute(self, context):
		fill(self, context)
		return {'FINISHED'}



def fill(self, context):
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uv_layer = bm.loops.layers.uv.verify();


	# 1.) Rotate minimal bounds (less than 45 degrees rotation)
	# 2.) Match width and height to UV bounds


	boundsAll = utilities_uv.getSelectionBBox()


	islands = utilities_uv.getSelectionIslands()
	allSizes = {}	#https://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
	allBounds = {}

	print("Islands: "+str(len(islands))+"x")

	bpy.context.window_manager.progress_begin(0, len(islands))

	#Rotate to minimal bounds
	for i in range(0, len(islands)):
		alignIslandMinimalBounds(uv_layer, islands[i])

		# Collect BBox sizes
		bounds = utilities_uv.getSelectionBBox()
		allSizes[i] = max(bounds['width'], bounds['height']) + i*0.000001;#Make each size unique
		allBounds[i] = bounds;
		print("Rotate compact:  "+str(allSizes[i]))

		bpy.context.window_manager.progress_update(i)












	print("Fill ")



def alignIslandMinimalBounds(uv_layer, faces):
	# Select Island
	bpy.ops.uv.select_all(action='DESELECT')
	utilities_uv.set_selected_faces(faces)

	steps = 8
	angle = 45;	# Starting Angle, half each step

	bboxPrevious = utilities_uv.getSelectionBBox()

	for i in range(0, steps):
		# Rotate right
		bpy.ops.transform.rotate(value=(angle * math.pi / 180), axis=(0, 0, 1))
		bbox = utilities_uv.getSelectionBBox()

		if i == 0:
			sizeA = bboxPrevious['width'] * bboxPrevious['height']
			sizeB = bbox['width'] * bbox['height']
			if abs(bbox['width'] - bbox['height']) <= 0.0001 and sizeA < sizeB:
				# print("Already squared")
				bpy.ops.transform.rotate(value=(-angle * math.pi / 180), axis=(0, 0, 1))
				break;


		if bbox['minLength'] < bboxPrevious['minLength']:
			bboxPrevious = bbox;	# Success
		else:
			# Rotate Left
			bpy.ops.transform.rotate(value=(-angle*2 * math.pi / 180), axis=(0, 0, 1))
			bbox = utilities_uv.getSelectionBBox()
			if bbox['minLength'] < bboxPrevious['minLength']:
				bboxPrevious = bbox;	# Success
			else:
				# Restore angle of this iteration
				bpy.ops.transform.rotate(value=(angle * math.pi / 180), axis=(0, 0, 1))

		angle = angle / 2

	if bboxPrevious['width'] < bboxPrevious['height']:
		bpy.ops.transform.rotate(value=(90 * math.pi / 180), axis=(0, 0, 1))