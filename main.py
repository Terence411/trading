from connection import IBConnection


def main():
    conn = IBConnection()

    connected = conn.connect()
    if not connected:
        return

    conn.get_account_summary()
    conn.disconnect()


if __name__ == "__main__":
    main()
