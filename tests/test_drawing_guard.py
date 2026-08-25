import unittest

from core.drawing_guard import FaceExitDrawingGuard


class FaceExitDrawingGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = FaceExitDrawingGuard(
            width=1000,
            height=1000,
            history_seconds=1.0,
            min_distance=0.08,
        )

    def test_stationary_face_does_not_request_rollback(self):
        self.guard.record(0.0, (500, 500), 10)
        self.guard.record(0.5, (520, 510), 20)

        self.assertIsNone(self.guard.rollback_point_count())

    def test_large_exit_movement_rolls_back_to_start_of_history(self):
        self.guard.record(0.0, (500, 500), 10)
        self.guard.record(0.5, (610, 500), 20)

        self.assertEqual(self.guard.rollback_point_count(), 10)

    def test_expired_samples_are_not_removed_from_canvas(self):
        self.guard.record(0.0, (400, 500), 10)
        self.guard.record(1.5, (600, 500), 20)

        self.assertIsNone(self.guard.rollback_point_count())


if __name__ == "__main__":
    unittest.main()
