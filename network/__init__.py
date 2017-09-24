import logging
import sys


network_logger = logging.getLogger("network_logger")
network_logger.setLevel(logging.DEBUG)

f_handler = logging.FileHandler("logs/network.log", "w")
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(logging.Formatter("%(asctime)s "
                                         "%(levelname)s "
                                         "%(message)s"))

s_handler = logging.StreamHandler(sys.stdout)
s_handler.setLevel(logging.CRITICAL)

network_logger.addHandler(f_handler)
network_logger.addHandler(s_handler)
# network_logger.addHandler(logging.StreamHandler(sys.stdout))
