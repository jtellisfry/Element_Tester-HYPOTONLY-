# driver.py
from __future__ import annotations
from typing import Optional, Iterable
import logging

from .procedures import PDIS08Procedures, RelayMapping
from .errors import PDIS08Error


class PDIS08Driver:
    """
    IDENTICAL INTERFACE to ERB08Driver - allows seamless driver swapping.
    
    Change:    relay_driver = ERB08Driver(board_num=0, port_low=12, port_high=13)
    To:        relay_driver = PDIS08Driver(board_num=0, port_low=10)
    
    All method signatures and behavior are identical. PDIS08 uses single-port
    architecture (port_low only), port_high is ignored.
    """

    def __init__(
        self,
        board_num: int = 0,
        port_low: object = 10,
        port_high: object = None,
        simulate: bool = False,
        active_high: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize PDIS08 driver with IDENTICAL SIGNATURE to ERB08Driver.
        
        Parameters (same as ERB08Driver):
            board_num: MCC board number (default 0)
            port_low: Port for all 8 relays (default 10 = FIRSTPORTA)
            port_high: Ignored (PDIS08 is single-port, ERB08 is dual-port)
            simulate: Enable simulation mode
            active_high: True=1 is ON, False=0 is ON
            logger: Optional logger instance
        """
        self.log = logger or logging.getLogger("element_tester.driver.pdis08")
        
        # Warn if port_high provided (PDIS08 is single-port)
        if port_high is not None:
            self.log.debug(
                f"PDIS08Driver ignoring port_high={port_high} "
                f"(PDIS08 uses single-port architecture, all relays on port={port_low})"
            )
        
        self.proc = PDIS08Procedures(
            board_num=board_num,
            port=port_low,
            simulate=simulate,
            active_high=active_high,
            logger=self.log,
        )

    # ---- Lifecycle ----
    def initialize(self) -> None:
        try:
            self.proc.ProcInitializeRelays()
        except Exception as e:
            raise PDIS08Error("Failed to initialize PDIS08: {0}".format(e)) from e

    def shutdown(self) -> None:
        try:
            self.proc.ProcShutdownRelays()
        except Exception as e:
            raise PDIS08Error("Failed to shutdown PDIS08: {0}".format(e)) from e

    # ---- Simple control wrappers ----
    def set_relay(self, bit: int, on: bool) -> None:
        try:
            self.proc.ProcSetBit(bit, on)
        except Exception as e:
            raise PDIS08Error("Failed to set relay {0} -> {1}: {2}".format(bit, on, e)) from e

    def all_off(self) -> None:
        try:
            self.proc.ProcAllOff()
        except Exception as e:
            raise PDIS08Error("Failed to set all relays OFF: {0}".format(e)) from e

    def all_on(self) -> None:
        try:
            self.proc.ProcAllOn()
        except Exception as e:
            raise PDIS08Error("Failed to set all relays ON: {0}".format(e)) from e

    def apply_mapping(
        self,
        bits_on: Iterable[int],
        bits_off: Iterable[int],
    ) -> None:
        try:
            mapping = RelayMapping(
                bits_on=list(bits_on),
                bits_off=list(bits_off),
            )
            self.proc.ProcApplyMapping(mapping)
        except Exception as e:
            raise PDIS08Error("Failed to apply mapping: {0}".format(e)) from e

    def self_test_walk(self, delay_ms: float = 100.0) -> None:
        try:
            self.proc.ProcSelfTestWalk(delay_ms=delay_ms)
        except Exception as e:
            raise PDIS08Error("Self-test walk failed: {0}".format(e)) from e

    # ---- Pin-Specific Measurement Functions ----
    def close_pin1to6(self, delay_ms: float = 200.0) -> None:
        """
        Close relays to measure resistance between pin 1 and pin 6.
        
        Relay mapping:
        - Relay 4 (bit 4): Meter position
        
        Args:
            delay_ms: Settling delay after relay closure in milliseconds
        """
        try:
            self.all_off()
            import time
            time.sleep(0.5)
            self.set_relay(4, True)  # Meter position (relay 5, bit 4)
            self.log.info("RELAY: Waiting 1 second after closing relay 5 (bit 4)")
            time.sleep(3.0)  # 3 second delay after closing relay 5
            time.sleep(delay_ms / 1000.0)
            self.log.info(f"RELAY: Pin1to6 closed with {delay_ms}ms settling delay")
        except Exception as e:
            raise PDIS08Error("Failed to close Pin1to6: {0}".format(e)) from e

    def open_pin1to6(self, delay_ms: float = 100.0) -> None:
        """
        Open relays after pin 1 to pin 6 measurement.
        
        Args:
            delay_ms: Delay after opening relays in milliseconds
        """
        try:
            import time
            self.log.info("RELAY: Waiting 1 second before opening relay 5 (bit 4)")
            time.sleep(1.0)  # 1 second delay before opening relay 5
            self.all_off()
            time.sleep(delay_ms / 1000.0)
            self.log.info(f"RELAY: Pin1to6 opened with {delay_ms}ms delay")
        except Exception as e:
            raise PDIS08Error("Failed to open Pin1to6: {0}".format(e)) from e

    def close_pin2to5(self, delay_ms: float = 200.0) -> None:
        """
        Close relays to measure resistance between pin 2 and pin 5.
        
        Relay mapping:
        - Relay 0 (bit 0): Pin 2
        - Relay 4 (bit 4): Meter position
        - Relay 1 (bit 1): Pin 5
        
        Args:
            delay_ms: Settling delay after relay closure in milliseconds
        """
        try:
            self.all_off()
            import time
            time.sleep(0.05)
            self.set_relay(0, True)  # Pin 2
            self.set_relay(4, True)  # Meter position
            self.set_relay(1, True)  # Pin 5
            time.sleep(delay_ms / 1000.0)
            self.log.info(f"RELAY: Pin2to5 closed with {delay_ms}ms settling delay")
        except Exception as e:
            raise PDIS08Error("Failed to close Pin2to5: {0}".format(e)) from e

    def open_pin2to5(self, delay_ms: float = 100.0) -> None:
        """
        Open relays after pin 2 to pin 5 measurement.
        
        Args:
            delay_ms: Delay after opening relays in milliseconds
        """
        try:
            self.all_off()
            import time
            time.sleep(delay_ms / 1000.0)
            self.log.info(f"RELAY: Pin2to5 opened with {delay_ms}ms delay")
        except Exception as e:
            raise PDIS08Error("Failed to open Pin2to5: {0}".format(e)) from e

    def close_pin3to4(self, delay_ms: float = 200.0) -> None:
        """
        Close relays to measure resistance between pin 3 and pin 4.
        
        Relay mapping:
        - Relay 2 (bit 2): Pin 3
        - Relay 4 (bit 4): Meter position
        - Relay 3 (bit 3): Pin 4
        
        Args:
            delay_ms: Settling delay after relay closure in milliseconds
        """
        try:
            self.all_off()
            import time
            time.sleep(0.05)
            self.set_relay(2, True)  # Pin 3
            self.set_relay(4, True)  # Meter position
            self.set_relay(3, True)  # Pin 4
            time.sleep(delay_ms / 1000.0)
            self.log.info(f"RELAY: Pin3to4 closed with {delay_ms}ms settling delay")
        except Exception as e:
            raise PDIS08Error("Failed to close Pin3to4: {0}".format(e)) from e

    def open_pin3to4(self, delay_ms: float = 100.0) -> None:
        """
        Open relays after pin 3 to pin 4 measurement.
        
        Args:
            delay_ms: Delay after opening relays in milliseconds
        """
        try:
            self.all_off()
            import time
            time.sleep(delay_ms / 1000.0)
            self.log.info(f"RELAY: Pin3to4 opened with {delay_ms}ms delay")
        except Exception as e:
            raise PDIS08Error("Failed to open Pin3to4: {0}".format(e)) from e
