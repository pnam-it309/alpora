"""Discovery of local wallpaper image folders and files."""
from pathlib import Path

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def discover_image_folders() -> list[dict]:
    """Return existing user and system directories commonly containing wallpapers."""
    home = Path.home()
    candidates = (
        (home / 'Pictures', 'Pictures'),
        (home / 'Pictures/Wallpapers', 'Wallpapers'),
        (home / 'Wallpapers', '~/Wallpapers'),
        (home / 'Downloads', 'Downloads'),
        (home / 'Pictures/Screenshots', 'Screenshots'),
        (Path('/usr/share/backgrounds'), 'System Backgrounds'),
        (Path('/usr/share/wallpapers'), 'System Wallpapers'),
    )
    folders = []
    for path, label in candidates:
        try:
            if path.is_dir():
                folders.append({'path': str(path), 'label': label})
        except OSError:
            continue
    return folders


def discover_local_images(folder=None, limit=60) -> list[dict]:
    """Scan a specific path or common local directories for recent wallpaper images."""
    if limit <= 0:
        return []
    folder_text = str(folder).strip() if folder is not None else ''
    candidates = []
    if folder_text:
        try:
            target = Path(folder_text).expanduser().resolve()
            if target.is_file():
                if target.suffix.lower() in IMAGE_EXTENSIONS:
                    return [{'path': str(target), 'name': target.stem, 'folder': str(target.parent)}]
                return []
            if not target.is_dir():
                return []
            for pattern in ('*', '*/*'):
                for path in target.glob(pattern):
                    candidates.append((0, path))
        except (OSError, ValueError):
            return []
    else:
        folders = discover_image_folders()
        screenshots_dir = (Path.home() / 'Pictures/Screenshots').resolve()
        non_screenshots = [entry for entry in folders if entry['label'] != 'Screenshots']
        screenshots = [entry for entry in folders if entry['label'] == 'Screenshots']
        for group_priority, group in ((0, non_screenshots), (1, screenshots)):
            for entry in group:
                base = Path(entry['path'])
                for pattern in ('*', '*/*'):
                    try:
                        for path in base.glob(pattern):
                            try:
                                is_ss = group_priority == 1 or path.resolve().is_relative_to(screenshots_dir)
                            except OSError:
                                is_ss = group_priority == 1
                            candidates.append((1 if is_ss else 0, path))
                    except OSError:
                        continue

    seen = set()
    found = []
    for priority, raw_path in candidates:
        try:
            if raw_path.suffix.lower() not in IMAGE_EXTENSIONS or not raw_path.is_file():
                continue
            resolved = raw_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            mtime = resolved.stat().st_mtime
        except OSError:
            continue
        found.append((priority, -mtime, resolved))

    found.sort(key=lambda item: (item[0], item[1], str(item[2])))
    return [
        {'path': str(path), 'name': path.stem[:40], 'folder': path.parent.name}
        for _, _, path in found[:limit]
    ]
