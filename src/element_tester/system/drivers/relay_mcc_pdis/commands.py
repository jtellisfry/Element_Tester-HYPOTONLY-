# =================
# PDIS08 Commands (low-level)
# =================
#
# IDENTICAL to relay_mcc/commands.py - only uses PDIS08Transport instead of ERB08Transport.
# All command logic is the same.

from __future__ import annotations
from dataclasses import dataclass
from typing import List

from .transport import PDIS08Transport


@dataclass
class RelayState:
    current_byte: int = 0


class PDIS08Commands:
    """
    Low-level relay commands for PDIS08.

    LEGO pieces (identical to ERB08Commands):
      - cmd_set_bit
      - cmd_set_many
      - cmd_all_off
      - cmd_read_relay
      - cmd_pulse_bit
    """

    def __init__(self, transport: PDIS08Transport):
        self.t = transport
        self.state = RelayState()

    # -------- Helpers for logical ON/OFF with active_high mapping ----------
    def _logical_to_device_bit(self, on: bool) -> bool:
        """
        Maps logical relay ON/OFF to actual device bit (considering active_high).
        """
        if self.t.p.active_high:
            # device 1 = ON, 0 = OFF
            return on
        else:
            # device 0 = ON, 1 = OFF
            return not on

    # -------- Commands ----------
    def cmd_set_bit(self, relay: int, on: bool) -> None:
        """
        Set a single relay (0-7) ON/OFF logically.
        Automatically handles active_high logic.
        """
        device_on = self._logical_to_device_bit(on)
        self.t.write_bit_raw(relay, device_on)

    def cmd_set_many(self, relays_on: List[int], relays_off: List[int]) -> None:
        """
        Turn multiple relays ON and OFF.
        Each relay is written individually.
        """
        # First apply OFF
        for relay in relays_off:
            if 0 <= relay <= 7:
                self.cmd_set_bit(relay, False)
        
        # Then apply ON
        for relay in relays_on:
            if 0 <= relay <= 7:
                self.cmd_set_bit(relay, True)

    def cmd_all_off(self) -> None:
        """
        Drive all 8 relays to logical OFF.
        """
        for relay in range(8):
            self.cmd_set_bit(relay, False)

    def cmd_read_relay(self, relay: int) -> bool:
        """
        Read current state of a relay.
        Returns logical state (accounting for active_high).
        """
        device_state = self.t.read_bit_raw(relay)
        # Invert if active_low
        if self.t.p.active_high:
            return device_state
        else:
            return not device_state

    def cmd_pulse_bit(self, relay: int, on_ms: float = 100.0) -> None:
        """
        Turn a relay ON for on_ms milliseconds and then OFF.
        """
        import time

        self.cmd_set_bit(relay, True)
        time.sleep(on_ms / 1000.0)
        self.cmd_set_bit(relay, False)
