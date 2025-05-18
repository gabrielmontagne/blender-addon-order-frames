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

version_file = 'VERSION.txt'

class SEQUENCE_OT_order_frames(bpy.types.Operator):
    bl_idname = 'sequencer.order_frames'
    bl_label = "Order image sequences"
    bl_options = {'PRESET'}

    target_name: bpy.props.StringProperty(name="Target", default='ordered')
    pad_with_copies: bpy.props.BoolProperty(name="Padd with properties", default=True)

    @classmethod
    def poll(self, context):
        return bpy.data.filepath and context.selected_sequences and len(context.selected_sequences)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        path, base = split(bpy.data.filepath)

        filepath = bpy.data.filepath
        base_dir = os.path.dirname(filepath)

        version_path = os.path.join(base_dir, version_file)
        version = None
        if os.path.isfile(os.path.join(base_dir, version_path)):
            version = open(version_path, 'r').read().strip()

        if version:
            target_path = join(path, clean_name(self.target_name), version)
        else:
            target_path = join(path, clean_name(self.target_name))

        os.makedirs(target_path, exist_ok=True)

        all_elements = []

        ordered_sequences = sorted(context.selected_sequences, key=lambda s: s.frame_final_start)

        for active_strip in ordered_sequences:
            strip_directory = abspath(active_strip.directory)
            elements = active_strip.elements
            frame_offset_start = int(active_strip.frame_offset_start)
            frame_final_start = int(active_strip.frame_final_start)
            frame_final_duration = int(active_strip.frame_final_duration)

            first_selection_index = frame_offset_start
            final_selection_index = frame_final_duration + frame_offset_start

            selected_elements = elements[ first_selection_index : final_selection_index ]

            if self.pad_with_copies:

                target_length = final_selection_index - first_selection_index
                current_length = len(selected_elements)

                missing_length = target_length - current_length

                if missing_length > 0:
                    pad = [selected_elements[-1]] * missing_length
                    selected_elements += pad

            all_elements += [ join(strip_directory, element.filename) for element in selected_elements ]

        wm = context.window_manager
        wm.progress_begin(0, len(all_elements))

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

            wm.progress_update(i)

        wm.progress_end()

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SEQUENCE_OT_order_frames)

def unregister():
    bpy.utils.unregister_class(SEQUENCE_OT_order_frames)

if __name__ == '__main__':
    register()
