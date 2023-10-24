import urllib3
import certifi

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
        ca_certs=certifi.where(),  # Path to the Certifi bundle.
        )