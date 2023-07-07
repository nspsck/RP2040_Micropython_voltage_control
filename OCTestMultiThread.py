import machine, time, random, _thread
from micropython import const
from machine import Pin

"""
This test assumes that your board has a led on the pin 25.

Notes:
1. The Pico can only run the second thread on core1. The Pico is
only capble running 2 threads atm.

2. The temperature sensor is not accurate by default. for
details please visit: https://youtu.be/YeY0SY8iYxk?t=132
Or check the official datasheet yourself. (Chapter: 4.9.5)
https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf

3. Note the lock for frequencies is obsolete. I just added it for
fun. Why only use one lock if you can have two. C:
PS. It actually slows the other thread down for a tiny little bit.

"""

_BASE_FREQUENCY = const(125_000_000)
_REST_FREQUENCY = const(20_000_000) #unused

led = Pin(25, Pin.OUT)
count = 0
ledStart = 0
ledEnd = 0
temperature = 0
turbo_freq = 0
run_count = 0

lock = _thread.allocate_lock()
quitting_lock = _thread.allocate_lock()
freqlock = _thread.allocate_lock()

def is_valid_freq(freq):
    freq *= 1000000
    try:
        machine.freq(freq)
    except ValueError as e:
        return False
    return True


def find_clock_freq(limit):
    for i in range(limit):
        if is_valid_freq(i):
            print("%d MHz is valid" % i)
#     return [x for x in range(limit) if is_valid_freq(x)]
    


def print_info(count, end, start, temperature, id):
    print("Round: %d, time used: %d ms, done by thread %d." 
          % (count, end - start, id))
    temperature = 27- (machine.ADC(4).read_u16() * 3.3 / (65535)- 0.706)/0.001721
    print("Current frequency: %dMHz Temperature: {:.2f}".format(round(temperature, 2)) 
          % (machine.freq() // 1000000))
    

def stresstest_vanilla(random):
    for i in range(0,100000):
        random.random() * random.random()
        
        
def stresstest_led(ledEnd, ledStart, random):
    for x in range(0,100000):
        random.random() * random.random()
        #toggle LED to verify runtime
        ledEnd = time.ticks_ms()
        if (ledEnd - ledStart >= 500):
            led.toggle()
            ledStart = time.ticks_ms()
    return ledEnd, ledStart


def change_frequency(freq):
    freqlock.acquire()
    machine.freq(freq)
    freqlock.release()
    

def stresstest(random, functionID):
    global count
    global ledEnd
    global ledStart
    
    #calculate the time used by running the stress test
    change_frequency(turbo_freq)
    print("Current frequency (OC): %dMHz" 
          % (machine.freq() // 1000000))
    start = time.ticks_ms()
    if (functionID == 0):
        stresstest_vanilla(random)
    elif (functionID == 1):
        ledEnd, ledStart = stresstest_led(ledEnd, ledStart, random)
    else:
        pass
    end = time.ticks_ms()
    change_frequency(_BASE_FREQUENCY)
    
    #output the result and the condition of the chip
    lock.acquire()
    count = count + 1
    print_info(count, end, start, temperature, functionID)
    lock.release()
    

def test_thread_non_stop():
    global count
    count = 0
    while True:
        stresstest(random, 1)
        

def run_non_stop(freq):
    global turbo_freq
    global count
    count = 0
    
    # Test to see if the frequency is supported
    turbo_freq = int(freq * 1000000)
    try:
        change_frequency(turbo_freq)
    except ValueError as e:
        freqlock.release()
        print("ValueError: can not change frequency to %dMHz" 
              % (turbo_freq // 1000000))
        print("Aborted.")
        return e

    _thread.start_new_thread(test_thread_non_stop, ())
    while True:
        stresstest(random, 0)
        
        
def test_thread():
    global run_count
    # this lock ensures that the thread on core1 can terminate
    quitting_lock.acquire()
    while True:
        lock.acquire()
        run_count += 1
        lock.release()
        if run_count > 100:
            break 
        stresstest(random, 1)
    try:
        _thread.exit()
    except SystemExit as e:
        quitting_lock.release()
        pass
            

def run(freq):
    global turbo_freq
    global count
    global run_count
    
    # reset for next run    
    run_count = 0
    count = 0
    
    # Test to see if the frequency is supported
    if is_valid_freq(freq):
        turbo_freq = int(freq * 1000000)
    else:
        print("ValueError: can not change frequency to %dMHz" 
              % freq)
        print("Aborted.")
        return
    
    print("The test goes for 100 rounds total.")
    
    # this means that the task on core1 has been finished.
    quitting_lock.acquire()
    quitting_lock.release()
    
    _thread.start_new_thread(test_thread, ())
    
    while True:
        lock.acquire()
        run_count += 1
        lock.release()
        if run_count > 100:
            break  
        stresstest(random, 0)
    
    # this prevents the main thread terminates before core1. 
    # if 
    quitting_lock.acquire()
    quitting_lock.release()
        


