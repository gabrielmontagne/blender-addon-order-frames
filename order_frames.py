from os.path import split, join, splitext
from shutil import copy
import bpy
import os

class SEQUENCE_OT_order_frames(bpy.types.Operator):
    bl_idname = 'sequencer.order_frames'
    bl_label = "Order text images"
    bl_options = {'PRESET'}

    target_name: bpy.props.StringProperty(name="Target", default='ordered')

    @classmethod
    def poll(self, context):
        return bpy.data.filepath and len(context.selected_sequences)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        path, base = split(bpy.data.filepath)
        target_path = join(path, bpy.path.clean_name(self.target_name))
        os.makedirs(target_path, exist_ok=True)

        all_elements = []

        print('\n' * 3 + '-' * 5)

        for active_strip in context.selected_sequences:
            strip_directory = bpy.path.abspath(active_strip.directory)
            elements = active_strip.elements
            frame_offset_start = active_strip.frame_offset_start
            frame_final_start = active_strip.frame_final_start
            frame_final_duration = active_strip.frame_final_duration

            all_elements += [ 
                join(strip_directory, element.filename)
                for element in 
                elements[
                frame_offset_start:frame_final_duration + frame_offset_start]
            ]

        for i, element in enumerate(all_elements):
            extension = splitext(element)[1]
            print(copy(element, join(target_path, 'frame-{:08d}.{}'.format(i, extension))))

        # window_manager.progress_begin(0, len(elements_to_process))
        # print('elements_to_process', elements_to_process)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SEQUENCE_OT_order_frames)

def unregister():
    bpy.utils.unregister_class(SEQUENCE_OT_order_frames)

if __name__ == '__main__':
    register()
