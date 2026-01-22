#!/usr/bin/env python3
"""
Modbus Connection Diagnostic Tool

This script helps diagnose connection issues with the Xinje MA-8X8YR relay
via USB-to-RS485 converter (YYH-256 with CH340 chip).

Common Issues:
1. User not in 'dialout' group - Run: sudo usermod -a -G dialout $USER (then logout/login)
2. Port already in use by another application
3. Incorrect baudrate or slave ID
4. Bad cable or converter
"""

import sys
import os

def check_permissions():
    """Check if user has permission to access serial port"""
    import grp
    import pwd

    username = pwd.getpwuid(os.getuid()).pw_name
    groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
    primary_group = grp.getgrgid(pwd.getpwuid(os.getuid()).pw_gid).gr_name
    groups.append(primary_group)

    print(f"Current user: {username}")
    print(f"Groups: {', '.join(groups)}")

    if 'dialout' not in groups:
        print("\n❌ ERROR: User is not in 'dialout' group!")
        print("   Run: sudo usermod -a -G dialout $USER")
        print("   Then logout and login again")
        return False
    else:
        print("✅ User is in 'dialout' group")
        return True

def check_port_exists(port):
    """Check if serial port exists"""
    if os.path.exists(port):
        print(f"✅ Port {port} exists")
        # Check permissions
        import stat
        st = os.stat(port)
        mode = stat.filemode(st.st_mode)
        print(f"   Permissions: {mode}")
        return True
    else:
        print(f"❌ ERROR: Port {port} does not exist!")
        print("   Available ports:")
        import glob
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        if ports:
            for p in ports:
                print(f"   - {p}")
        else:
            print("   No USB serial ports found!")
        return False

def check_driver():
    """Check if CH340/CH341 driver is loaded"""
    import subprocess
    try:
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        if 'ch341' in result.stdout or 'ch340' in result.stdout:
            print("✅ CH340/CH341 driver is loaded")
            return True
        else:
            print("❌ WARNING: CH340/CH341 driver not found")
            print("   The driver should load automatically for CH340 chip")
            return False
    except Exception as e:
        print(f"⚠️  Could not check driver: {e}")
        return True  # Don't fail, just warn

def test_serial_open(port, baudrate=19200):
    """Test opening the serial port"""
    try:
        import serial
        print(f"\nTesting serial port: {port} at {baudrate} baud...")

        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=1
        )
        print(f"✅ Successfully opened {port}")
        print(f"   Port info: {ser}")
        ser.close()
        return True
    except PermissionError as e:
        print(f"❌ PERMISSION ERROR: {e}")
        print("   You don't have permission to access this port")
        print("   Make sure you're in the 'dialout' group and logged out/in")
        return False
    except Exception as e:
        print(f"❌ ERROR opening port: {e}")
        return False

def test_modbus_connection(port='/dev/ttyUSB0', baudrate=19200, slave_id=8):
    """Test Modbus connection to Xinje relay"""
    try:
        import minimalmodbus

        print(f"\nTesting Modbus connection...")
        print(f"Port: {port}, Baudrate: {baudrate}, Slave ID: {slave_id}")

        instrument = minimalmodbus.Instrument(port, slave_id)
        instrument.serial.baudrate = baudrate
        instrument.serial.bytesize = 8
        instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1
        instrument.mode = minimalmodbus.MODE_RTU

        # Try to read a coil (output status)
        print("Reading output coil 0x0008...")
        value = instrument.read_bit(0x0008, functioncode=1)
        print(f"✅ Modbus communication successful!")
        print(f"   Output 0 (Y0) state: {'ON' if value else 'OFF'}")

        # Try to read all outputs
        print("\nReading all outputs...")
        for i in range(8):
            try:
                value = instrument.read_bit(0x0008 + i, functioncode=1)
                print(f"   Y{i}: {'ON' if value else 'OFF'}")
            except Exception as e:
                print(f"   Y{i}: Error - {e}")

        return True

    except Exception as e:
        print(f"❌ Modbus communication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that the Xinje relay is powered on")
        print("2. Verify baudrate is set to 19200 on the relay")
        print("3. Verify slave ID is set to 8 on the relay")
        print("4. Check RS485 wiring: A to A+, B to B-")
        print("5. Try swapping A and B wires if not working")
        return False

def main():
    print("=" * 60)
    print("Modbus Connection Diagnostic Tool")
    print("For Xinje MA-8X8YR with USB-RS485 (YYH-256/CH340)")
    print("=" * 60)

    # Check permissions first
    if not check_permissions():
        print("\n❌ Fix permission issue first!")
        sys.exit(1)

    # Check driver
    check_driver()

    # Get port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'

    # Check port exists
    if not check_port_exists(port):
        sys.exit(1)

    # Test serial open
    if not test_serial_open(port):
        sys.exit(1)

    # Test Modbus
    test_modbus_connection(port)

    print("\n" + "=" * 60)
    print("Diagnostic complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

