#!/usr/bin/env python3
"""
FOR https://geonode.com/free-proxy-list 
"""
import requests
import json
import os
from connection import check_connection

# Some constants
RESULTS = []
PROTOCOLS = ["https", "http", "socks4", "socks5"]


def get_results(log_file: str, page: int = 1, protocols: list[str] = []) -> None:
    """Fetching results from https://geonode.com/free-proxy-list

    Args:
        log_file (str): file which will store the output
        page (int, optional): starting page number. Defaults to 1.
        protocols (list[str], optional): list of valid protocols that you want to fetch. Defaults to [].
    """
    url = "https://proxylist.geonode.com/api/proxy-list?limit=200&sort_by=lastChecked&sort_type=desc"

    protocol_param = ""
    # Checking if protocols are valid
    if protocols:
        for protocol in protocols:
            assert protocol.lower() in PROTOCOLS, \
                f"Invalid Protocol: {protocol}\n Valid protocols are: {PROTOCOLS}"
        protocol_param += "&protocols=" + '%2c'.join(protocols)  # Param string

    request_url = f"{url}&page={page}{protocol_param}"

    r = requests.get(url=request_url)

    if r.status_code != 200:
        print(f"Request failed with status code {r.status_code}")
        r.close()
        return

    data = r.json()

    # Using get to avoid key error
    ips = data.get("data")

    # Nothing left lmao
    if not len(ips):
        r.close()
        return

    result = []

    for ip in ips:
        ip_collection = {}
        ip_collection["ip"] = ip["ip"]
        ip_collection["port"] = int(ip["port"])
        ip_collection["protocols"] = ip["protocols"]
        ip_collection["country"] = ip["country"]
        ip_collection["anonymityLevel"] = ip["anonymityLevel"]
        result.append(ip_collection)

    RESULTS.extend(result)

    with open(log_file, 'w') as f:
        json.dump(RESULTS, f, indent=2)

    print(f"Fetched {len(RESULTS)} IPS")
    r.close()
    get_results(log_file=log_file, page=page+1, protocols=protocols)


def filter_ips(log_file: str, result_file: str, protocols: list[str], timeout: int = 10) -> None:
    """Filtering proxies by connecting to it within a given time

    Args:
        log_file (str): File from where to read the proxies to check
        result_file (str): To store the checked proxies
        protocols (list[str]): list of protocols that should only be checked
        timeout (int, optional): Timeout for connection. Defaults to 10.

    Raises:
        IOError: Log file not found
    """

    if not os.path.exists(log_file):
        raise IOError(f"{log_file} doesn't exits")

    if os.path.exists(result_file):
        n = input(
            f"{result_file} already exists, do you want to ovewrite ? [y/N]: "
        )
        if n.lower() != 'y':
            return

        with open(result_file, 'w') as f:
            f.write('')
    
    if protocols:
        for protocol in protocols:
            assert protocol.lower() in PROTOCOLS, \
                f"Invalid Protocol: {protocol}"

    results = []
    with open(log_file) as f:
        if protocols:
            for ip in json.load(f):
                for protocol in protocols:
                    if protocol in ip["protocols"]:
                        results.append(ip)
                        break
        else:
            results = json.load(f)

    try:
        os.remove(result_file)
    except:
        pass

    for result in results:
        ip = result["ip"]
        port = result["port"]
        protocol = result["protocols"]
        country = result["country"]
        anonymity_level = result["anonymityLevel"]

        if check_connection(host=result["ip"], port=result["port"], timeout=timeout):
            result_string = f"{ip}:{port}\t{', '.join(protocol)} {country} {anonymity_level}"
            with open(result_file, 'a') as f:
                f.write(f"{result_string}\n")



log_file = "log/geonode-iplist-socks5.json"
result_file = "log/geonode-workinglist-socks5.txt"

get_results(log_file, protocols=["socks5"])
filter_ips(log_file, result_file, protocols=["socks5"])
