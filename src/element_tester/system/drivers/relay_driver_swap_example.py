"""
Example: Swapping Between ERB08 and PDIS08 Relay Drivers

This demonstrates how to easily switch between relay drivers with identical interfaces.
Both drivers use the same mcculw library but different port configurations:
- ERB08: Dual-port (relays 0-3 on port 12, relays 4-7 on port 13)
- PDIS08: Single-port (all relays 0-7 on port 10)
"""

# =============================================================================
# METHOD 1: Simple flag-based switching (RECOMMENDED)
# =============================================================================

USE_PDIS = False  # Change to True to use PDIS08 instead of ERB08 (default)

if USE_PDIS:
    from element_tester.system.drivers.relay_mcc_pdis import PDIS08Driver as RelayDriver
    relay = RelayDriver(board_num=0, port_low=10, simulate=True)
else:
    from element_tester.system.drivers.relay_mcc import ERB08Driver as RelayDriver
    relay = RelayDriver(board_num=0, port_low=12, port_high=13, simulate=True)

# Everything below works identically regardless of driver choice
relay.initialize()
relay.set_relay(4, True)
relay.close_pin1to6()
relay.open_pin1to6()
relay.shutdown()


# =============================================================================
# METHOD 2: Configuration-based switching
# =============================================================================

config = {
    "driver": "ERB08",  # "ERB08" (default) or "PDIS08"
    "board_num": 0,
    "simulate": False,
}

if config["driver"] == "PDIS08":
    from element_tester.system.drivers.relay_mcc_pdis import PDIS08Driver as RelayDriver
    relay = RelayDriver(board_num=config["board_num"], port_low=10, simulate=config["simulate"])
else:
    from element_tester.system.drivers.relay_mcc import ERB08Driver as RelayDriver
    relay = RelayDriver(board_num=config["board_num"], port_low=12, port_high=13, simulate=config["simulate"])


# =============================================================================
# METHOD 3: Runtime substitution (for test_runner.py integration)
# =============================================================================

class TestRunner:
    def __init__(self, use_pdis=False, simulate=False):
        if use_pdis:
            from element_tester.system.drivers.relay_mcc_pdis import PDIS08Driver
            self.relay_driver = PDIS08Driver(board_num=0, port_low=10, simulate=simulate)
        else:
            # DEFAULT: ERB08
            from element_tester.system.drivers.relay_mcc import ERB08Driver
            self.relay_driver = ERB08Driver(
                board_num=0, port_low=12, port_high=13, simulate=simulate
            )
        
        self.relay_driver.initialize()
    
    def run_test(self):
        # Same code works for both drivers
        self.relay_driver.all_off()
        self.relay_driver.close_pin1to6()
        # ... perform measurement ...
        self.relay_driver.open_pin1to6()


# =============================================================================
# METHOD 4: Simple one-line swap at top of file
# =============================================================================

# DEFAULT (ERB08):
# from element_tester.system.drivers.relay_mcc import ERB08Driver as RelayDriver

# TO USE PDIS08, JUST CHANGE TO:
# from element_tester.system.drivers.relay_mcc_pdis import PDIS08Driver as RelayDriver

# Then create driver instance (same for both):
# relay = RelayDriver(board_num=0, port_low=12, port_high=13, simulate=True)
# Note: PDIS08 ignores port_high, uses port_low for all relays


# =============================================================================
# IDENTICAL API METHODS (same for both drivers)
# =============================================================================
"""
Lifecycle:
    initialize()          - Initialize hardware, all relays OFF
    shutdown()            - Safe shutdown (all OFF, close connection)

Basic Control:
    set_relay(bit, on)    - Set individual relay ON/OFF
    all_off()             - Turn all relays OFF
    all_on()              - Turn all relays ON
    apply_mapping(on, off)- Apply relay configuration
    self_test_walk(ms)    - Walk through relays for testing

Pin-Specific:
    close_pin1to6(ms)     - Close relays for pin 1-6 measurement
    open_pin1to6(ms)      - Open after pin 1-6 measurement
    close_pin2to5(ms)     - Close relays for pin 2-5 measurement
    open_pin2to5(ms)      - Open after pin 2-5 measurement
    close_pin3to4(ms)     - Close relays for pin 3-4 measurement
    open_pin3to4(ms)      - Open after pin 3-4 measurement
"""
