#!/usr/bin/env python3
"""Temporary test script for py-mercury-switch-api."""

import sys

from py_mercury_switch_api import MercurySwitchConnector
from py_mercury_switch_api.exceptions import (
    LoginFailedError,
    MercurySwitchConnectionError,
    MercurySwitchModelNotDetectedError,
)


def main() -> None:
    """Test the Mercury Switch API with user-provided credentials."""
    print("=" * 60)
    print("Mercury Switch API Test Script")
    print("=" * 60)
    print()

    # Get credentials from user
    host = input("Enter switch host (IP address): ").strip()
    if not host:
        print("Error: Host is required")
        sys.exit(1)

    username = input("Enter username (default: admin): ").strip() or "admin"
    password = input("Enter password: ").strip()
    if not password:
        print("Error: Password is required")
        sys.exit(1)

    print()
    print(f"Connecting to {host} as {username}...")
    print()

    # Create connector
    try:
        connector = MercurySwitchConnector(
            host=host, username=username, password=password
        )
    except Exception as e:
        print(f"Error creating connector: {e}")
        sys.exit(1)

    # Test auto-detection
    print("Step 1: Auto-detecting switch model...")
    try:
        model = connector.autodetect_model()
        print(f"✓ Detected model: {model.MODEL_NAME}")
        print(f"✓ Number of ports: {connector.ports}")
    except MercurySwitchModelNotDetectedError as e:
        print(f"✗ Model detection failed: {e}")
        print("  Continuing anyway...")
    except Exception as e:
        print(f"✗ Error during model detection: {e}")
        print("  Continuing anyway...")
    print()

    # Test login
    print("Step 2: Testing login...")
    try:
        if connector.get_login_cookie():
            print("✓ Login successful")
        else:
            print("✗ Login failed - no cookie received")
            sys.exit(1)
    except LoginFailedError as e:
        print(f"✗ Login failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error during login: {e}")
        sys.exit(1)
    print()

    # Get switch information
    print("Step 3: Fetching switch information...")
    try:
        switch_info = connector.get_switch_infos()
        print("✓ Successfully retrieved switch information")
        print()
        print("=" * 60)
        print("Switch Information:")
        print("=" * 60)

        # Display basic info
        if "switch_model" in switch_info:
            print(f"Model: {switch_info['switch_model']}")
        if "switch_mac" in switch_info:
            print(f"MAC Address: {switch_info['switch_mac']}")
        if "switch_ip" in switch_info:
            print(f"IP Address: {switch_info['switch_ip']}")
        if "switch_firmware" in switch_info:
            print(f"Firmware: {switch_info['switch_firmware']}")
        if "switch_hardware" in switch_info:
            print(f"Hardware: {switch_info['switch_hardware']}")

        print()

        # Display port information
        print("Port Status:")
        print("-" * 60)
        ports = connector.ports
        for port_num in range(1, ports + 1):
            status_key = f"port_{port_num}_status"
            speed_key = f"port_{port_num}_connection_speed"
            tx_key = f"port_{port_num}_tx_good"
            rx_key = f"port_{port_num}_rx_good"

            status = switch_info.get(status_key, "unknown")
            speed = switch_info.get(speed_key, "unknown")
            tx = switch_info.get(tx_key, 0)
            rx = switch_info.get(rx_key, 0)

            print(
                f"Port {port_num}: {status:4s} | Speed: {speed:15s} | TX: {tx:>12,} | RX: {rx:>12,}"
            )

        print()

        # Display VLAN information
        if "vlan_enabled" in switch_info:
            print("VLAN Information:")
            print("-" * 60)
            print(f"802.1Q VLAN Enabled: {switch_info.get('vlan_enabled', False)}")
            print(f"VLAN Type: {switch_info.get('vlan_type', 'Unknown')}")
            print(f"VLAN Count: {switch_info.get('vlan_count', 0)}")
            print()

            # Display per-VLAN info
            vlan_count = switch_info.get("vlan_count", 0)
            if vlan_count > 0:
                print("VLAN Details:")
                for key, value in sorted(switch_info.items()):
                    if key.startswith("vlan_") and (
                        "_name" in key
                        or "_tagged_ports" in key
                        or "_untagged_ports" in key
                    ):
                        print(f"  {key}: {value}")

        print()
        print("=" * 60)
        print("All available keys in switch_info:")
        print("=" * 60)
        for key in sorted(switch_info.keys()):
            print(f"  - {key}")

    except MercurySwitchConnectionError as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error fetching switch information: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
