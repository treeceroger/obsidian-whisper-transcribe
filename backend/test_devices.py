"""
Quick test script to check audio device enumeration
"""
import sounddevice as sd

try:
    print("Querying audio devices...")
    devices = sd.query_devices()

    print(f"\nFound {len(devices)} total devices")
    print(f"Default device: {sd.default.device}")

    print("\n=== Input Devices ===")
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            default_marker = " [DEFAULT]" if idx == sd.default.device[0] else ""
            print(f"  {idx}: {device['name']}{default_marker}")
            print(f"      Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']}")

    print("\nTest completed successfully!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
