"""Minimal URDF serial-chain model used by the Jacobian short-move planner."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
import xml.etree.ElementTree as ET

import numpy as np


def _vector(text: str | None, default) -> np.ndarray:
    values = [float(value) for value in str(text or "").split()]
    return np.asarray(values if len(values) == 3 else default, dtype=float)


def _origin_transform(xyz: np.ndarray, rpy: np.ndarray) -> np.ndarray:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rotation = np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ])
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = xyz
    return transform


def _axis_rotation(axis: np.ndarray, angle: float) -> np.ndarray:
    norm = float(np.linalg.norm(axis))
    if norm <= 1e-12:
        raise ValueError("URDF revolute joint has a zero-length axis")
    x, y, z = axis / norm
    c, s, one_minus_c = math.cos(angle), math.sin(angle), 1.0 - math.cos(angle)
    rotation = np.array([
        [c + x * x * one_minus_c, x * y * one_minus_c - z * s, x * z * one_minus_c + y * s],
        [y * x * one_minus_c + z * s, c + y * y * one_minus_c, y * z * one_minus_c - x * s],
        [z * x * one_minus_c - y * s, z * y * one_minus_c + x * s, c + z * z * one_minus_c],
    ])
    transform = np.eye(4)
    transform[:3, :3] = rotation
    return transform


@dataclass(frozen=True)
class JointSpec:
    name: str
    joint_type: str
    parent: str
    child: str
    origin: np.ndarray
    axis: np.ndarray
    lower: float | None
    upper: float | None


@dataclass(frozen=True)
class UrdfChain:
    joints: tuple[JointSpec, ...]

    def forward(self, positions_by_name: dict[str, float]) -> np.ndarray:
        transform = np.eye(4)
        for joint in self.joints:
            transform = transform @ joint.origin
            if joint.joint_type in {"revolute", "continuous"}:
                if joint.name not in positions_by_name:
                    raise KeyError(f"missing position for URDF joint {joint.name}")
                transform = transform @ _axis_rotation(
                    joint.axis, float(positions_by_name[joint.name])
                )
            elif joint.joint_type == "prismatic":
                if joint.name not in positions_by_name:
                    raise KeyError(f"missing position for URDF joint {joint.name}")
                translation = np.eye(4)
                translation[:3, 3] = joint.axis * float(positions_by_name[joint.name])
                transform = transform @ translation
        return transform

    def position_violations(
        self, positions_by_name: dict[str, float], tolerance: float = 1e-9
    ) -> list[tuple[str, float, float, float]]:
        violations = []
        for joint in self.joints:
            if joint.name not in positions_by_name or joint.lower is None or joint.upper is None:
                continue
            value = float(positions_by_name[joint.name])
            if value < joint.lower - tolerance or value > joint.upper + tolerance:
                violations.append((joint.name, value, joint.lower, joint.upper))
        return violations


@lru_cache(maxsize=8)
def load_urdf_chain(urdf_path: str, base_link: str, tip_link: str) -> UrdfChain:
    root = ET.parse(urdf_path).getroot()
    by_child: dict[str, JointSpec] = {}
    for element in root.findall("joint"):
        parent_element = element.find("parent")
        child_element = element.find("child")
        if parent_element is None or child_element is None:
            continue
        origin_element = element.find("origin")
        axis_element = element.find("axis")
        limit_element = element.find("limit")
        xyz = _vector(origin_element.get("xyz") if origin_element is not None else None, [0, 0, 0])
        rpy = _vector(origin_element.get("rpy") if origin_element is not None else None, [0, 0, 0])
        lower = upper = None
        if limit_element is not None:
            if limit_element.get("lower") is not None:
                lower = float(limit_element.get("lower"))
            if limit_element.get("upper") is not None:
                upper = float(limit_element.get("upper"))
        spec = JointSpec(
            name=str(element.get("name") or ""),
            joint_type=str(element.get("type") or "fixed"),
            parent=str(parent_element.get("link") or ""),
            child=str(child_element.get("link") or ""),
            origin=_origin_transform(xyz, rpy),
            axis=_vector(axis_element.get("xyz") if axis_element is not None else None, [1, 0, 0]),
            lower=lower,
            upper=upper,
        )
        by_child[spec.child] = spec

    reversed_chain = []
    link = str(tip_link)
    visited = set()
    while link != base_link:
        if link in visited:
            raise ValueError(f"cycle while resolving URDF chain to {tip_link}")
        visited.add(link)
        joint = by_child.get(link)
        if joint is None:
            raise ValueError(f"no URDF chain from {base_link} to {tip_link}; stopped at {link}")
        reversed_chain.append(joint)
        link = joint.parent
    return UrdfChain(tuple(reversed(reversed_chain)))

