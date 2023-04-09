import serial.tools.list_ports


def get_serial_ports():
    ports = []

    for port in serial.tools.list_ports.comports():
        ports.append(port.device)

    return ports
