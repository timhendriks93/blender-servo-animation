import re

IP_ADDRESS_REGEX = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"


def is_ip(value):
    return re.match(IP_ADDRESS_REGEX, value)
