import os
import bpy
import bpy.utils.previews
from bpy.types import Panel, Operator

bl_info = {
    "name": "PainterlifyDEMO",
    "blender": (4, 2, 1),
    "category": "Compositing",
    "location": "Compositing > PainterlyDEMO",
    "version": (1, 0, 0),
    "author": "Kent Edoloverio",
    "description": "Adds Paint Overlay effect into compositing node",
    "wiki_url": "",
    "tracker_url": "",
}


class Painterly(Operator):
    bl_idname = "compnode.painterlyeffect"
    bl_label = "Painterlify"

    def __init__(self):
        self.source_file = os.path.join(os.path.dirname(
            __file__), "..", "PainterlifyDEMO/data", "PainterlyDEMO.blend")

    def import_file(self):
        if not os.path.isfile(self.source_file):
            self.report(
                {'ERROR'}, "File not found: {}".format(self.source_file))
            return {'CANCELLED'}
        return {'FINISHED'}

    def import_node_group(self, node_group_name):
        with bpy.data.libraries.load(self.source_file, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]

        if not data_to.node_groups or not data_to.node_groups[0]:
            self.report(
                {'ERROR'}, "Failed to load the node group: {}".format(node_group_name))
            return {'CANCELLED'}

        self.report(
            {'INFO'}, "Successfully appended node group: {}".format(node_group_name))
        return {'FINISHED'}

    def ensure_use_nodes(self):
        scene = bpy.context.scene
        if not scene.node_tree:
            scene.use_nodes = True
            if not scene.node_tree:
                self.report({'ERROR'}, "Failed to create node tree.")
                return {'CANCELLED'}
        elif not scene.node_tree.nodes:
            scene.use_nodes = True

        return {'FINISHED'}

    def add_node_group_to_compositing(self, node_group_name):
        scene = bpy.context.scene
        node_tree = scene.node_tree
        if not node_tree:
            self.report({'ERROR'}, "No compositing node tree found.")
            return {'CANCELLED'}

        render_layers_node = None
        composite_node = None

        for node in node_tree.nodes:
            if node.type == 'COMPOSITE':
                composite_node = node
            elif node.type == 'R_LAYERS':
                render_layers_node = node

        if not render_layers_node:
            self.report({'ERROR'}, "Render Layers node not found.")
            return {'CANCELLED'}

        if not composite_node:
            composite_node = node_tree.nodes.new(
                type='CompositorNodeComposite')
            composite_node.location = (400, 0)

        if node_group_name not in bpy.data.node_groups:
            self.report(
                {'ERROR'}, "Node group not found in current blend data.")
            return {'CANCELLED'}

        node_group = bpy.data.node_groups[node_group_name]
        if not node_group:
            self.report(
                {'ERROR'}, "Node group not found: {}".format(node_group_name))
            return {'CANCELLED'}

        painterly_node = node_tree.nodes.new(type='CompositorNodeGroup')
        painterly_node.node_tree = node_group
        painterly_node.location = (200, 0)

        node_tree.links.new(
            render_layers_node.outputs['Image'], painterly_node.inputs[0])
        node_tree.links.new(
            painterly_node.outputs[0], composite_node.inputs[0])

        self.report({'INFO'}, "Node group and connections added to compositing node tree: {}".format(
            node_group_name))
        return {'FINISHED'}

    def execute(self, context):
        if self.import_file() == {'CANCELLED'}:
            return {'CANCELLED'}

        if self.import_node_group("PainterlyDEMO") == {'CANCELLED'}:
            return {'CANCELLED'}

        if self.ensure_use_nodes() == {'CANCELLED'}:
            return {'CANCELLED'}

        if self.add_node_group_to_compositing("PainterlyDEMO") == {'CANCELLED'}:
            return {'CANCELLED'}

        return {'FINISHED'}


class PainterlyPanel(Panel):
    bl_idname = "NODE_PT_painterly"
    bl_label = "Painterly"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Painterly'

    def draw(self, context):
        pcoll = icon_preview["main"]
        kofi = pcoll["kofi"]
        deviant = pcoll["deviant"]
        github = pcoll["github"]

        layout = self.layout

        col = layout.row(align=False)
        col.enabled = True
        col.scale_x = 2.0
        col.scale_y = 2.0
        col.operator("compnode.painterlyeffect")

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        kofi = box.operator(
            'wm.url_open',
            text='KO-FI',
            icon_value=kofi.icon_id,
            emboss=False
        )
        kofi.url = 'https://ko-fi.com/kents_workof_art'

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        deviant = box.operator(
            'wm.url_open',
            text='DEVIANT ART',
            icon_value=deviant.icon_id,
            emboss=False
        )
        deviant.url = 'https://www.deviantart.com/kents001'

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        github = box.operator(
            'wm.url_open',
            text='GITHUB',
            icon_value=github.icon_id,
            emboss=False
        )
        github.url = 'https://github.com/kents00'


icon_preview = {}

classes = (
    Painterly,
    PainterlyPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    pcoll = bpy.utils.previews.new()

    absolute_path = os.path.join(os.path.dirname(__file__), 'data/')
    relative_path = "icons"
    path = os.path.join(absolute_path, relative_path)
    pcoll.load("kofi", os.path.join(path, "kofi.png"), 'IMAGE')
    pcoll.load("deviant", os.path.join(path, "deviantart.png"), 'IMAGE')
    pcoll.load("github", os.path.join(path, "github.png"), 'IMAGE')
    icon_preview["main"] = pcoll


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.utils.previews.remove(icon_preview["main"])


if __name__ == "__main__":
    register()
