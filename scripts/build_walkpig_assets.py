from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = BASE_DIR / "assets" / "walkpig" / "sheets"
OUTPUT_DIR = BASE_DIR / "assets" / "walkpig"
FRAME_COUNT = 4
PADDING = 18


def remove_green_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if g > 145 and g > r * 1.25 and g > b * 1.25:
                pixels[x, y] = (r, g, b, 0)

    return rgba


def crop_content(frame: Image.Image) -> Image.Image:
    alpha = frame.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return frame

    left, top, right, bottom = bbox
    left = max(0, left - PADDING)
    top = max(0, top - PADDING)
    right = min(frame.width, right + PADDING)
    bottom = min(frame.height, bottom + PADDING)
    return frame.crop((left, top, right, bottom))


def normalize_frames(frames: list[Image.Image]) -> list[Image.Image]:
    max_width = max(frame.width for frame in frames)
    max_height = max(frame.height for frame in frames)
    normalized = []

    for frame in frames:
        canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
        x = (max_width - frame.width) // 2
        y = max_height - frame.height
        canvas.alpha_composite(frame, (x, y))
        normalized.append(canvas)

    return normalized


def build_variant(sheet_path: Path, variant_index: int) -> None:
    image = Image.open(sheet_path)
    frame_width = image.width // FRAME_COUNT
    frames = []

    for frame_index in range(FRAME_COUNT):
        left = frame_index * frame_width
        right = image.width if frame_index == FRAME_COUNT - 1 else left + frame_width
        raw_frame = image.crop((left, 0, right, image.height))
        transparent = remove_green_background(raw_frame)
        frames.append(crop_content(transparent))

    variant_dir = OUTPUT_DIR / f"variant_{variant_index}"
    variant_dir.mkdir(parents=True, exist_ok=True)
    normalized_frames = normalize_frames(frames)

    for frame_index, frame in enumerate(normalized_frames):
        frame.save(variant_dir / f"{frame_index}.png")

    normalized_frames[0].save(
        OUTPUT_DIR / f"preview_variant_{variant_index}.gif",
        save_all=True,
        append_images=normalized_frames[1:] + normalized_frames[:1],
        duration=140,
        loop=0,
        disposal=2,
    )


def main() -> None:
    sheets = sorted(SOURCE_DIR.glob("walkpig_variant_*_sheet.png"))
    if not sheets:
        raise SystemExit(f"No walkpig sheets found in {SOURCE_DIR}")

    for variant_index, sheet_path in enumerate(sheets, start=1):
        build_variant(sheet_path, variant_index)
        print(f"Built variant_{variant_index} from {sheet_path.name}")


if __name__ == "__main__":
    main()
