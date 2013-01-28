from webiopi.server import *

def displayHelp():
    print("WebIOPi command-line usage")
    print("python -m webiopi [-d] [-h] [-c config] [-l log] [port]")
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
        error(e)
        exit()
