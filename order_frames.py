from os.path import split, join, splitext
from shutil import copy
import bpy
import os
from bpy.path import relpath, clean_name, abspath

bl_info = {
    'name': "VSE: Order image sequences",
    'category': 'Development',
    'author': "Gabriel Montagné Láscaris-Comneno",
    'blender': (2, 80, 0)
}

class SEQUENCE_OT_order_frames(bpy.types.Operator):
    bl_idname = 'sequencer.order_frames'
    bl_label = "Order image sequences"
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
        target_path = join(path, clean_name(self.target_name))
        os.makedirs(target_path, exist_ok=True)

        all_elements = []

        print('\n' * 3 + '-' * 5)

        ordered_sequences = sorted(context.selected_sequences, key=lambda s: s.frame_final_start)

        for active_strip in ordered_sequences:
            strip_directory = abspath(active_strip.directory)
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
            file_name = 'frame-{:08d}{}'.format(i, extension)
            destination_path = join(target_path, file_name)
            copy(element, destination_path)

            if i == 0:
                first_strip = ordered_sequences[0]
                new_sequence_name = self.target_name + '.000'
                print('Creating new image sequence "{}"'.format(new_sequence_name))
                new_sequence = context.scene.sequence_editor.sequences.new_image(
                    name=new_sequence_name,
                    filepath=relpath(destination_path),
                    frame_start=first_strip.frame_final_start,
                    channel=active_strip.channel + 1)
            else:
                new_sequence.elements.append(file_name)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SEQUENCE_OT_order_frames)

def unregister():
    bpy.utils.unregister_class(SEQUENCE_OT_order_frames)

if __name__ == '__main__':
    register()
