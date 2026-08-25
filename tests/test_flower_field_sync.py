from types import SimpleNamespace
import unittest

from gallery.visitor_flowers.flower_field import FlowerField


class FlowerFieldSyncTests(unittest.TestCase):
    @staticmethod
    def _field(paths):
        field = FlowerField.__new__(FlowerField)
        field.flowers = [SimpleNamespace(source_path=path) for path in paths]
        field.known_files = set(paths)
        field._cached_images = {path: object() for path in paths}

        def load_image(path):
            image = object()
            field._cached_images[path] = image
            return image

        field._load_image = load_image
        field._make_flower = lambda image, path, **kwargs: SimpleNamespace(
            source_path=path,
            delay=0.0,
        )
        field._trim_to_max = lambda: None
        return field

    def test_deleted_file_disappears_from_field(self):
        field = self._field(["kept.png", "deleted.png"])

        field.sync_files(["kept.png"])

        self.assertEqual(
            [flower.source_path for flower in field.flowers],
            ["kept.png"],
        )
        self.assertNotIn("deleted.png", field._cached_images)

    def test_new_file_is_added(self):
        field = self._field(["kept.png"])

        field.sync_files(["kept.png", "new.png"])

        self.assertEqual(
            [flower.source_path for flower in field.flowers],
            ["kept.png", "new.png"],
        )

    def test_modified_file_is_reloaded(self):
        field = self._field(["changed.png"])
        old_image = field._cached_images["changed.png"]

        field.sync_files(["changed.png"], {"changed.png"})

        self.assertIsNot(field._cached_images["changed.png"], old_image)
        self.assertEqual(len(field.flowers), 1)

    def test_deletion_promotes_next_file_when_gallery_is_full(self):
        paths = [f"flower_{index}.png" for index in range(31)]
        field = self._field(paths[1:])
        field.known_files = set(paths)

        field.sync_files(paths[:-1])

        displayed = {flower.source_path for flower in field.flowers}
        self.assertNotIn(paths[-1], displayed)
        self.assertIn(paths[0], displayed)
        self.assertEqual(len(displayed), 30)


if __name__ == "__main__":
    unittest.main()
