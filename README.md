# Status as of January 25, 2022

Now that I've learned a bit more Python, I've decided to create a package that works on top of py65 rather than modifies it.  That let's you add the 65816 simulation while maintaining your py65 installation intact.  See [py65816](https://github.com/tmr4/py65816) for a version with my debug window.  This is where I'll be making future updates to the 65816 simulation.

# Add support for the 65C816 to py65

Py65 (https://github.com/mnaberez/py65) is a great simulator for the 6502.  Recently I added support for interrupts (https://github.com/tmr4/py65_int) and a debug window (https://github.com/tmr4/py65_debug_window).  After success with these modifications, I decided to try adding support for the 65C816. Luckily, py65 is open-source and enhancing it isn't very difficult.

This repository provides a framework for adding support for the 65C816 to py65.  I've included the modules I've developed to simulate and test the 65C816.  As noted below, a few modifications are needed to the core py65 modules as well.

# Screenshot

![Screenshot of py65 running Liara Forth on a simulated 65C816](img/py65_65c816.png)

# Contents

I've included the main device module, `mpu65c816.py`, to add simulation support for the 65C816 to py65.  I've also include several modules for testing the 65C816 simulation.  So far these have been derived largely from similarly named py65 test modules.  I've also included two binary files, `liara.bin` and `of816_forth.bin`.  I modified the former from Scot W. Stevenson's Liara Forth (https://github.com/scotws/LiaraForth) to work with py65 simulating the 65C816.  The later is a port for py65 of Michael Guidero's OF816 (https://github.com/mgcaret/of816).  Note that I'm a Python newbie and appreciate any feedback to make these better.

* `mpu65c816.py`

The 65C816 device.

* `test_mpu65c816_emulation.py`, `test_mpu65c816_native_8.py` and  `test_mpu65c816_native_16.py`

The main unit test modules for the 65C816, emulation and native 8-bit and 16-bit modes.  These are far from complete but the 65816 simulation passes all of them.

* `test_mpu65816_Common6502.py`

Unit tests for 65C816 emulation mode.
  
* `test_mpu65816_Common65c02.py`

Additional 65C02 based unit tests for 65C816 emulation mode.

* `liara.bin`

A modified version of Scot W. Stevenson's Liara Forth (https://github.com/scotws/LiaraForth) for testing.  Liara Forth is designed to run on the Western Design Center's W65C265SXB development board (https://www.westerndesigncenter.com/wdc/documentation/W65C265SXB.pdf).  I've modified the Liara Forth binary to interface with alternate I/O addresses rather than those used by the development board.

* `of816_forth.bin`

A compiled binary of [OF816](https://github.com/mgcaret/of816), by Michael Guidero, for the [py65816 platform](https://github.com/tmr4/of816/blob/master/platforms/py65816/).  OF816 provides a more robust test of the simulation as it uses more features and can operate outside bank 0.  This port has the dictionary located in bank 1.

# Modifications to core py65 modules

The following modifications are needed for py65 to simulate the 65C816:

1. `monitor.py`

* Add a reference to new 65C816 MPU class `from devices.mpu65c816 import MPU as CMOS65C816`
* Add the `'65C816': CMOS65C816` pair to the `Microprocessors` dictionary.

# License

The `mpu65c816.py`, `test_mpu65816_Common6502.py` and `test_mpu65816_Common65c02.py` modules contain large portions of code from or derived from py65 which is covered by a BSD 3-Clause License.  I've included that license as required.

# Running the 65C816 Unit Tests

You can run the unit tests with `python -m unittest test_mpu65c816_emulation.py` to run 65816 emulation mode tests.  Use `python -m unittest test_mpu65c816_native_8.py` to run the 65816 native mode 8-bit tests.  The 65C816 simulation passes the py65 6502- and 65C02-based test (507 in total) in emulation mode.  Some of tests were modified to run properly with the new device.  I still have to create the tests for native mode operations (not a small task).  I expect these to take some time and I expect these will turn up many errors in my code.

# Testing the 65C816 Simulation with Liara Forth

It wasn't easy to find a sizable program to test with the new 65C816 simulation.  You can run the slightly modified version of Liara Forth with `python monitor.py -m 65c816 -l liara.bin -g 5000 -i fff0 -o fff1`.

# Testing the 65C816 Simulation with OF816

I forked [OF816](https://github.com/mgcaret/of816), by Michael Guidero, and created a new platform for the 65816 on py65, (https://github.com/tmr4/of816/blob/master/platforms/py65816/).  OF816 is another sizable program to test with the new 65C816 simulation.  OF816 is an attractive test program because it uses many more 65816 features than Liara Forth.  As such I've been able to track down more errors in the simulation.  You can run py65816 version of OF816 with `python monitor.py -m 65c816 -r of816_forth.bin -i 7FC0 -o 7FE0`.

# Limitations

1. The new 65C816 device is largely untested.  I plan to update it as I work on supporting hardware and code.  Use at your own risk.  Some know issues:

* FIXED: ROL and ROR haven't been updated for a 16 bit accumulator.
* Extra cycle counts haven't been considered for any new to 65816 opcodes.
* ADC and SBC in decimal mode are likely invalid in 16 bit.
* FIXED: Native mode hasn't been tested outside of bank 0.  Assume it will fail for this until it is tested.  Bank 1 successfully tested with OF816.
* Currently only 3 banks of memory are modeled, by py65 default, but this can easily be changed.
* The simulation is meant to emulate the actual W65C816.  Modelling so far has been based on the 65816 Programming Manual only.  I intend to test at least some code against the W65C265SXB development board.
* Currently no way to break to the py65 monitor.  I've successfully run Liara Forth and OF816 with a version of my debug window (https://github.com/tmr4/py65_debug_window) without the interrupt code.
* Register wrapping of Direct page addressing modes need tested.

2. Liara Forth now runs in py65 with the new 65C816 device, but it hasn't been extensively tested.  Liara Forth runs entirely in bank 0.  There is no way to break to the monitor since Liara Forth was designed to run on hardware only (you can use my debug window with it).  It can only be ended with a control-C.

3. I've successfully run a non-interrupt version of my own 6502 Forth in the new 65C816 device in emulation mode.  This isn't surprising since much of the code comes from py65 6502 and 65C02 devices.  I expect an interrupt version of it will run as well, but I haven't tested this.  I expect that many 6502 programs will run in emulation mode.  Note however, that there are differences between the 65C816 operating in emulation mode and the 6502/65C02 that could cause problems with your program.

4. OF816 now runs in py65 with the new 65C816 device with the py65816 platform.  I've successfully run a version running entirely in bank 0 and one with the dictionary in bank 1.  Neither has been extensively tested.

# Status

* Initial commit: January 11, 2022
* As of January 21, 2022:
    * Successfully tested my 65C02 Forth in emulation mode
    * Was able to run Liara Forth in native mode in block 0.
    * FIXED: (Many words cause it to crash (likely due to one of the limitations listed above).)
    * FIXED: Currently all numbers print out as 0.  After verifying that Liara Forth works properly on the W65C265SXB development board, using my debug window (https://github.com/tmr4/py65_debug_window) I tracked the issue down to UM* where the high byte in the high cell of the result is zero (for example $1234 * $1234 = $14b5a90 but my 65816 simulation is yielding $04b5a90).  I couldn't find any obvious errors in my code after examining each line code for the Liara Forth UM*.  I'm ending up with a 24 bit value rather than a 32 bit one, so that may give me a clue to what's happening. Update: turns out I was shifting the high byte by the byte mask ($ffff) instead of the byte width ($08)! Oops.
    * Was able to start OF816 in native mode in bank 0 and with the dictionary in bank 1.  
        * FIXED: Currently input is accepted but not properly interpreted.
        * FIXED: Numbers aren't interpreted properly, but coded ones (-1, 0, 1, 2, 3) work as expected.
    * Successfully ran 507 unit tests in emulation mode, 506 unit tests in native 8-bit mode and 226 unit tests in native 16-bit mode.

# Next Steps

* COMPLETED: Resolve simulator issues with running Liara Forth.  I view this as a robust test of the 65816 simulator, other than bank switching, which Liara Forth doesn't handle out of the box.  Some hardware specific Liara Forth features will not work with the simulator (KEY? for example which is hardwired to a W65C265SXB development board specific address indicating whether a key has been pressed).
* COMPLETE: I ported [OF816](https://github.com/tmr4/of816) to get another test program.  Working in bank 0 and with the dictionary in bank 1 as in the [W65C816SXB platform](https://github.com/tmr4/of816/blob/master/platforms/W65C816SXB/W65C816SXB.s).
    * Older entries:
        * The port starts properly in py65 but input is not yet properly interpreted by the system.  Tracking the error is made more difficult in that much of the program is coded in Forth, making it more difficult to debug in py65.
        * With this I fixed several errors with several instructions, mainly those involving long address modes, but also the TSB TRB REP JML instructions.  Still a problem with number input (FIXED: I had neglected to properly calculated the negative flag when dealing with s 16 bit accumulator).  With some clever breakpoint setting, it is easier to debug once you understand the program.
* Add native mode unit tests.
  * Native mode, 8-bit tests: In progress. Added 506 unit tests modified from the emulation mode tests.
  * Native mode, 16-bit and mixed-bit tests: Just going with brut force.  226 unit tests added so far for ADC AND ASL BIT CMP CPX CPY DEC DEX DEY SBC.  These have already proven their worth by pointing out a problem with how I calculated the overflow flag in ADC.  Still the going is slow.  
    * Older entry: Still looking for an easy way to do this.  All of the 65816 testing frameworks I've found so far require an amount of conversion almost equal to modifying the emulation mode tests for native mode.

* As of January 21, 2022:
    * I'll probably continue updates to the simulation as I work on my hardware build.  I expect the simulation to be functional, having run several large programs successfully.  However, as noted above, much work remains.  I'll continue to add unit tests from time to time but this isn't a high priority for me right now.
