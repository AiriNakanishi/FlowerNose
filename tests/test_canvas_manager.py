import unittest

import config
from core.canvas_manager import CanvasManager


class CanvasManagerTests(unittest.TestCase):
    def test_truncate_removes_points_across_segments(self):
        canvas = CanvasManager(100, 100)
        canvas.strokes = [[
            {
                "color": config.Colors.PEN_PINK,
                "points": [(10, 10), (20, 20), (30, 30)],
            },
            {
                "color": config.Colors.PASTEL_BLUE,
                "points": [(30, 30), (40, 40)],
            },
        ]]

        changed = canvas.truncate_to_point_count(4)

        self.assertTrue(changed)
        self.assertEqual(canvas.point_count(), 4)
        self.assertEqual(canvas.strokes[0][1]["points"], [(30, 30)])
        self.assertIsNone(canvas.current_stroke)
        self.assertIsNone(canvas.current_segment)


if __name__ == "__main__":
    unittest.main()
