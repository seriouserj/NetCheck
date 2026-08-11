"""
Version: 1.6.9
Date: 2026-08-11
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Verify packaged SVG arrows for numeric stepper controls.
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


def test_raster_ditis_logo_is_transparent_and_visible() -> None:
    logo = Image.open(resource_path("icons/ditis-logo.png"))
    assert logo.mode == "RGBA"
    assert logo.size == (1000, 216)
    assert logo.getbbox() is not None
    assert logo.getpixel((999, 0))[3] == 0


def test_tubbetec_header_logo_is_transparent_and_visible() -> None:
    logo = Image.open(resource_path("icons/tubbetec-logo.png"))

    assert logo.mode == "RGBA"
    assert logo.size == (160, 63)
    assert logo.getbbox() is not None


def test_numeric_stepper_arrows_are_valid_svg_resources() -> None:
    for name in ("step-up-white.svg", "step-down-white.svg"):
        arrow = resource_path(f"icons/{name}")

        assert arrow.is_file()
        assert ElementTree.parse(arrow).getroot().tag.endswith("svg")
