import unittest
import sys
import devices.mpu65c816
from tests.devices.test_mpu65816_Common6502 import Common6502Tests
from tests.devices.test_mpu65816_Common65c02 import Common65C02Tests

# 2 tests
class MPUTests(unittest.TestCase, Common6502Tests, Common65C02Tests):
#class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests - Emulation Mode """

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Emulation Mode

    # Reset

    def test_reset_sets_registers_to_initial_states(self):
        mpu = self._make_mpu()
        mpu.reset()
        #self.assertEqual(0xFF, mpu.sp)
        self.assertEqual(0, mpu.a)
        self.assertEqual(0, mpu.x)
        self.assertEqual(0, mpu.y)
        self.assertEqual(mpu.BREAK | mpu.UNUSED, mpu.p)

    # ADC Absolute

    def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self.assertEqual(0x10000, len(mpu.memory))

        mpu.memory[0xC000] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # BRK

    def test_brk_clears_decimal_flag(self):
        mpu = self._make_mpu()
        mpu.p = mpu.DECIMAL
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    def test_brk_interrupt(self):
        mpu = self._make_mpu()
        mpu.p = 0x60 # bits 4 and 5 always set in emulation mode
        self._write(mpu.memory, 0xFFFE, (0x00, 0x04))

        self._write(mpu.memory, 0x0000, (0xA9, 0x01,   # LDA #$01
                                         0x00, 0xEA,   # BRK + skipped byte
                                         0xEA, 0xEA,   # NOP, NOP
                                         0xA9, 0x03))  # LDA #$03

        self._write(mpu.memory, 0x0400, (0xA9, 0x02,   # LDA #$02
                                         0x40))        # RTI

        mpu.step()  # LDA #$01
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x0002, mpu.pc)
        mpu.step()  # BRK
        self.assertEqual(0x0400, mpu.pc)
        mpu.step()  # LDA #$02
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0x0402, mpu.pc)
        mpu.step()  # RTI

        self.assertEqual(0x0004, mpu.pc)
        mpu.step()  # A NOP
        mpu.step()  # The second NOP

        mpu.step()  # LDA #$03
        self.assertEqual(0x03, mpu.a)
        self.assertEqual(0x0008, mpu.pc)

    def test_brk_pushes_pc_plus_2_and_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        mpu.p = mpu.UNUSED
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

        self.assertEqual(0xC0, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x02, mpu.memory[0x1FE])  # PCL
        self.assertEqual(mpu.BREAK | mpu.UNUSED, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)

        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p)

    # IRQ and NMI handling (very similar to BRK)

    def test_irq_pushes_pc_and_correct_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        mpu.p = mpu.UNUSED
        self._write(mpu.memory, 0xFFFA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        mpu.pc = 0xC123
        mpu.irq()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0xC1, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FE])  # PCL
        self.assertEqual(mpu.UNUSED, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)
        self.assertEqual(mpu.UNUSED | mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector(self):
        mpu = self._make_mpu()
        mpu.p = mpu.UNUSED
        self._write(mpu.memory, 0xFFFA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        mpu.pc = 0xC123
        mpu.nmi()
        self.assertEqual(0x7788, mpu.pc)
        self.assertEqual(0xC1, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FE])  # PCL
        self.assertEqual(mpu.UNUSED, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)
        self.assertEqual(mpu.UNUSED | mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    # JMP Indirect

    def test_jmp_ind_does_not_have_page_wrap_bug(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x10FF, (0xCD, 0xAB))
        # $0000 JMP ($10FF)
        self._write(mpu.memory, 0, (0x6c, 0xFF, 0x10))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # JSR

    def test_jsr_pushes_pc_plus_2_and_sets_pc(self):
        mpu = self._make_mpu()
        # $C000 JSR $FFD2
        self._write(mpu.memory, 0xC000, (0x20, 0xD2, 0xFF))
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0xFFD2, mpu.pc)
        self.assertEqual(0xFD,   mpu.sp)
        self.assertEqual(0xC0,   mpu.memory[0x01FF])  # PCH
        self.assertEqual(0x02,   mpu.memory[0x01FE])  # PCL+2

    # RTI

    def test_rti_forces_break_and_unused_flags_high(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FD, (0x00, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.sp = 0xFC

        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(mpu.UNUSED, mpu.p & mpu.UNUSED)

    def test_rti_restores_status_and_pc_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FD, (0xFC, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.sp = 0xFC

        mpu.step()
        self.assertEqual(0xC003, mpu.pc)
        self.assertEqual(0xFC,   mpu.p)
        self.assertEqual(0xFF,   mpu.sp)

    # PHA

    def test_pha_pushes_a_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        # $0000 PHA
        mpu.memory[0x0000] = 0x48
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xFE, mpu.sp)

    # PHP

    def test_php_pushes_processor_status_and_updates_sp(self):
        for flags in range(0x100):
            mpu = self._make_mpu()
            mpu.p = flags | mpu.BREAK | mpu.UNUSED
            # $0000 PHP
            mpu.memory[0x0000] = 0x08
            mpu.step()
            self.assertEqual(0x0001, mpu.pc)
            self.assertEqual((flags | mpu.BREAK | mpu.UNUSED),
                             mpu.memory[0x1FF])
            self.assertEqual(0xFE, mpu.sp)

    # PHX

    def test_phx_pushes_x_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        # $0000 PHX
        mpu.memory[0x0000] = 0xDA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.x)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xFE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PHY

    def test_phy_pushes_y_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        # $0000 PHY
        mpu.memory[0x0000] = 0x5A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.y)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xFE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PLA

    def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.a)
        self.assertEqual(0xFF,   mpu.sp)

    # PLP

    def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLP
        mpu.memory[0x0000] = 0x28
        mpu.memory[0x01FF] = 0xBA  # must have BREAK and UNUSED set
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xBA,   mpu.p)
        self.assertEqual(0xFF,   mpu.sp)

    # PLX

    def test_plx_pulls_top_byte_from_stack_into_x_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLX
        mpu.memory[0x0000] = 0xFA
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.x)
        self.assertEqual(0xFF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # PLY

    def test_ply_pulls_top_byte_from_stack_into_y_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLY
        mpu.memory[0x0000] = 0x7A
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.y)
        self.assertEqual(0xFF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # RTS

    def test_rts_restores_pc_and_increments_then_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTS
        mpu.memory[0x0000] = 0x60
        self._write(mpu.memory, 0x01FE, (0x03, 0xC0))  # PCL, PCH
        mpu.pc = 0x0000
        mpu.sp = 0xFD

        mpu.step()
        self.assertEqual(0xC004, mpu.pc)
        self.assertEqual(0xFF,   mpu.sp)

    def test_rts_wraps_around_top_of_memory(self):
        mpu = self._make_mpu()
        # $1000 RTS
        mpu.memory[0x1000] = 0x60
        self._write(mpu.memory, 0x01FE, (0xFF, 0xFF))  # PCL, PCH
        mpu.pc = 0x1000
        mpu.sp = 0xFD

        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0xFF,   mpu.sp)




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

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _get_target_class(self):
        return devices.mpu65c816.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
