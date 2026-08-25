import unittest

from core.face_tracker import PlayerState


class WinkDetectionTests(unittest.TestCase):
    @staticmethod
    def _neutral(state, frames=1):
        return [
            state.update_wink(0.05, 0.05, 0.30, 0.30)
            for _ in range(frames)
        ]

    @staticmethod
    def _right_wink(state, frames=1):
        return [
            state.update_wink(0.75, 0.05, 0.12, 0.30)
            for _ in range(frames)
        ]

    def test_face_detected_with_persistent_false_candidate_does_not_trigger(self):
        state = PlayerState()

        results = self._right_wink(state, frames=30)

        self.assertFalse(any(results))

    def test_held_wink_changes_color_only_once(self):
        state = PlayerState()
        self._neutral(state, frames=3)

        results = self._right_wink(state, frames=30)

        self.assertEqual(results.count("right"), 1)

    def test_opening_eye_rearms_next_wink(self):
        state = PlayerState()
        self._neutral(state, frames=3)
        first_wink = self._right_wink(state, frames=2)
        self._neutral(state, frames=12)
        for _ in range(12):
            state.update_cooldowns()
        second_wink = self._right_wink(state, frames=2)

        self.assertEqual(first_wink.count("right"), 1)
        self.assertEqual(second_wink.count("right"), 1)


if __name__ == "__main__":
    unittest.main()
