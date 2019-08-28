#!/usr/bin/python3

################################################                                             
#      ____    _                   _           #
#     |__  |__| |___ _ __  ___ _ _| |_ ___     #
#       / / -_) / -_) '  \/ -_) ' \  _(_-<     #
#      /_/\___|_\___|_|_|_\___|_||_\__/__/     #
#                                              #
################################################
# John Moss, @x41x41x41

import argparse, os
import urllib.request as urllib2
import xml.etree.ElementTree as ETree
from multiprocessing import Pool
import tldextract

def check(domain):
    # make sure it's a domain we are dealing with
    domain = domain.strip()
    ext = tldextract.extract(domain)
    domain = ext.domain+'.'+ext.suffix

    try:
        #request the XML
        print("[*] Scan: " + domain)
        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36' }
        request = urllib2.Request('https://login.microsoftonline.com/getuserrealm.srf?login=username@' + domain + '&xml=1', None, headers)
        req = urllib2.urlopen(request)
        
        #process the xml
        if req.code == 200:
            xmlroot = ETree.ElementTree(ETree.fromstring(req.read())).getroot()
            if xmlroot.attrib['Success'] == 'true':
                if xmlroot.find('NameSpaceType').text in ['Managed','Federated']:
                    print('[*] USES O365: ' + domain + ' :: ' + xmlroot.find('FederationBrandName').text)
                    result = xmlroot.find('NameSpaceType').text
                    fedname = xmlroot.find('FederationBrandName').text
                elif xmlroot.find('NameSpaceType').text == 'Unknown':
                    print('[*] NO O365: ' + domain)
                    result = 'No'
                    fedname = ''
                else:
                    print('[*] UNKNOWN: ' + domain)
                    result = 'Unhandled Result'
                    fedname = ''
                    
                # Write to RESULTSFILE
                fHandle = open(RESULTSFILE,'a')
                fHandle.write(domain+', '+ result +', '+ fedname +'\n')
                fHandle.close()
            else:
                print('[*] XML not playing ball: ' + domain)
        else:
            print('[*] None 200 response: ' + domain)
        return

    except Exception as e:   
        # :(
        print('[*] ERRORED: ' + domain + ' :: ' + str(e.message))
         
      
if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', default='domains.txt', help='input file')
    parser.add_argument('-t', '--threads', default=200, help='threads')
    args = parser.parse_args()

    DOMAINFILE = args.inputfile
    RESULTSFILE = os.path.splitext(args.inputfile)[0]+"_results.csv"
    MAXPROCESSES=int(args.threads)

    print("Scanning...")
    
    #setup file and prep the things
    fHandle = open(RESULTSFILE,'a')
    fHandle.write("domain, o365, brandname \n")
    fHandle.close()
    pool = Pool(processes=MAXPROCESSES)
    domains = open(DOMAINFILE, "r").readlines()
    
    #run the things
    pool.map(check, domains) 
    print("Finished")
