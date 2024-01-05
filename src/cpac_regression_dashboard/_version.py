#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Get version from packaging metadata."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cpac_regression_dashboard")
except PackageNotFoundError:
    __version__ = "unknown"
