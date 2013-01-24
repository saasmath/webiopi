from webiopi.server import *

def main(argv):
    port = 8000
    configfile = "/etc/webiopi/config"

    if len(argv)  == 2:
        port = int(argv[1])
    
    server = Server(port=port, configfile=configfile)
    runLoop()
    server.stop()

if __name__ == "__main__":
    main(sys.argv)
