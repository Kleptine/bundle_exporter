import bpy
import json
import math
from mathutils import Vector, Matrix, Quaternion

from . import modifier


# Maximum size for custom property JSON (conservative limit)
MAX_CUSTOM_PROPERTY_SIZE = 65536  # 64KB


def vector_to_list(v):
    """Convert a Blender Vector to a list, rounding to reduce JSON size."""
    return [round(v.x, 6), round(v.y, 6), round(v.z, 6)]


def quat_to_list(q):
    """Convert a Blender Quaternion to a list [x, y, z, w]."""
    return [round(q.x, 6), round(q.y, 6), round(q.z, 6), round(q.w, 6)]


def transform_point_z_to_y_up(point):
    """Convert from Blender Z-up to Unity Y-up coordinate system.

    Blender: X-right, Y-forward, Z-up
    Unity:   X-right, Y-up, Z-forward
    Transform: (x, y, z) -> (x, z, -y)
    """
    return Vector((point.x, point.z, -point.y))


def transform_quat_z_to_y_up(quat):
    """Convert quaternion from Z-up to Y-up coordinate system."""
    # Rotation matrix for the coordinate change
    # This rotates -90 degrees around X axis
    coord_change = Quaternion((1, 0, 0), math.radians(-90))
    return coord_change @ quat


def compute_knot_rotation(tangent_out, tilt):
    """Compute a quaternion rotation for a knot given its outgoing tangent and tilt.

    The rotation orients the knot so that:
    - The forward direction (Z in Unity) aligns with the tangent
    - The tilt rotates around that forward axis
    """
    if tangent_out.length < 0.0001:
        # Degenerate case - use identity
        return Quaternion()

    forward = tangent_out.normalized()

    # Find a suitable up vector (prefer world Z, unless tangent is parallel)
    world_up = Vector((0, 0, 1))
    if abs(forward.dot(world_up)) > 0.999:
        world_up = Vector((0, 1, 0))

    # Compute right and corrected up
    right = forward.cross(world_up).normalized()
    up = right.cross(forward).normalized()

    # Build rotation matrix
    rot_matrix = Matrix((
        (right.x, up.x, forward.x),
        (right.y, up.y, forward.y),
        (right.z, up.z, forward.z)
    ))

    base_quat = rot_matrix.to_quaternion()

    # Apply tilt as rotation around the forward axis
    if abs(tilt) > 0.0001:
        tilt_quat = Quaternion(forward, tilt)
        base_quat = tilt_quat @ base_quat

    return base_quat


def extract_bezier_spline(spline, matrix_world, pivot, use_y_up):
    """Extract data from a Bezier spline."""
    knots = []

    for bp in spline.bezier_points:
        # Transform positions to world space
        co_world = matrix_world @ bp.co
        handle_left_world = matrix_world @ bp.handle_left
        handle_right_world = matrix_world @ bp.handle_right

        # Apply pivot offset
        co_world -= pivot
        handle_left_world -= pivot
        handle_right_world -= pivot

        # Compute tangents relative to knot position
        tangent_in = handle_left_world - co_world
        tangent_out = handle_right_world - co_world

        # Compute rotation from tangent and tilt
        rotation = compute_knot_rotation(tangent_out, bp.tilt)

        # Convert to Y-up if needed
        if use_y_up:
            co_world = transform_point_z_to_y_up(co_world)
            tangent_in = transform_point_z_to_y_up(tangent_in)
            tangent_out = transform_point_z_to_y_up(tangent_out)
            rotation = transform_quat_z_to_y_up(rotation)

        knots.append({
            "position": vector_to_list(co_world),
            "tangentIn": vector_to_list(tangent_in),
            "tangentOut": vector_to_list(tangent_out),
            "rotation": quat_to_list(rotation),
        })

    return {
        "type": "bezier",
        "closed": spline.use_cyclic_u,
        "knots": knots
    }


def extract_nurbs_spline(spline, matrix_world, pivot, use_y_up):
    """Extract data from a NURBS spline.

    Unity Splines doesn't have native NURBS support, so we store
    the raw control points and NURBS parameters for custom handling.
    """
    knots = []

    for point in spline.points:
        # NURBS points have 4 components (x, y, z, w) where w is the homogeneous coordinate
        co = Vector((point.co.x, point.co.y, point.co.z))
        co_world = matrix_world @ co
        co_world -= pivot

        if use_y_up:
            co_world = transform_point_z_to_y_up(co_world)

        knots.append({
            "position": vector_to_list(co_world),
            "weight": round(point.co.w, 6),  # NURBS weight (homogeneous coord)
        })

    return {
        "type": "nurbs",
        "closed": spline.use_cyclic_u,
        "order": spline.order_u,
        "knots": knots
    }


def extract_poly_spline(spline, matrix_world, pivot, use_y_up):
    """Extract data from a Poly spline (linear segments)."""
    knots = []

    for point in spline.points:
        co = Vector((point.co.x, point.co.y, point.co.z))
        co_world = matrix_world @ co
        co_world -= pivot

        if use_y_up:
            co_world = transform_point_z_to_y_up(co_world)

        knots.append({
            "position": vector_to_list(co_world),
        })

    return {
        "type": "linear",
        "closed": spline.use_cyclic_u,
        "knots": knots
    }


