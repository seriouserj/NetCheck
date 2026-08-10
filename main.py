"""
Version: 1.6.2
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Start the NetCheck 1.6.2 click-to-copy maintenance release.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 13):
    raise SystemExit("NetCheck requires Python 3.13 or newer.")

from core.metadata import APP_VERSION


def main() -> int:
    """Start the NetCheck desktop application."""
    if "--version" in sys.argv:
        print(APP_VERSION)
        return 0
    if "--vlan-worker" in sys.argv:
        from core.vlan_worker import run_vlan_worker

        index = sys.argv.index("--vlan-worker")
        return run_vlan_worker(sys.argv[index + 1 :])
    if "--vlan-discovery-worker" in sys.argv:
        from core.vlan_discovery_service import run_vlan_discovery_worker

        index = sys.argv.index("--vlan-discovery-worker")
        return run_vlan_discovery_worker(sys.argv[index + 1 :])
    if "--neighbor-worker" in sys.argv:
        from core.neighbor_service import run_neighbor_worker

        index = sys.argv.index("--neighbor-worker")
        return run_neighbor_worker(sys.argv[index + 1 :])
    from PySide6.QtWidgets import QApplication

    from core.application import configure_application
    from ui.main_window import MainWindow

    application = QApplication(sys.argv)
    if "--smoke-test" in sys.argv:
        from ui.smoke import run_smoke_test

        return run_smoke_test(application)
    configure_application(application)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
