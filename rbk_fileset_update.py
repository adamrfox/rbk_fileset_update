#!/usr/bin/python

import sys
import os
import getpass
import getopt
import urllib3
import rubrik_cdm
import platform
urllib3.disable_warnings()

def usage():
    sys.stderr.write("Usage: rbk_fileset_update [-hvD] [-c creds] [-f fileset] share path rubrik\n")
    sys.stderr.write("-h | --help : Prints this message\n")
    sys.stderr.write("-v | --verbose : Verbose mode.  Prints more information\n")
    sys.stderr.write("-D| --debug : Debug mode.  Prints troubleshoting info (+ verbose mode)\n")
    sys.stderr.write("-c | --creds= : Rubrik crednetials.  Either user:password or creds file\n")
    sys.stderr.write("-f | --fileset= : Specify a fileset.  Needed if share has more than one assigned\n")
    sys.stderr.write("share : The share as defined on the rubrk.  Format: host:share/path\n")
    sys.stderr.write("path : The path to the share on the local machine\n")
    sys.stderr.write("rubrik: The name or IP of the Rubrik\n")
    exit(0)


def vprint(message):
    if verbose:
        print message
    return()

def dprint(message):
    if debug:
        print message
    return()


def get_creds_from_file(file, array):
    with open(file) as fp:
        data = fp.read()
    fp.close()
    data = data.decode('uu_codec')
    data = data.decode('rot13')
    lines = data.splitlines()
    for x in lines:
        if x == "":
            continue
        xs = x.split(':')
        if xs[0] == array:
            user = xs[1]
            password = xs[2]
    return (user, password)

def find_latest_dir(path):
    latest_dir = ""
    dprint ("PATH=" + path)
    dirs = os.listdir(path)
    for d_ent in dirs:
        if os.path.isdir(path + d_ent):
            if d_ent > latest_dir:
                latest_dir = d_ent
    return (latest_dir)

if __name__ == "__main__":
    user = ""
    password = ""
    path = ""
    verbose = False
    hs_id = ""
    fileset = ""
    includes = []
    updated_include = []
    debug = False

# Process command line

    optlist, args = getopt.getopt(sys.argv[1:], 'hvc:f:D', ['--help', '--verbose', '--creds=', '--fileset=','--debug'])
    for opt, a in optlist:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-v', '--versbose'):
            verbose = True
        if opt in ('-c', '--creds'):
            if ':' in a:
                (user, password) = a.split(':')
            else:
                (user, password) = get_creds_from_file(a, 'rubrik')
        if opt in ('-f', '--fileset'):
            fileset = a
        if opt in ('-D', '--debug'):
            debug = True
            verbose = True
    if args[0] == "?":
        usage()

# Parse share and deterime type

    (share, path, rubrik_host) = args
    (host, share_name) = share.split(':')
    if share_name.startswith("/"):
        share_type = "NFS"
        share_delim = "/"
    else:
        share_type = "SMB"
        share_delim = "\\"

# Get credentials if not provided

    if not user:
        user = raw_input("User: ")
    if not password:
        password = getpass.getpass("Password: ")

# Get the HostShare ID in order to find the associated fileset(s)

    rubrik_api = rubrik_cdm.Connect(rubrik_host, user, password)
    hs_data = rubrik_api.get('internal', '/host/share')
    for hs in hs_data['data']:
        if hs['hostname'] == host and hs['exportPoint'] == share_name:
            hs_id = hs['id']
            break
    if not hs_id:
        sys.stderr.write("Cannot find share: " + share + "\n ")
        exit (1)
    dprint(hs_id)

# Find the associated filesets.  If multiple, either use the given one or prompt the user for it.

    fs_data = rubrik_api.get('v1', '/fileset?share_id=' + str(hs_id))
    if fs_data['total'] == 0:
        sys.stderr.write("Export has no filesets\n")
        exit (1)
    elif fs_data['total'] > 1:
        if not fileset:
            print "Multiple filsets found for share."
            fileset = raw_input("Which fileset?: ")
            for fs in fs_data['data']:
                if fs['name'] == fileset:
                    fs_id = fs['templateId']
                    includes = fs['includes']
                    break
    else:
        fs_id = fs_data['data'][0]['templateId']
        includes = fs_data['data'][0]['includes']
    if len(includes) != 1:
        sys.stderr.write("Fileset must have only one include.  Has " + str(len(includes)) + "\n")
        exit(1)

# Grab the include path of the fileset.

    inc_path = includes[0]
    inc_path_list = inc_path.split(share_delim)
    inc_path_last =  inc_path_list.pop(-1)
    inc_path_list.pop(-1)
    path += share_delim.join(inc_path_list)
    if not path.endswith(share_delim):
        path += share_delim

# Find the latest directory via the local mount

    dirs = os.listdir(path)
    latest_dir = find_latest_dir(path)
    vprint("Latest Directory: " + latest_dir)
    if not latest_dir:
        sys.stderr.write("Can't find latest directory\n")
        exit(1)

# Form new include path, then update the Rubrik

    inc_path_list.append(latest_dir)
    inc_path_list.append(inc_path_last)
    updated_include.append(share_delim.join(inc_path_list))
    include_patch = {"id": fs_id, "includes": updated_include}
    dprint (include_patch)
    fs_update = rubrik_api.patch('v1', '/fileset_template/' + str(fs_id), include_patch)
    dprint(fs_update)
    if fs_update['includes'] == updated_include:
        vprint("Done")
    else:
        sys.stderr.write("Update Failed.")
        exit (1)




