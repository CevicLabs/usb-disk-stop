# usb-disk-stop

Spin down (or up) a USB disk whose enclosure ignores ATA standby.

Many USB-SATA bridges silently drop `hdparm -y` and `hdparm -S`, so the disk never sleeps. Most of them do pass the SCSI **START STOP UNIT** command. `disk-stop.py` sends it directly through Linux SG_IO.

Tested with an Innostor IS621 bridge (USB ID `1f75:0621`) and a 3 TB Hitachi disk: `hdparm -y` did nothing. `disk-stop.py` put the disk into real standby (enclosure LED off).

## Usage

```sh
sudo ./disk-stop.py /dev/sdX           # stop: spin down
sudo ./disk-stop.py --start /dev/sdX   # start: spin up, returns once the disk is ready
```

It prints `stop /dev/sdX: ok` and exits 0 on success, or `failed` with the SCSI status and exits 1.

- Python 3, standard library only. Linux only (SG_IO).
- Unmount the disk, or export its pool, before stopping it. A stopped disk spins up again on the next access, but some bridges need a few seconds before the disk answers, so check before mounting.
- `--start` waits for the spin-up to finish (IMMED=0), up to a 120-second timeout.

## Example: nightly job on a sleeping disk

```sh
disk-stop.py --start /dev/sdb           # wake it
# wait until a read succeeds, then mount, back up, unmount
disk-stop.py /dev/sdb                   # back to sleep
```

## Licence

MIT. See [LICENSE](LICENSE).
