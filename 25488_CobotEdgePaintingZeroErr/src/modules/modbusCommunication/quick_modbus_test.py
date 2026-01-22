#!/usr/bin/env python3
"""
Quick Modbus Test - Tests if we can communicate with Xinje relay
Usage: python3 quick_modbus_test.py
"""

def test():
    try:
        import minimalmodbus
        import serial

        port = '/dev/ttyUSB0'
        baudrate = 57600
        slave_id = 1

        print(f"Testing Modbus on {port}...")
        print(f"Baudrate: {baudrate}, Slave ID: {slave_id}")

        # Create instrument
        instrument = minimalmodbus.Instrument(port, slave_id)
        instrument.serial.baudrate = baudrate
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1
        instrument.mode = minimalmodbus.MODE_RTU

        print("\nReading outputs (Y0-Y7)...")
        for i in range(8):
            try:
                value = instrument.read_bit(0x0008 + i, functioncode=1)
                print(f"  Y{i}: {'ON' if value else 'OFF'}")
            except Exception as e:
                print(f"  Y{i}: ERROR - {e}")

        print("\nTesting write - Turning Y0 ON...")
        instrument.write_bit(0x0008, 1)
        print("  Success!")

        print("\nTesting write - Turning Y0 OFF...")
        instrument.write_bit(0x0008, 0)
        print("  Success!")

        print("\n✅ All tests passed! Modbus communication working.")
        return True

    except PermissionError:
        print("\n❌ PERMISSION ERROR!")
        print("You don't have permission to access the serial port.")
        print("\nFix:")
        print("1. Run: sudo usermod -a -G dialout $USER")
        print("2. Logout and login again")
        print("OR temporarily:")
        print("   sudo chmod 666 /dev/ttyUSB0")
        return False

    except FileNotFoundError:
        print("\n❌ Port /dev/ttyUSB0 not found!")
        print("Check if device is connected.")
        return False

    except Exception as e:
        print(f"\n❌ Communication Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is the relay powered on?")
        print("2. Is baudrate set to 19200 on the relay?")
        print("3. Is slave ID set to 8 on the relay?")
        print("4. Check RS485 wiring (A to A+, B to B-)")
        print("5. Try swapping A and B if not working")
        return False

if __name__ == "__main__":
    test()

