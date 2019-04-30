"""
ADK transport layer (HYT)
"""

import struct
#from . import types, exceptions
from . import exceptions

class HYTPacket(object):

    """ Root Hytera HYT packet """

    # HYT signature prefix
    __HYTSIG = b'\x32\x42\x00'

    def __init__(self, data = None):
        """
        Convert a block of bytes into a new HYTPacket.

        If data == None or not provided, an empty packet will be created
        """
        if data is None:
            self.hytPktType = 0xFF
            self.hytSeqID   = 1
            self.hytPayload = b''
            return

        # Unpack the packet data
        signature = data[0:3]
        pktType, seqid = struct.unpack_from('<BH', data, 3)

        # Check the initial signature is correct
        if signature != self.__HYTSIG:
            raise exceptions.HYTBadSignature()

        # De-encapsulate the fields -- TODO refactor and do this with struct.decode
        self.hytPktType = pktType
        self.hytSeqID   = seqid
        self.hytPayload = data[6:]


    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        return self.__HYTSIG + struct.pack('<BH', self.hytPktType, self.hytSeqID) + self.hytPayload


    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<HYTPacket: type 0x%02X, seqid %d, %d payload bytes>" % (self.hytPktType, self.hytSeqID, len(self.hytPayload))


    @staticmethod
    def decode(data):
        """ Decode an arbitrary HYTPacket into its lowest-level subclass """

        # First decode as a raw ADK packet to get the packet type
        p = HYTPacket(data)

        # Scan subclasses to find one which handles this packet type
        for sc in HYTPacket.__subclasses__():
            if sc.TYPE == p.hytPktType:
                return sc(data)

        # Couldn't find an ADK packet handler which handles this type of packet
        raise exceptions.HYTUnhandledType()



class HSTRPSyn(HYTPacket):
    """ HYT Repeater Announcement (SYN) packet """
    TYPE = 0x24

    def __init__(self, data = None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # Handle no-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            # Cannot create no-args SYN packets, they're only supposed to be
            # sent by the repeater
            raise HRNPCannotCreate()

        # Payload:
        #   83          unknown1
        #   04          unknown2
        #   00 01 86 9F     Repeater ID (99999)
        #   04          unknown3
        #   01          unknown4
        #   02              Timeslot, 01 or 02
        #
        # The ADK log calls this NetworkDescriptor / "syn packet"

        # Decode the payload
        self.unknown1, self.unknown2, self.synRepeaterRadioID, self.unknown3, self.unknown4, self.synTimeslot = \
                struct.unpack_from('>BBLBBB', self.hytPayload)


    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # Throw an exception because user code shouldn't be trying to send SYN packets?
        raise HRNPCannotCreate()
        #return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<HSTRPSyn: type 0x%02X, seqid %d, unknowns(hex %02X %02X %02X %02X), repeater ID %d, timeslot %d>" % \
                (self.hytPktType, self.hytSeqID, \
                self.unknown1, self.unknown2, self.unknown3, self.unknown4, \
                self.synRepeaterRadioID, self.synTimeslot)


class HSTRPSynAck(HYTPacket):
    """ HYT SYN-ACK packet, sent by IPDIS to repeater when a HSTRPSyn packet is received """
    TYPE = 0x05

    def __init__(self, data = None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # No-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            return

        # A SYN-ACK has no payload.


    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # A SYN-ACK has no payload.
        self.hytPayload = b''
        return super().__bytes__()


    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<HSTRPSynAck: type 0x%02X, seqid %d, %d payload bytes>" % (self.hytPktType, self.hytSeqID, len(self.hytPayload))


class HSTRPAck(HYTPacket):
    """ HYT ACK packet, sent by IPDIS or the repeater to acknowledge receipt of a packet """
    TYPE = 0x01

    def __init__(self, data = None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # No-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            return

        # An ACK has no payload.


    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # An ACK has no payload.
        self.hytPayload = b''
        return super().__bytes__()


    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<HSTRPAck: type 0x%02X, seqid %d, %d payload bytes>" % (self.hytPktType, self.hytSeqID, len(self.hytPayload))


class HSTRPHeartbeat(HYTPacket):
    """ HYT Heartbeat / Keepalive packet, sent by IPDIS or the repeater to keep the connection alive. Needs to be acked. """
    TYPE = 0x02

    def __init__(self, data = None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # No-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            return

        # A heartbeat has no payload.


    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # A heartbeat has no payload.
        self.hytPayload = b''
        return super().__bytes__()


    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<HSTRPHeartbeat: type 0x%02X, seqid %d, %d payload bytes>" % (self.hytPktType, self.hytSeqID, len(self.hytPayload))


