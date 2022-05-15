import sys
import glob
import serial

COMMAND_START = 0x3C
COMMAND_END = 0x3E


def get_available_serial_ports():
    available = []

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        ports = []

    for port in ports:
        try:
            connection = serial.Serial(port)
            connection.close()
            available.append(port)
        except (OSError, serial.SerialException):
            pass

    return available
