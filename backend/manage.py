#!/usr/bin/env python
# Importing Django's command line utility for administrative tasks.
import os
import sys

if __name__ == "__main__":
    # Telling Django where to find the settings.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "invoice_extractor.settings")
    try:
        # Trying to import the Django's command system.
        from django.core.management import execute_from_command_line
    # If it doesn't work, We show a helpful error.
    except ImportError as exc:
        raise ImportError("Couldn't import Django") from exc
    # Run's the command the user typed like runserver, mitigate, etc.
    execute_from_command_line(sys.argv)