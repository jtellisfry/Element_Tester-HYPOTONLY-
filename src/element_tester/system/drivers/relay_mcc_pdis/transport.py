# =================
# PDIS08 Transport (I/O)
# =================
#
# Thin I/O layer for MCC USB-PDIS08 relay board using mcculw library.
# PDIS08 uses SINGLE-PORT architecture (all 8 relays on one port).
#
# HARDWARE: Measurement Computing USB-PDIS08
# - 8 SPDT Power Relays (Form C)
# - All relays on FIRSTPORTA (port 10)
# - Uses mcculw library (same as ERB08)

from __future__ import annotations
from dataclasses import dataclass
from typing import Union

try:
    from mcculw import ul
    from mcculw.enums import DigitalPortType, DigitalIODirection
except Exception:
    ul = None
    DigitalPortType = None
    DigitalIODirection = None


@dataclass
class PDIS08OpenParams:
    """
    Connection/settings for an MCC USB-PDIS08 relay board.

    board_num   : MCC board number (from InstaCal, usually 0)
    port        : Port for all 8 relays (default 10 = FIRSTPORTA)
    simulate    : if True, do not touch hardware, just print and track state
    active_high : if True, 1 = relay ON; if False, 0 = relay ON (inverts logic)
    """
    board_num: int = 0
    port: Union[int, object, str] = 10  # FIRSTPORTA for PDIS08
    simulate: bool = False
    active_high: bool = True


class PDIS08Transport:
    """
    Thin I/O layer for MCC USB-PDIS08 using mcculw library.

    Responsibilities:
      - Initialize/config port for output (SINGLE-PORT architecture)
      - Write/read individual bits (relays 0-7 on single port)
      - Track current port value in software
      - Support simulate mode when hardware or mcculw is not available
      
    Architecture:
      - Relays 0-7 → FIRSTPORTA (port 10), bits 0-7
    """

    def __init__(self, p: PDIS08OpenParams):
        self.p = p
        self._current_value: int = 0  # Track all 8 relay states

    # -------- Lifecycle ----------
    def open(self) -> None:
        """Initialize PDIS08 board and configure port"""
        if self.p.simulate or ul is None:
            print(
                f"SIM: PDIS08Transport.open(board={self.p.board_num}, port={self.p.port})"
            )
            self._current_value = 0
            return

        port = self._resolve_port_enum(self.p.port)
        
        # Configure port for OUTPUT
        try:
            ul.d_config_port(self.p.board_num, port, DigitalIODirection.OUT)
        except Exception:
            pass
        
        # Initialize all relays to OFF state
        # Note: Initial state will be set by ProcInitializeRelays calling cmd_all_off
        # which properly handles active_high logic

    def close(self) -> None:
        """Close connection to PDIS08"""
        # Note: Relays will be turned OFF by ProcShutdownRelays before close is called
        # which properly handles active_high logic
        
        if self.p.simulate or ul is None:
            print("SIM: PDIS08Transport.close()")
            return

    # -------- Bit-level I/O ----------
    def write_bit_raw(self, relay: int, on: bool) -> None:
        """
        Write a single relay ON/OFF in 'device' space (no active_high invert).
        All 8 relays (0-7) are on the same port.
        """
        if not (0 <= relay <= 7):
            raise ValueError(f"relay must be in 0..7, got {relay}")
        
        port = self._resolve_port_enum(self.p.port)
        
        if self.p.simulate or ul is None:
            print(
                f"SIM: d_bit_out(board={self.p.board_num}, port={self.p.port}, "
                f"bit={relay}, value={1 if on else 0})"
            )
            # Track state
            mask = 1 << relay
            if on:
                self._current_value |= mask
            else:
                self._current_value &= ~mask
            return
        
        # Try direct bit write first
        try:
            ul.d_bit_out(self.p.board_num, port, relay, 1 if on else 0)
        except Exception:
            # Fallback: read-modify-write on whole port
            try:
                current = ul.d_in(self.p.board_num, port)
                mask = 1 << relay
                new_val = (current | mask) if on else (current & ~mask)
                ul.d_out(self.p.board_num, port, new_val)
            except Exception as e:
                raise RuntimeError(f"Failed to write relay {relay} (port={port}, bit={relay}): {e}")

    def read_bit_raw(self, relay: int) -> bool:
        """
        Read current state of a relay from hardware (if available).
        """
        if not (0 <= relay <= 7):
            raise ValueError(f"relay must be in 0..7, got {relay}")

        if self.p.simulate or ul is None:
            # Return from software cache in simulate mode
            mask = 1 << relay
            return bool(self._current_value & mask)
        
        port = self._resolve_port_enum(self.p.port)
        
        try:
            # Read entire port and extract bit
            current = ul.d_in(self.p.board_num, port)
            mask = 1 << relay
            return bool(current & mask)
        except Exception:
            # Fallback to software cache
            mask = 1 << relay
            return bool(self._current_value & mask)

    # -------- Helpers ----------
    def _resolve_port_enum(self, port_value) -> object:
        """
        Try to transform p.port into a DigitalPortType if mcculw enums are available.
        Allows p.port to be:
          - a DigitalPortType already
          - an int (cast to DigitalPortType)
          - a string like "FIRSTPORTA"
        """
        if DigitalPortType is None:
            # No enums (simulate or import failure)
            return port_value

        # Already a DigitalPortType instance
        try:
            if isinstance(port_value, DigitalPortType):
                return port_value
        except TypeError:
            # DigitalPortType not usable with isinstance (in older mcculw),
            # just fall through to other options.
            pass

        # If string, try to look up by name
        if isinstance(port_value, str):
            try:
                return getattr(DigitalPortType, port_value)
            except AttributeError:
                return port_value  # give up, pass through raw

        # If int, try to cast directly
        if isinstance(port_value, int):
            try:
                return DigitalPortType(port_value)
            except Exception:
                return port_value

        # Anything else, just return as-is
        return port_value
