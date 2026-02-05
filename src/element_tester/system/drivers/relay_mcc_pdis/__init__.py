"""
=================
PDIS08 relay driver package
=================

This package implements a driver for MCC USB-PDIS08 relay hardware with IDENTICAL
interface to relay_mcc (ERB08). Both use mcculw library, only difference is
PDIS08 uses single-port (all 8 relays on FIRSTPORTA) vs ERB08 dual-port.

IDENTICAL API to relay_mcc - allows seamless driver swapping:
    relay_driver = ERB08Driver(board_num=0, port_low=12, port_high=13)  # ERB08
    # or
    relay_driver = PDIS08Driver(board_num=0, port_low=10)  # PDIS08
    
    # All methods work identically
    relay_driver.initialize()
    relay_driver.set_relay(0, True)
    relay_driver.close_pin1to6()

LAYERS:
 - transport  : mcculw communication (same library as ERB08)
 - commands   : low-level relay operations (same as ERB08)
 - procedures : higher-level flows (same as ERB08)
 - driver     : façade (same interface as ERB08)

USAGE:
    from element_tester.system.drivers.relay_mcc_pdis import PDIS08Driver
    
    # Real hardware
    drv = PDIS08Driver(board_num=0, port_low=10, simulate=False)
    drv.initialize()
    drv.set_relay(0, True)
    drv.shutdown()
    
    # Simulate mode (no hardware)
    drv = PDIS08Driver(board_num=0, simulate=True)
"""

from .transport import PDIS08OpenParams, PDIS08Transport
from .commands import PDIS08Commands
from .procedures import PDIS08Procedures, RelayMapping
from .driver import PDIS08Driver
from .errors import PDIS08Error

__all__ = [
    "PDIS08OpenParams",
    "PDIS08Transport",
    "PDIS08Commands",
    "PDIS08Procedures",
    "RelayMapping",
    "PDIS08Driver",
    "PDIS08Error",
]
