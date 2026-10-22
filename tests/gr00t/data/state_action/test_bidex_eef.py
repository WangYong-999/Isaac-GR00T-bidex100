"""Regression checks for the BiDex-100 quaternion action representation."""

from gr00t.data.state_action.state_action_processor import StateActionProcessor
from gr00t.data.types import ActionFormat, ActionType
import numpy as np
import pytest
from scipy.spatial.transform import Rotation


@pytest.mark.parametrize("arms", [1, 2])
def test_bidex_relative_actions_restore_pose(arms):
    rng = np.random.default_rng(20261022)
    reference = np.concatenate(
        [
            np.concatenate([rng.normal(size=3), Rotation.random(random_state=rng).as_quat()])
            for _ in range(arms)
        ]
    )
    actions = np.concatenate(
        [
            np.concatenate(
                [rng.normal(size=(16, 3)), Rotation.random(16, random_state=rng).as_quat()], axis=1
            )
            for _ in range(arms)
        ],
        axis=1,
    )
    original = actions.copy()
    processor = StateActionProcessor.__new__(StateActionProcessor)
    relative = processor._convert_to_relative_action(
        actions, reference, ActionType.EEF_XYZ_QUAT_XYZW, ActionFormat.DEFAULT
    )
    restored = processor._convert_to_absolute_action(
        relative, reference, ActionType.EEF_XYZ_QUAT_XYZW, ActionFormat.DEFAULT
    )
    for arm in range(arms):
        start = arm * 7
        np.testing.assert_allclose(
            restored[:, start : start + 3], actions[:, start : start + 3], atol=1e-12
        )
        expected = Rotation.from_quat(actions[:, start + 3 : start + 7])
        actual = Rotation.from_quat(restored[:, start + 3 : start + 7])
        np.testing.assert_allclose((expected.inv() * actual).magnitude(), 0, atol=1e-12)
    np.testing.assert_array_equal(actions, original)


def test_bidex_unchanged_pose_has_identity_delta():
    processor = StateActionProcessor.__new__(StateActionProcessor)
    reference = np.array([1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0] * 2)
    actions = np.repeat(reference[None], 16, axis=0)
    relative = processor._convert_to_relative_action(
        actions, reference, ActionType.EEF_XYZ_QUAT_XYZW, ActionFormat.DEFAULT
    )
    np.testing.assert_allclose(relative, np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0] * 2] * 16))
