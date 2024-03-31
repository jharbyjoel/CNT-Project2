from .common import *

class CwndControl:
    '''Interface for the congestion control actions'''

    def __init__(self):
        self.cwnd = 1.0 * MTU
        self.ssthresh = INIT_SSTHRESH

    def on_ack(self, ackedDataLen):
        # Congestion control logic for handling acknowledgments
        if self.cwnd < self.ssthresh:
            self.cwnd += ackedDataLen
        else:
            self.cwnd += (MTU * MTU) / self.cwnd

    def on_timeout(self):
        # Congestion control logic for handling timeouts
        self.ssthresh = self.cwnd / 2
        self.cwnd = MTU

    def __str__(self):
        return f"cwnd:{self.cwnd} ssthresh:{self.ssthresh}"

