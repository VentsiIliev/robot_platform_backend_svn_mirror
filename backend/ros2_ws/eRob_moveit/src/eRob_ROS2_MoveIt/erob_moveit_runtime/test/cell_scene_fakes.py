"""MoveIt-like scene service: removing an absent object reports failure."""
from concurrent.futures import Future
from types import SimpleNamespace as NS
from unittest.mock import Mock


def scene_node(existing=()):
    node,reader,writer=Mock(),Mock(),Mock()
    reader.service_is_ready.return_value=True
    writer.service_is_ready.return_value=True
    world=set(existing)
    calls=[]
    def completed(value):
        future=Future();future.set_result(value);return future
    def read(request):
        assert request.components.components==8
        return completed(NS(scene=NS(world=NS(collision_objects=[NS(id=key) for key in world]))))
    def apply(request):
        calls.append(request)
        success=True
        for obj in request.scene.world.collision_objects:
            if obj.operation==obj.REMOVE:
                if obj.id not in world:success=False
                else:world.remove(obj.id)
            else:world.add(obj.id)
        return completed(NS(success=success))
    reader.call_async.side_effect=read
    writer.call_async.side_effect=apply
    node.create_client.side_effect=lambda _type,name:reader if name=='/get_planning_scene' else writer
    return node,calls,world
