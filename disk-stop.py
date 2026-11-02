#!/usr/bin/env python3
"""Send SCSI START STOP UNIT to a disk, e.g. a USB disk whose bridge ignores ATA standby.

Usage: sudo disk-stop.py /dev/sdX          (stop: spin down)
       sudo disk-stop.py --start /dev/sdX  (start: spin up; returns once the disk is up)
"""
import ctypes
import fcntl
import os
import sys

SG_IO = 0x2285


class SgIoHdr(ctypes.Structure):
    _fields_ = [("interface_id", ctypes.c_int), ("dxfer_direction", ctypes.c_int),
                ("cmd_len", ctypes.c_ubyte), ("mx_sb_len", ctypes.c_ubyte), ("iovec_count", ctypes.c_ushort),
                ("dxfer_len", ctypes.c_uint), ("dxferp", ctypes.c_void_p), ("cmdp", ctypes.c_void_p),
                ("sbp", ctypes.c_void_p), ("timeout", ctypes.c_uint), ("flags", ctypes.c_uint),
                ("pack_id", ctypes.c_int), ("usr_ptr", ctypes.c_void_p), ("status", ctypes.c_ubyte),
                ("masked_status", ctypes.c_ubyte), ("msg_status", ctypes.c_ubyte), ("sb_len_wr", ctypes.c_ubyte),
                ("host_status", ctypes.c_ushort), ("driver_status", ctypes.c_ushort), ("resid", ctypes.c_int),
                ("duration", ctypes.c_uint), ("info", ctypes.c_uint)]


def main() -> int:
    args = sys.argv[1:]
    start = "--start" in args
    devs = [a for a in args if a != "--start"]
    if len(devs) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    dev = devs[0]
    # START STOP UNIT; IMMED=0 so a start returns only once the disk has spun up.
    cdb = (ctypes.c_ubyte * 6)(0x1B, 0, 0, 0, 0x01 if start else 0x00, 0)
    sense = (ctypes.c_ubyte * 32)()
    hdr = SgIoHdr(interface_id=ord("S"), dxfer_direction=-1, cmd_len=6, mx_sb_len=32,
                  cmdp=ctypes.addressof(cdb), sbp=ctypes.addressof(sense), timeout=120000)
    fd = os.open(dev, os.O_RDONLY | os.O_NONBLOCK)
    try:
        fcntl.ioctl(fd, SG_IO, hdr)
    finally:
        os.close(fd)
    ok = hdr.status == 0 and hdr.host_status == 0 and hdr.driver_status == 0
    word = "start" if start else "stop"
    print(f"{word} {dev}: {'ok' if ok else 'failed'} "
          f"(status={hdr.status} host={hdr.host_status} driver={hdr.driver_status})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
