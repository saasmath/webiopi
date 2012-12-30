#!/usr/bin/python
import sys
file = None

print("WebIOPi passwd file generator")
if len(sys.argv)  == 2:
    file = sys.argv[1]
    if file == "--help" or file == "-h":
        print("Usage: webiopi-passwd [--help|file]")
        print("Compute and display hash used by WebIOPi for Authentication")
        print("Login and Password are prompted")
        print("\t--help\tDisplay this help")
        print("\t-h")
        print("\tfile\tSave hash to file")
        sys.exit()
else:
    file = "/etc/webiopi/passwd"       

f = open(file, "w")
_LOGIN      = "Enter Login: "
_PASSWORD   = "Enter Password: "
_CONFIRM    = "Confirm password: "
_DONTMATCH  = "Passwords don't match !"

import getpass
try:
    login = raw_input(_LOGIN)
except NameError:
    login = input(_LOGIN)
password = getpass.getpass(_PASSWORD)
password2 = getpass.getpass(_CONFIRM)
while password != password2:
    print(_DONTMATCH)
    password = getpass.getpass(_PASSWORD)
    password2 = getpass.getpass(_CONFIRM)

import webiopi
auth = webiopi.encodeAuth(login, password)
print("\nHash: %s" % auth)
if file:
    f.write(auth)
    f.close()
    print("Saved to %s" % file)
