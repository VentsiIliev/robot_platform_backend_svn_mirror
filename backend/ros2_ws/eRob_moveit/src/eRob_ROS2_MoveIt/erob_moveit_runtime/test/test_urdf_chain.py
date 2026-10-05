from pathlib import Path

import numpy as np

from motion.planning.urdf_chain import load_urdf_chain


ZEROERR_ROOT = Path(__file__).resolve().parents[2] / "zeroerr"
SHORT_LINK_URDF = (
    ZEROERR_ROOT
    / "config"
    / "paint_short_links"
    / "urdfs"
    / "erob_arm_short_links.with_mounting_stl.urdf"
)


def test_short_link_chain_uses_active_urdf_geometry():
    chain = load_urdf_chain(str(SHORT_LINK_URDF), "base_link", "ee_link")
    joint_3 = next(joint for joint in chain.joints if joint.name == "Joint_3")
    joint_4 = next(joint for joint in chain.joints if joint.name == "Joint_4")

    assert np.allclose(joint_3.origin[:3, 3], [0.0, 0.0005, 0.2435])
    assert np.allclose(joint_4.origin[:3, 3], [0.0, -0.014, 0.211])


def test_short_link_chain_detects_joint_1_upper_limit_violation():
    chain = load_urdf_chain(str(SHORT_LINK_URDF), "base_link", "ee_link")
    positions = {f"Joint_{index}": 0.0 for index in range(1, 7)}
    positions["Joint_1"] = 6.358437

    assert chain.position_violations(positions) == [
        ("Joint_1", 6.358437, -6.28318, 6.28318)
    ]


def test_short_link_chain_forward_kinematics_is_finite():
    chain = load_urdf_chain(str(SHORT_LINK_URDF), "base_link", "ee_link")
    positions = {f"Joint_{index}": 0.0 for index in range(1, 7)}
    transform = chain.forward(positions)

    assert transform.shape == (4, 4)
    assert np.isfinite(transform).all()
    assert np.allclose(transform[3], [0.0, 0.0, 0.0, 1.0])
