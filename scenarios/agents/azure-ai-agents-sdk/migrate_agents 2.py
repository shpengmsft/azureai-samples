#!/usr/bin/env python3

"""
migrate_agents.py

Scan source for client.<old_method>(…) calls and rewrite them to the new
sub-client form.  Supports processing files by glob, directories (recursively),
and stdin→stdout.  By default it processes .py and .md files; you can add
other extensions in the EXTENSIONS set.

Usage:

  # In‐place single py file
  python migrate_agents.py my_script.py

  # In‐place single md file
  python migrate_agents.py README.md

  # In‐place entire tree (with globs)
  python migrate_agents.py src/**/*.py docs/**/*.md

  # In‐place directory recursion
  python migrate_agents.py my_folder

  # stdout (no in-place)
  cat old.py | python migrate_agents.py --stdout > new.py
"""

import argparse
import glob
import re
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# old_method_name → new_subclient_and_method
# -----------------------------------------------------------------------------
METHOD_RENAMES = {
    # threads
    "create_thread": "threads.create",
    "get_thread": "threads.get",
    "list_threads": "threads.list",
    "update_thread": "threads.update",
    "delete_thread": "threads.delete",
    # messages
    "create_message": "messages.create",
    "get_message": "messages.get",
    "update_message": "messages.update",
    "list_messages": "messages.list",
    # runs
    "create_run": "runs.create",
    "get_run": "runs.get",
    "list_runs": "runs.list",
    "update_run": "runs.update",
    "cancel_run": "runs.cancel",
    "get_run_steps": "runs_steps.get",
    "list_run_steps": "runs_steps.list",
    "create_and_process_run": "runs.create_and_process",
    "create_stream": "runs.stream",
    "submit_tool_outputs_to_run": "runs.submit_tool_outputs",
    "submit_tool_outputs_to_stream": "runs.submit_tool_outputs_stream",
    # polling/file helpers
    "upload_file_and_poll": "files.upload_and_poll",
    "create_vector_store_and_poll": "vector_stores.create_and_poll",
    "create_vector_store_file_batch_and_poll": "vector_store_file_batches.create_and_poll",
    # files
    "upload_file": "files.upload",
    "get_file": "files.get",
    "get_file_content": "files.get_content",
    "list_files": "files.list",
    "delete_file": "files.delete",
    "save_file": "files.save",
    # vector_stores
    "create_vector_store": "vector_stores.create",
    "list_vector_stores": "vector_stores.list",
    "get_vector_store": "vector_stores.get",
    "modify_vector_store": "vector_stores.update",
    "delete_vector_store": "vector_stores.delete",
    # vector_store_files
    "create_vector_store_file": "vector_store_files.create",
    "list_vector_store_files": "vector_store_files.list",
    "get_vector_store_file": "vector_store_files.get",
    "delete_vector_store_file": "vector_store_files.delete",
    # vector_store_file_batches
    "create_vector_store_file_batch": "vector_store_file_batches.create",
    "get_vector_store_file_batch": "vector_store_file_batches.get",
    "cancel_vector_store_file_batch": "vector_store_file_batches.cancel",
    "list_vector_store_file_batch_files": "vector_store_file_batches.list_files",
}

# -----------------------------------------------------------------------------
# Which file‐suffixes should we process?
# Extend this if you want e.g. ".txt" or ".rst"
# -----------------------------------------------------------------------------
EXTENSIONS = {".py", ".md"}

# Precompile regex → replacement pairs
REWRITES = []
for old_name, new_chain in METHOD_RENAMES.items():
    pat = re.compile(rf"\b(\w+)\.{old_name}\(")
    rep = rf"\1.{new_chain}("
    REWRITES.append((pat, rep))


def migrate_text(src: str) -> str:
    """
    Apply all regex-based rewrites to the given source text.
    """
    dst = src
    for pat, rep in REWRITES:
        dst = pat.sub(rep, dst)
    return dst


def process_file(path: Path, in_place: bool):
    """
    Read the file at `path`, apply migrations, and either overwrite it
    (if in_place) or write to stdout.
    """
    text = path.read_text(encoding="utf-8")
    new_text = migrate_text(text)

    if in_place:
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"Migrated: {path}")
        else:
            print(f"No changes: {path}")
    else:
        sys.stdout.write(new_text)


def main():
    parser = argparse.ArgumentParser(
        prog="migrate_agents.py", description="Rewrite X.<old_method> calls to the new sub-client form"
    )
    parser.add_argument(
        "files", nargs="*", help="Files, directories, or glob patterns to process. If none, reads stdin."
    )
    parser.add_argument(
        "--stdout", action="store_true", help="Write transformed text to stdout instead of in-place updates."
    )
    args = parser.parse_args()

    # stdin → stdout
    if not args.files:
        src = sys.stdin.read()
        sys.stdout.write(migrate_text(src))
        return

    # expand file arguments
    paths = []
    for pattern in args.files:
        p = Path(pattern)
        if p.is_dir():
            # recurse for each supported extension
            for ext in EXTENSIONS:
                for f in p.rglob(f"*{ext}"):
                    paths.append(f)
        else:
            # use glob.glob (supports absolutes, **, etc.)
            for fn in glob.glob(pattern, recursive=True):
                paths.append(Path(fn))

    # filter and process
    for path in paths:
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            process_file(path, in_place=not args.stdout)


if __name__ == "__main__":
    main()
