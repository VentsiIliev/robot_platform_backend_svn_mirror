"""
Xinje MA-8X8YR Relay Diagnostic Script

Tests communication with various settings to find the correct configuration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import minimalmodbus
import serial
import time

def test_configuration(port, baudrate, parity, slave_id, timeout=0.5):
    """Test a specific configuration"""
    try:
        instrument = minimalmodbus.Instrument(port, slave_id, debug=False)
        instrument.serial.baudrate = baudrate
        instrument.serial.bytesize = 8
        instrument.serial.stopbits = 1
        instrument.serial.timeout = timeout
        instrument.serial.parity = parity

        # Try to read a coil (relay output) - function code 01
        result = instrument.read_bit(8, functioncode=1)  # Read Y0 (output address 8)
        return True, result
    except Exception as e:
        return False, str(e)
    finally:
        if 'instrument' in locals() and instrument.serial.is_open:
            instrument.serial.close()

def scan_configurations(port='/dev/ttyUSB0'):
    """Scan through common configurations"""
    print(f"=" * 80)
    print(f"Xinje MA-8X8YR Relay Communication Diagnostic")
    print(f"=" * 80)
    print(f"Port: {port}")
    print(f"Testing various configurations...\n")

    # Common configurations for Xinje devices
    baudrates = [19200, 9600, 38400, 115200, 57600, 4800]
    parities = [
        ('NONE', serial.PARITY_NONE),
        ('EVEN', serial.PARITY_EVEN),
        ('ODD', serial.PARITY_ODD)
    ]
    slave_ids = [8, 1, 2, 3, 4, 5, 6, 7, 9, 10]

    success_configs = []
    test_count = 0
    total_tests = len(baudrates) * len(parities) * len(slave_ids)

    for baudrate in baudrates:
        for parity_name, parity in parities:
            for slave_id in slave_ids:
                test_count += 1
                print(f"\r[{test_count}/{total_tests}] Testing: {baudrate} bps, Parity={parity_name}, Slave={slave_id}...", end='', flush=True)

                success, result = test_configuration(port, baudrate, parity, slave_id)

                if success:
                    config = {
                        'baudrate': baudrate,
                        'parity': parity_name,
                        'slave_id': slave_id,
                        'result': result
                    }
                    success_configs.append(config)
                    print(f"\n✓ SUCCESS: baudrate={baudrate}, parity={parity_name}, slave_id={slave_id}, Y0={result}")

                time.sleep(0.05)  # Small delay between tests

    print(f"\n\n" + "=" * 80)
    print(f"Scan Complete")
    print(f"=" * 80)

    if success_configs:
        print(f"\nFound {len(success_configs)} working configuration(s):\n")
        for i, config in enumerate(success_configs, 1):
            print(f"{i}. Baudrate: {config['baudrate']} bps")
            print(f"   Parity: {config['parity']}")
            print(f"   Slave ID: {config['slave_id']}")
            print(f"   Y0 State: {config['result']}")
            print()

        print("\nRecommended settings for robot_config.json:")
        print(f"  'modbus_enabled': True,")
        print(f"  'modbus_port': '{port}',")
        print(f"  'modbus_baudrate': {success_configs[0]['baudrate']},")
        print(f"  'modbus_parity': '{success_configs[0]['parity']}',")
        print(f"  'modbus_slave_id': {success_configs[0]['slave_id']}")
    else:
        print("\n❌ No working configurations found!")
        print("\nTroubleshooting steps:")
        print("1. Check physical wiring:")
        print("   - Verify RS485 A and B connections")
        print("   - Try swapping A and B wires")
        print("   - Ensure device is powered")
        print("2. Check if device is on /dev/ttyUSB0:")
        print("   - Run: ls -la /dev/ttyUSB*")
        print("   - Try other ports if available")
        print("3. Verify device settings:")
        print("   - Check DIP switches on the device")
        print("   - Confirm slave ID is set correctly")
        print("   - Verify baudrate jumper/switch settings")
        print("4. Test with a different tool:")
        print("   - Use ModPoll or similar Modbus testing tool")
        print("   - Confirm device responds to basic commands")

if __name__ == "__main__":
    # Check available ports
    print("\nAvailable serial ports:")
    import glob
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    for p in ports:
        print(f"  - {p}")

    if not ports:
        print("  No serial ports found!")
        sys.exit(1)

    # Use first available port or specified port
    port_to_test = ports[0] if ports else '/dev/ttyUSB0'

    if len(sys.argv) > 1:
        port_to_test = sys.argv[1]

    print(f"\nUsing port: {port_to_test}")
    input("\nPress Enter to start scanning... (This may take a few minutes)")

    scan_configurations(port_to_test)

