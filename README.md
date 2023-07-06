# RP2040_Micropython_voltage_control
This script let you control the voltage (0.85v ~ 1.30v) of any rp2040 based board using Micropython.

# Warning
Even this script only let you use voltages in a range that is specified by the documentations, there is no guarantee that operating the chip at certain voltage won't damage the board.

The flash can be accessed even under 312 MHz, tho the reliability has not been tested. Also this lead me to suspect that the flash is holding the core frequency back. As in C (using the pico SDK), way higher frequency (over 400 MHz) can be reached. But after 300 MHz, the flash storage started to malfunction. (Can be fixed by divide the clock by 4)

Source: [https://www.youtube.com/watch?v=rU381A-b79c](https://www.youtube.com/watch?v=rU381A-b79c)


# Usage
The POV.py (well, not point of view, but Pico-overvoltaging) is used to control voltage and combined with OCTestMultiThread.py, you may try to overclock and test your boards. 
You can just upload the 2 files to your pico through thonny or other IDE/commands.

Examples:
1. setting voltage. Note: this chip seems to be temperature sensitive, that means, you can achieve higher frequency if you provide lower temperature.
```python
import POV
POV.set_voltage(1.10)
"""
Returns:
True
"""
```
2. find valid inputs for `machine.freq()`.
```python
import POV
POV.find_valid_clocks(270)
"""
Output:
18 MHz is valid
20 MHz is valid
21 MHz is valid
22 MHz is valid
...
264 MHz is valid
266 MHz is valid
267 MHz is valid
268 MHz is valid
"""
```

3. run a multi-threaded test for a given frequency.
```python
import POV
POV.test(270)
"""
Output:
The test goes for 100 rounds total.
Current frequency (OC): 266MHz
Current frequency (OC): 266MHz
Round: 1, time used: 1674 ms, done by thread 0.
Current frequency: 125MHz Temperature: 36.41
Current frequency (OC): 266MHz
Round: 2, time used: 2252 ms, done by thread 1.
Current frequency: 125MHz Temperature: 39.68
Current frequency (OC): 266MHz
Round: 3, time used: 1685 ms, done by thread 0.
Current frequency: 125MHz Temperature: 41.56
...
"""
```
4. run a multi-threaded test for a given frequency non stop.
```python
import POV
POV.test_non_stop(266)
```
5. little example on testing the functionality of the built-in flash
```python
import POV, machine
POV.set_voltage(1.30)

machine.freq(312_000_000)

f = open("some_text.txt", 'w')
f.write("some random data")
f.close()

f = open("some_text.txt")
text = f.read()
f.close()

print(text)
"""
Output:
'some random data'
"""
```
