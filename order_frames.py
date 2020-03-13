import bpy



class SEQUENCE_OT_order_frames(bpy.types.Operator):
    bl_idname = 'sequencer.order_frames'
    bl_label = "Order text images"
    bl_options = {'PRESET'}

    target_name: bpy.props.StringProperty(name="Target", default='ordered')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        print('tons? target {}'.format(self.target_name))
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SEQUENCE_OT_order_frames)

def unregister():
    bpy.utils.unregister_class(SEQUENCE_OT_order_frames)

if __name__ == '__main__':
    register()
