import subprocess

def write_target_position(slave_id, position):
    cmd = [
        "ethercat", "download",
        f"-p{slave_id}",
        "--type", "int32",
        "0x607A", "0",
        str(position)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr

def read_actual_position(slave_id):
    cmd = [
        "ethercat", "upload",
        f"-p{slave_id}",
        "--type", "int32",
        "0x6064", "0"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()
    print(f"Raw result for slave {slave_id}: {output}")
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    try:
        # Try to extract the decimal part (after space)
        parts = output.split()
        if len(parts) == 2:
            return int(parts[1])  # use the decimal part
        elif len(parts) == 1:
            return int(parts[0], 0)  # fallback: parse hex
        else:
            print("Unexpected output format")
            return None
    except Exception as e:
        print(f"Could not parse result: {output} ({e})")
        return None

# Test loop
for i in range(6):
    write_target_position(i, 10000 * (i + 1))

for i in range(6):
    actual = read_actual_position(i)
    print(f"Slave {i} actual position: {actual}")

