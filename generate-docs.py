#!/usr/bin/env python3

import os
from pathlib import Path

import django
import pdoc

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

pdoc.render.configure(docformat="restructuredtext", search=True)

modules_to_document = [
    "core.management.commands",
    "core.models",
    "core.views",
]

output_dir = Path("docs")
pdoc.pdoc(*modules_to_document, output_directory=output_dir)
