import os
from pathlib import Path


# ============================================================
# FAST SEARCH ROOTS
# ============================================================

USER_ROOTS = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]


START_MENU_ROOTS = [
    Path(os.environ.get("APPDATA", ""))
    / "Microsoft/Windows/Start Menu/Programs",

    Path(os.environ.get("PROGRAMDATA", ""))
    / "Microsoft/Windows/Start Menu/Programs",
]


# ============================================================
# DIRECTORIES TO IGNORE
# ============================================================

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "appdata",
    "windows",
    "temp",
    "$recycle.bin",
    "system volume information",
    "perflogs",
}


# ============================================================
# IGNORE WALK ERRORS
# ============================================================

def handle_walk_error(error):
    # Ignore directories that cannot be accessed
    # and allow the search to continue.
    pass


# ============================================================
# SEARCH FUNCTION
# ============================================================

def search_item(target_name):

    if not target_name:
        return None


    target_name = target_name.lower().strip()


    # ========================================================
    # 1. DIRECT USER ROOT MATCH
    # ========================================================

    for root in USER_ROOTS:

        if (
            root.exists()
            and root.name.lower() == target_name
        ):

            return root


    # ========================================================
    # 2. SEARCH USER FOLDERS
    # ========================================================

    for root in USER_ROOTS:

        result = search_directory(
            root,
            target_name
        )

        if result:
            return result


    # ========================================================
    # 3. SEARCH START MENU
    # ========================================================

    for root in START_MENU_ROOTS:

        result = search_directory(
            root,
            target_name
        )

        if result:
            return result


    # ========================================================
    # 4. DEEP DRIVE SEARCH
    # ========================================================

    print(
        f"ORBIT: '{target_name}' wasn't found "
        "in the quick-search locations."
    )

    print(
        "ORBIT: Initiating deep drive search "
        "(this may take a while)..."
    )


    return search_drives(target_name)


# ============================================================
# SEARCH DIRECTORY
# ============================================================

def search_directory(root, target_name):

    if not root.exists():
        return None


    for dirpath, dirnames, filenames in os.walk(
        root,
        onerror=handle_walk_error
    ):

        # Remove ignored directories before os.walk
        # continues into them.
        dirnames[:] = [
            directory
            for directory in dirnames
            if directory.lower() not in IGNORE_DIRS
        ]


        current_dir = Path(dirpath)


        # ----------------------------------------------------
        # Search folders
        # ----------------------------------------------------

        for dirname in dirnames:

            if dirname.lower() == target_name:

                return current_dir / dirname


        # ----------------------------------------------------
        # Search files
        # ----------------------------------------------------

        for filename in filenames:

            file_path = current_dir / filename


            file_name_lower = (
                file_path.name.lower()
            )

            file_stem_lower = (
                file_path.stem.lower()
            )


            if (
                file_name_lower == target_name
                or
                file_stem_lower == target_name
            ):

                return file_path


    return None


# ============================================================
# SEARCH ALL AVAILABLE DRIVES
# ============================================================

def search_drives(target_name):

    for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":

        drive = Path(
            f"{drive_letter}:/"
        )


        if not drive.exists():

            continue


        print(
            f"ORBIT: Searching {drive}..."
        )


        result = search_directory(
            drive,
            target_name
        )


        if result:

            return result


    return None


# ============================================================
# OPEN FILE / FOLDER / APPLICATION
# ============================================================

def open_item(target):

    if target is None:

        return False


    try:

        os.startfile(
            str(target)
        )

        return True


    except OSError as error:

        print(
            f"ORBIT Error: Could not open {target}"
        )

        print(error)

        return False