#imports
import requests
import subprocess
import json
import sys
import multiprocessing
import time
import random
# configuratiom
# channel URL (formatt this way twitch.tv/raffledog )
channel_url = "twitch.tv/raffledog"
# Mul is an integer that shows how many Views you will get from one proxy
# max 10 recommended 5
Mul = 5
# n defines the randomness of the delay  between the Views to avoid Bot detection
n = 8

#############################################################################################
processes = []

def get_proxies():
    # Reading the list of proxies
    try:
        lines = [line.rstrip("\n") for line in open("proxylist.txt")]
        print "Found "+str(len(lines))+" proxies "
    except IOError as e:
        print "An error has occurred while trying to read the list of proxies: %s" % e.strerror
        sys.exit(1)

    return lines


def get_url():
    # Getting the json with all data regarding the stream
    try:
        response = subprocess.Popen(
            ["livestreamer", "--http-header", "Client-ID=ewvlchtxgqq88ru9gmfp1gmyt6h2b93",
            channel_url, "-j"], stdout=subprocess.PIPE).communicate()[0]
    except subprocess.CalledProcessError:
        print "An error has occurred while trying to get the stream data. Is the channel online? Is the channel name correct?"
        sys.exit(1)
    except OSError:
        print "An error has occurred while trying to use livestreamer package. Is it installed? Do you have Python in your PATH variable?"

    # Decoding the url to the worst quality of the stream
    try:
        url = json.loads(response)['streams']['audio']['url']
    except (ValueError, KeyError):
        print "An error has occurred while trying to get the stream data. Is the channel online? Is the channel name correct?"
        sys.exit(1)

    return url


def open_url(url, proxy):
    # Sending HEAD requests
    print "proc started "
    while True:
        try:
            with requests.Session() as s:
                response = s.head(url, proxies=proxy)
            print "Sent HEAD request with %s" % proxy["http"]
            time.sleep(20)
        except requests.exceptions.Timeout:
            print "  Timeout error for %s" % proxy["http"]
        except requests.exceptions.ConnectionError:
            print "  Connection error for %s" % proxy["http"]


def prepare_processes():
    global processes
    proxies = get_proxies()
    proxies = proxies * Mul
    n = 0

    if len(proxies) < 1:
        print "An error has occurred while preparing the process: Not enough proxy servers. Need at least 1 to function."
        sys.exit(1)

    for proxy in proxies:
        # Preparing the process and giving it its own proxy
        processes.append(multiprocessing.Process(target=open_url, kwargs={"url": get_url(), "proxy": {"http": proxy}}))
        print '.',
    print ''

if __name__ == "__main__":
    print "Obtaining the channel..."
    print "Channel url : " + channel_url
    print "Obtained the channel"
    print "Preparing the processes..."
    prepare_processes()
    print "Prepared the processes ( "+str(len(processes))+" processes prepared ) "
    print "Booting up the processes..."
    # Starting up the processes
    for process in processes:
        time.sleep(random.randint(1, 5) * n)
        process.daemon = True
        process.start()
        if n > 1:
            n -= 1

    # Running infinitely
    while True:
        time.sleep(1)
