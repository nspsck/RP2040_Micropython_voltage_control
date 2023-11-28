import machine
from micropython import const

"""
Useful cheat sheets:

# Content in _VREG_AND_CHIP_RESET_BASE (0x40064000)
ROK = const(0x00001000) #[12] ROK (0): regulation status
VSEL = const(0x000000f0) #[7:4] VSEL (0xb): output voltage select
HIZ = const(0x00000002) #[1] HIZ (0): high impedance mode select
EN = const(0x00000001) #[0] EN (1): enable

Everything else in the content of this address is unused.

Unused bit combinations to control the voltage:
_UNUSED_1 = const(0b0000)
_UNUSED_2 = const(0b0001)
_UNUSED_3 = const(0b0010)
_UNUSED_4 = const(0b0011)
_UNUSED_5 = const(0b0100)
_UNUSED_6 = const(0b0101)

Trying to use these bit combinations will result a hard reset.
Using 0.85v could also cause a hard reset.

"""

# The voltage and chip reset control address
_VREG_AND_CHIP_RESET_BASE = const(0x40064000)

# Possible voltage
VOLTAGE_CONSTANTS = [
    const(0b0110),  # < 0.85v
    const(0b0111),  # < 0.90v
    const(0b1000),  # < 0.95v
    const(0b1001),  # < 1.00v
    const(0b1010),  # < 1.05v
    const(0b1011),  # < 1.10v
    const(0b1100),  # < 1.15v
    const(0b1101),  # < 1.20v
    const(0b1110),  # < 1.25v
    const(0b1111),  # < 1.30v
]

# The masks to extract/replace the voltage settings
_CLEAN_VSEL_VALUE_MASK = const(0xffffff0f)
_CLEAN_RAMDOM_BITS_MASK = const(0x000000f0)

def voltage_control_bits(volt_bits):
    return (volt_bits << 4) & _CLEAN_RAMDOM_BITS_MASK

def clean_vsel_bits():
    return machine.mem32[_VREG_AND_CHIP_RESET_BASE] & _CLEAN_VSEL_VALUE_MASK

def isclose(a, b):
    return abs(a - b) < 0.004

def set_voltage_bits(volt):
    for idx, value in enumerate(VOLTAGE_CONSTANTS):
        if isclose(volt, 0.85 + idx * 0.05):
            return clean_vsel_bits() ^ voltage_control_bits(value)

    raise ValueError("Unsupported inputs. Valid inputs have to be close to: 0.85 ~ 1.30, with a 0.05 increment each step. Voltage unchanged.")

def set_voltage(volt):
    try:
        machine.mem32[_VREG_AND_CHIP_RESET_BASE] = set_voltage_bits(volt)
        return True
    except ValueError as e:
        print("Error: ", str(e))
        return False
    
def test_non_stop(freq):
    if freq >= 1000:
        print("The unit used is MHz, please try again.")
        return
    elif freq <= 0:
        print("The input must be positiv")
        return
    try:
        import OCTestMultiThread as OC
        OC.run_non_stop(freq)
    except ImportError as e:
        print("ImportError", str(e))
        print("You can get the test on: https://github.com/nspsck/RP2040_Micropython_voltage_control")
        
def test(freq):
    if freq >= 1000:
        print("The unit used is Mhz, please try again.")
        return
    elif freq <= 0:
        print("The input must be positiv")
        return
    try:
        import OCTestMultiThread as OC
        OC.run(freq)
    except ImportError as e:
        print(str(e))
        print("You can get the test on: https://github.com/nspsck/RP2040_Micropython_voltage_control")
        
def find_valid_clocks(limit):
    try:
        import OCTestMultiThread as OC
        OC.find_clock_freq(limit)
    except ImportError as e:
        print(str(e))
        print("You can get the test on: https://github.com/nspsck/RP2040_Micropython_voltage_control")
        
