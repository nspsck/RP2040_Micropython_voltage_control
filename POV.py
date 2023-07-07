import machine
from micropython import const

"""
Useful cheat sheets:

# Content in _VREG_AND_CHIP_RESET_BASE (0x40064000)
ROK = const(0x00001000) #[12] ROK (0): regulation status
VSEL = const(0x000000f0) #[7:4] VSEL (0xb): output voltage select
HIZ = const(0x00000002) #[1] HIZ (0): high impedance mode select
EN = const(0x00000001) #[0] EN (1): enable

Everything else is unused.

"""

class VoltageError(Exception):
    pass


# The voltage and chip reset control address
_VREG_AND_CHIP_RESET_BASE = const(0x40064000)

# Possible voltage
_VREG_VOLTAGE_0_85 = const(0b0110)    #< 0.85v
_VREG_VOLTAGE_0_90 = const(0b0111)    #< 0.90v
_VREG_VOLTAGE_0_95 = const(0b1000)    #< 0.95v
_VREG_VOLTAGE_1_00 = const(0b1001)    #< 1.00v
_VREG_VOLTAGE_1_05 = const(0b1010)    #< 1.05v
_VREG_VOLTAGE_1_10 = const(0b1011)    #< 1.10v
_VREG_VOLTAGE_1_15 = const(0b1100)    #< 1.15v
_VREG_VOLTAGE_1_20 = const(0b1101)    #< 1.20v
_VREG_VOLTAGE_1_25 = const(0b1110)    #< 1.25v
_VREG_VOLTAGE_1_30 = const(0b1111)    #< 1.30v

# The masks to extract/replace the voltage settings
_CLEAN_VSEL_VALUE_MASK = const(0xffffff0f)
_CLEAN_RAMDOM_BITS_MASK = const(0x000000f0)


def read_mem(mem_addr):
    return machine.mem32[mem_addr]


def voltage_control_bits(volt_bits):
    return (volt_bits << 4) & _CLEAN_RAMDOM_BITS_MASK


def clean_vsel_bits():
    return read_mem(_VREG_AND_CHIP_RESET_BASE) & _CLEAN_VSEL_VALUE_MASK


def isclose(a, b):
    if abs(a - b) < 0.004:
        return True
    else:
        return False
    

def set_voltage_bits(volt):

    if isclose(volt, 0.85):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_0_85)

    elif isclose(volt, 0.90):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_0_90)

    elif isclose(volt, 0.95):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_0_95)

    elif isclose(volt, 1.00):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_00)

    elif isclose(volt, 1.05):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_05)

    elif isclose(volt, 1.10):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_10)

    elif isclose(volt, 1.15):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_15)

    elif isclose(volt, 1.20):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_20)

    elif isclose(volt, 1.25):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_25)

    elif isclose(volt, 1.30):
        return clean_vsel_bits() ^ voltage_control_bits(_VREG_VOLTAGE_1_30)

    else:
        raise ValueError("Unsupported inputs. Valid inputs has to be close to: 0.85 ~ 1.30, with a 0.05 increment each step. Voltage unchanged.")


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
        print("You can get the test on: ")
        

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
        
                
                