def extract_curve_data(curve_obj, pivot, use_y_up):
    """Extract all spline data from a curve object."""
    curve_data = curve_obj.data
    matrix_world = curve_obj.matrix_world.copy()

    splines = []
    for spline in curve_data.splines:
        if spline.type == 'BEZIER':
            splines.append(extract_bezier_spline(spline, matrix_world, pivot, use_y_up))
        elif spline.type == 'NURBS':
            splines.append(extract_nurbs_spline(spline, matrix_world, pivot, use_y_up))
        elif spline.type == 'POLY':
            splines.append(extract_poly_spline(spline, matrix_world, pivot, use_y_up))

    return {
        "splines": splines,
        "dimensions": curve_data.dimensions,  # '2D' or '3D'
        "resolution": curve_data.resolution_u,
    }


class BGE_mod_export_curves(modifier.BGE_mod_default):
    label = "Export Curves as Custom Properties"
    id = 'export_curves'
    type = 'GENERAL'
    icon = 'CURVE_DATA'
    priority = 100  # Run early, before other processing
    tooltip = 'Exports curve/spline data as JSON custom properties for Unity Spline Package'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    property_name: bpy.props.StringProperty(
        name="Property Name",
        default="spline_data",
        description="Name of the custom property to store spline data"
    )

    def _draw_info(self, layout, modifier_bundle_index):
        layout.prop(self, "property_name", text="Property")

        # Show info about curves in current bundle if available
        from ..bundles import get_bundles
        bundles = get_bundles()
        if modifier_bundle_index >= 0 and modifier_bundle_index < len(bundles):
            bundle = bundles[modifier_bundle_index]
            curves = [obj for obj in bundle.objects if obj.type == 'CURVE']
            if curves:
                layout.label(text=f"Curves in bundle: {len(curves)}")

    def _warning(self):
        """Show warning if export_extras might not be enabled."""
        # We can't easily check the preset here, so just return False
        # The actual check happens during process()
        return False

    def _check_export_extras(self, bundle_info):
        """Check if custom properties export is enabled in the export preset.

        Different exporters use different property names:
        - GLTF/GLB: export_extras
        - FBX: use_custom_props
        - OBJ: No custom property support
        - COLLADA: No custom property support
        """
        preset = bundle_info.get('export_preset', {})
        export_format = bundle_info.get('export_format', '')

        # Check format-specific property
        if export_format in ('GLTF', 'GLB'):
            return preset.get('export_extras', False)
        elif export_format == 'FBX':
            return preset.get('use_custom_props', False)
        elif export_format in ('OBJ', 'COLLADA'):
            # These formats don't support custom properties
            return False

        # Fallback: check both properties
        return preset.get('export_extras', False) or preset.get('use_custom_props', False)

    def process(self, bundle_info):
        # Find curves in the bundle
        # Curves are in 'meshes' because CURVE is in mesh_types
        all_objects = bundle_info['meshes'] + bundle_info['empties'] + bundle_info['extras']
        curves = [obj for obj in all_objects if obj.type == 'CURVE']

        if not curves:
            return

        # Check if export_extras is enabled
        export_format = bundle_info.get('export_format', '')
        if not self._check_export_extras(bundle_info):
            if export_format in ('OBJ', 'COLLADA'):
                def draw_error(self, context):
                    self.layout.label(text="The 'Export Curves as Custom Properties' modifier")
                    self.layout.label(text=f"is not supported for {export_format} format.")
                    self.layout.label(text="Use GLB, GLTF, or FBX instead.")
                bpy.context.window_manager.popup_menu(draw_error, title="Export Error", icon='ERROR')
                print(f"ERROR: {export_format} format does not support custom properties!")
                return
            else:
                prop_name = 'use_custom_props' if export_format == 'FBX' else 'export_extras'
                def draw_error(self, context):
                    self.layout.label(text="The 'Export Curves as Custom Properties' modifier requires")
                    self.layout.label(text=f"'{prop_name}' to be enabled in the export preset.")
                    self.layout.label(text="Custom properties will not be exported without it.")
                bpy.context.window_manager.popup_menu(draw_error, title="Export Warning", icon='ERROR')
                print(f"WARNING: {prop_name} is not enabled - curve custom properties will not be exported!")

        pivot = bundle_info['pivot']

        # Check if Y-up conversion is needed
        # Different exporters use different property names:
        # - GLTF/GLB: export_yup (bool)
        # - FBX: axis_up ('Y' or 'Z')
        preset = bundle_info.get('export_preset', {})
        if export_format == 'FBX':
            use_y_up = preset.get('axis_up', 'Y') == 'Y'
        else:
            use_y_up = preset.get('export_yup', True)

        for curve_obj in curves:
            # Extract curve data
            curve_data = extract_curve_data(curve_obj, pivot, use_y_up)

            # Serialize to JSON
            json_data = json.dumps(curve_data, separators=(',', ':'))  # Compact JSON

            # Check size limit
            if len(json_data) > MAX_CUSTOM_PROPERTY_SIZE:
                def draw_error(self, context):
                    self.layout.label(text=f"Curve '{curve_obj.name}' spline data exceeds size limit.")
                    self.layout.label(text=f"Size: {len(json_data)} bytes, Limit: {MAX_CUSTOM_PROPERTY_SIZE} bytes")
                    self.layout.label(text="Consider simplifying the curve or splitting into multiple curves.")
                bpy.context.window_manager.popup_menu(draw_error, title="Export Error", icon='ERROR')
                print(f"ERROR: Curve '{curve_obj.name}' spline data too large: {len(json_data)} bytes")
                continue

            # Store as custom property
            curve_obj[self.property_name] = json_data
            print(f"Exported curve '{curve_obj.name}' spline data ({len(json_data)} bytes)")
