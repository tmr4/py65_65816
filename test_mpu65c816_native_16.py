import unittest
import sys
import devices.mpu65c816

# x tests
class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests - Native Mode - 16 Bit"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Native Mode - 16 bit

    # ADC Absolute

    def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0

        self.assertEqual(0x30000, len(mpu.memory))

        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute, X-Indexed

    def test_adc_bcd_off_abs_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_abs_x_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFF, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute, Y-Indexed

    def test_adc_bcd_off_abs_y_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_abs_y_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFF, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page

    def test_adc_bcd_off_dp_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_dp_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page, X-Indexed

    def test_adc_bcd_off_dp_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_dp_x_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_x_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page Indirect, Indexed (X)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page, Indirect

    def test_adc_bcd_off_dp_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_dp_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_overflow_cleared_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_cleared_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page Indexed, Indirect (Y)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0000, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        mpu.y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Immediate

    def test_adc_bcd_off_immediate_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC #$0000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC #$0000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_immediate_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC #$FEFF
        self._write(mpu.memory, 0x0000, (0x69, 0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC #$FFFF
        self._write(mpu.memory, 0x0000, (0x69, 0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC #$01
        self._write(mpu.memory, 0x000, (0x69, 0x01, 0X00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC #$FFFF
        self._write(mpu.memory, 0x000, (0x69, 0xff, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC #$01
        self._write(mpu.memory, 0x000, (0x69, 0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC #$FFFF
        self._write(mpu.memory, 0x000, (0x69, 0xff, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        # $0000 ADC #$4000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Absolute

    def test_and_absolute_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $ABCD
        self._write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_absolute_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $ABCD
        self._write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Absolute, X-Indexed

    def test_and_abs_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3d, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3d, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Absolute, Y-Indexed

    def test_and_abs_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page

    def test_and_dp_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $0010
        self._write(mpu.memory, 0x0000, (0x25, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $0010
        self._write(mpu.memory, 0x0000, (0x25, 0x10))
        self._write(mpu.memory, 0x0010, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page, X-Indexed

    def test_and_dp_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $0010,X
        self._write(mpu.memory, 0x0000, (0x35, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_x_all_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $0010,X
        self._write(mpu.memory, 0x0000, (0x35, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page Indirect, Indexed (X)

    def test_and_ind_indexed_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x21, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_ind_indexed_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x21, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page, Indirect

    def test_and_dp_ind_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_ind_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page Indexed, Indirect (Y)

    def test_and_indexed_ind_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x31, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_indexed_ind_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x31, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Immediate

    def test_and_immediate_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND #$00
        self._write(mpu.memory, 0x0000, (0x29, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_immediate_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND #$AA
        self._write(mpu.memory, 0x0000, (0x29, 0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ASL Accumulator

    def test_asl_accumulator_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_accumulator_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x7FFF
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFFE, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFFE, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_asl_accumulator_80_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x8000
        mpu.p &= ~(mpu.ZERO)
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # ASL Absolute

    def test_asl_absolute_sets_z_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_absolute_sets_n_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x80, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Absolute, X-Indexed

    def test_asl_abs_x_indexed_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_abs_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Direct Page

    def test_asl_dp_sets_z_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_dp_sets_n_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_dp_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_dp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Direct Page, X-Indexed

    def test_asl_dp_x_indexed_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_dp_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_dp_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.a = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_dp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.a = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)










    # *** TODO: probably makes sense to move the relevant values to the high byte or perhaps both since we've already tested the low byte in 8 bit ***
    # SBC Absolute

    def test_sbc_abs_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute, X-Indexed

    def test_sbc_abs_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute, Y-Indexed

    def test_sbc_abs_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page

    def test_sbc_dp_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # => SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # => SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page, X-Indexed

    def test_sbc_dp_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page Indirect, Indexed (X)

    def test_sbc_ind_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page, Indirect

    def test_sbc_dp_ind_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page Indexed, Indirect (Y)

    def test_sbc_ind_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Immediate

    def test_sbc_imm_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xE9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC #$01
        self._write(mpu.memory, 0x0000, (0xE9, 0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xE9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC #$02
        self._write(mpu.memory, 0x0000, (0xE9, 0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

#    def test_sbc_bcd_on_immediate_0a_minus_00_carry_set(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.p |= mpu.CARRY
#        mpu.a = 0x0a
#        # $0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x0a, mpu.a)
#        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
#
#    def test_sbc_bcd_on_immediate_9a_minus_00_carry_set(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.p |= mpu.CARRY
#        mpu.a = 0x9a
#        #$0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x9a, mpu.a)
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
#
#    def test_sbc_bcd_on_immediate_00_minus_01_carry_set(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.p |= mpu.OVERFLOW
#        mpu.p |= mpu.ZERO
#        mpu.p |= mpu.CARRY
#        mpu.a = 0x00
#        # => $0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x01, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x99, mpu.a)
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(0, mpu.p & mpu.CARRY)
#
#    def test_sbc_bcd_on_immediate_20_minus_0a_carry_unset(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.a = 0x20
#        # $0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x0a, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x1f, mpu.a)
#        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)








    # Test Helpers

    def _make_mpu(self, *args, **kargs):
        klass = self._get_target_class()
        mpu = klass(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x30000 * [0xAA]

        # set native mode
        mpu.pCLR(mpu.CARRY)
        mpu.inst_0xfb() # XCE
        mpu.pCLR(mpu.CARRY) # many 6502 based tests expect the carry flag to be clear
        mpu.pCLR(mpu.MS)
        mpu.pCLR(mpu.IRS)

        # py65 mpus have sp set to $ff, I've modeled the 65816
        # based on the physical chip which requires sp to be set
        # in software.  The core tests assume sp is set to $ff,
        # so we have to set sp here
        mpu.sp = 0x1ff 
        
        return mpu

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _get_target_class(self):
        return devices.mpu65c816.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
