"""Import a resolved URDF as a static scene at zero joint positions. No ROS."""
from pathlib import Path
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

import numpy as np

from .geometry import make_box, make_cylinder, make_sphere, read_stl
from .model import Pose, Scene, SceneObject, euler_degrees, vector


def _numbers(value, default, label):
    return vector(value.split() if value else default,label)


def _origin(element):
    matrix = np.eye(4)
    if element is not None:
        xyz = np.asarray(_numbers(element.get('xyz'),(0,0,0),'URDF XYZ'))*1000
        rpy = np.degrees(_numbers(element.get('rpy'),(0,0,0),'URDF RPY'))
        matrix = Pose(tuple(xyz),tuple(rpy)).matrix()
    return matrix


def resolve_mesh(uri, urdf_path, package_root=None, package_resolver=None):
    if '${' in uri or '$(' in uri:
        raise ValueError('Import a resolved URDF. Xacro expressions must be expanded outside this app.')
    if uri.startswith('package://'):
        parts = uri[len('package://'):].split('/',1)
        if len(parts) != 2: raise ValueError(f'Invalid package mesh URI: {uri}')
        package, relative = parts
        candidates = []
        if package_resolver:
            try:
                candidates.append(Path(package_resolver(package))/relative)
            except LookupError:
                pass
        if package_root:
            candidates.extend([Path(package_root)/relative,Path(package_root)/package/relative])
        for parent in [Path(urdf_path).parent,*Path(urdf_path).parents]:
            if parent.name == package: candidates.append(parent/relative)
            candidates.append(parent/package/relative)
        for candidate in candidates:
            if candidate.is_file(): return candidate.resolve()
        raise FileNotFoundError(f'Cannot resolve {uri}. Choose its mesh package folder when importing the URDF.')
    if uri.startswith('file://'):
        return Path(unquote(urlparse(uri).path)).resolve()
    if '://' in uri:
        raise ValueError('Only local files and package:// mesh references are supported.')
    return (Path(urdf_path).parent/uri).resolve()


def load_urdf(path, package_root=None, *, local_visuals=False, package_resolver=None):
    """Load static visuals, or return (link, local visual) pairs for a live TF view."""
    path = Path(path).resolve()
    root = ET.parse(path).getroot()
    links = {link.get('name'):link for link in root.findall('link')}
    if root.tag != 'robot' or not links:
        raise ValueError('No robot links found. Open a resolved .urdf file, rather than xacro.')
    if None in links or '' in links or len(links) != len(root.findall('link')):
        raise ValueError('URDF links must have unique, nonempty names.')
    parents = {}
    for joint in root.findall('joint'):
        parent, child = joint.find('parent'),joint.find('child')
        if parent is None or child is None: raise ValueError('A URDF joint is missing its parent or child.')
        parent,child = parent.get('link'),child.get('link')
        if parent not in links or child not in links or child in parents:
            raise ValueError('Invalid or ambiguous URDF link hierarchy.')
        parents[child] = (parent,_origin(joint.find('origin')))
    matrices = {}
    visiting = set()
    def world(name):
        if name in matrices: return matrices[name]
        if name in visiting: raise ValueError('The URDF link hierarchy contains a cycle.')
        visiting.add(name)
        matrices[name] = world(parents[name][0]) @ parents[name][1] if name in parents else np.eye(4)
        visiting.remove(name)
        return matrices[name]
    materials = {}
    for material in root.findall('material'):
        color = material.find('color')
        if color is not None: materials[material.get('name')] = vector(color.get('rgba','').split(),'URDF color',4)
    scene,cache,visuals = Scene(),{},[]
    for name,link in links.items():
        link_matrix = np.eye(4) if local_visuals else world(name)
        for index,visual in enumerate(link.findall('visual')):
            geometry = visual.find('geometry')
            if geometry is None: continue
            unit_scale = (1.,1.,1.)
            if (mesh_spec := geometry.find('mesh')) is not None:
                source = resolve_mesh(mesh_spec.get('filename',''),path,package_root,package_resolver)
                if source.suffix.lower() != '.stl':
                    raise ValueError(f'Only STL meshes are supported in this version: {source.name}')
                if source not in cache: cache[source] = read_stl(source)
                mesh = cache[source]
                unit_scale = tuple(np.asarray(_numbers(mesh_spec.get('scale'),(1,1,1),'URDF mesh scale'))*1000)
            elif (spec := geometry.find('box')) is not None:
                mesh = make_box(np.asarray(_numbers(spec.get('size'),None,'box size'))*1000)
            elif (spec := geometry.find('cylinder')) is not None:
                mesh = make_cylinder(float(spec.get('radius'))*1000,float(spec.get('length'))*1000)
            elif (spec := geometry.find('sphere')) is not None:
                mesh = make_sphere(float(spec.get('radius'))*1000)
            else:
                raise ValueError(f'Unsupported geometry in link {name}.')
            matrix = link_matrix @ _origin(visual.find('origin'))
            material = visual.find('material')
            color = (0.62,0.66,0.73,1.)
            if material is not None:
                color_spec = material.find('color')
                color = vector(color_spec.get('rgba','').split(),'URDF color',4) if color_spec is not None else materials.get(material.get('name'),color)
            obj = SceneObject(f'{name} / visual {index+1}',mesh,
                pose=Pose(tuple(matrix[:3,3]),euler_degrees(matrix)),unit_scale=unit_scale,color=color,
                **({'id':f'robot/{name}/visual/{index}'} if local_visuals else {}))
            scene.objects.append(obj)
            visuals.append((name, obj))
    if not scene.objects: raise ValueError('This URDF contains no supported visual geometry.')
    return visuals if local_visuals else scene
