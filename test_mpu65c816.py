import unittest
import sys
import devices.mpu65c816
from tests.devices.test_mpu65816_Common6502 import Common6502Tests
from tests.devices.test_mpu65816_Common65c02 import Common65C02Tests

# 2 tests
class MPUTests(unittest.TestCase, Common6502Tests, Common65C02Tests):
#class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Emulation Mode

    # JMP Indirect

    def test_jmp_ind_does_not_have_page_wrap_bug(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x10FF, (0xCD, 0xAB))
        # $0000 JMP ($10FF)
        self._write(mpu.memory, 0, (0x6c, 0xFF, 0x10))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes


    # Test Helpers

    def _make_mpu(self, *args, **kargs):
        klass = self._get_target_class()
        mpu = klass(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x10000 * [0xAA]

        # py65 mpus have sp set to $ff, I've modeled the 65816
        # based on the physical chip which requires sp to be set
        # in software.  The core tests assume sp is set to $ff,
        # so we have to set sp here
        mpu.sp = 0xff 
        
        return mpu

    def _get_target_class(self):
        return devices.mpu65c816.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
