#   Copyright 2012-2013 Eric Ptak - trouch.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
from webiopi.utils import *
from webiopi.server import Server

def displayHelp():
    print("WebIOPi command-line usage")
    print("webiopi [-d] [-h] [-c config] [-l log] [-s script] [port]")
    exit()

def main(argv):
    port = 8000
    configfile = None
    logfile = None
    setInfo()
    
    i = 1
    while i < len(argv):
        if argv[i] in ["-c", "-C", "--config-file"]:
            configfile = argv[i+1]
            i+=1
        elif argv[i] in ["-l", "-L", "--log-file"]:
            logfile = argv[i+1]
            i+=1
        elif argv[i] in ["-s", "-S", "--script-file"]:
            scriptfile = argv[i+1]
            scriptname = scriptfile.split("/")[-1].split(".")[0]
            loadScript(scriptname, scriptfile)
            i+=1
        elif argv[i] in ["-h", "-H", "--help"]:
            displayHelp()
        elif argv[i] in ["-d", "--debug"]:
            setDebug()
        else:
            try:
                port = int(argv[i])
            except ValueError:
                displayHelp()
        i+=1
    
    if logfile:
        logToFile(logfile)

    info("Starting %s" % VERSION_STRING)
    server = Server(port=port, configfile=configfile)
    runLoop()
    server.stop()

if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception as e:
        exception(e)
        stop()
