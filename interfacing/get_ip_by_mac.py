import argparse
import subprocess
import re
import json
import getpass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mac_list', help='Path to JSON file containing MAC to ID mapping')
    parser.add_argument('interface', help='Network interface on which to make query')
    parser.add_argument('-c', help='Optional command for address', default=None)

    args = parser.parse_args()
    interface = args.interface

    try:
        f = open(args.mac_list, 'r')
        mac_to_id = json.load(f)
    except Exception as e:
        print(repr(e))
        print('Could not open file ({})'.format(args.mac_list))

    pid = subprocess.Popen(['arp-scan', '-I', interface, '-l'], stdout=subprocess.PIPE)
    out = pid.communicate()[0].decode()
    lines = out.split('\n')

    mac_to_ip = {}

    for line in lines:

        # Look for MAC address in the line
        mac = re.search(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', line, re.I)
        if(mac is None):
            continue
        # Else
        mac = mac.group()

        ip = re.search(r'((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])', line, re.I)
        if(ip is None):
            continue
        # Else
        ip = ip.group()

        mac_to_ip[mac] = ip

    # Make ID to IP mapping
    id_to_ip = dict({mac_to_id[x]: y for x, y in mac_to_ip.items() if x in mac_to_id})

    print(id_to_ip)

    if(args.c is None):
        return

    print('Enter secrets for robots')
    password = getpass.getpass()
    # -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no
    # Else, send command to robots
    cmds = [['sshpass', '-p', password, 'ssh', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no', 'pi@'+x, args.c] for x in id_to_ip.values()]
    pids = []
    for cmd in cmds:
        pids.append(subprocess.Popen(cmd))

    for pid in pids:
        pid.communicate()


if __name__ == '__main__':
    main()
