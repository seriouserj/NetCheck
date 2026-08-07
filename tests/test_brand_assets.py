"""
Version: 1.1.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify official logo availability and transparent application icon corners.
"""

from xml.etree import ElementTree

from PIL import Image

from core.resources import resource_path


def test_application_icon_has_transparent_outer_corners() -> None:
    icon = Image.open(resource_path("icons/netcheck-1024.png"))

    assert icon.size == (1024, 1024)
    assert icon.mode == "RGBA"
    assert all(icon.getpixel(point)[3] == 0 for point in ((0, 0), (1023, 0), (0, 1023), (1023, 1023)))


def test_official_ditis_logo_is_valid_svg() -> None:
    logo = resource_path("icons/ditis-logo.svg")

    assert logo.is_file()
    assert ElementTree.parse(logo).getroot().tag.endswith("svg")
