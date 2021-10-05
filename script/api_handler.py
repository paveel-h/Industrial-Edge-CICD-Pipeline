import os
import argparse
import sys
import iem_functions_api as api

# Optional args if calling script
parser = argparse.ArgumentParser()
parser.add_argument("type", help="pipeline or standalone")
parser.add_argument(
    "--app_name", help="application name to be created or updated")
parser.add_argument("--ie_url", help="endpoint of IEM")
parser.add_argument("--username", help="username for IEM login")
parser.add_argument("--password", help="password for IEM login")
parser.add_argument("--devices", help="list of IEDs to deploy app")
parser.add_argument("--appVersionID", help="app id")
args = parser.parse_args()


def getAppId(ie_url, token, app_name):
    for app in api.listApps(ie_url, token).content:
        if app["title"] == app_name:
            return app["applicationId"]
    print(f"App {app_name} not found in IEM catalog")
    sys.exit(1)


def getDeviceIdbyName(ie_url, token, ied_name):
    for device in api.listAllIEDs(ie_url, token).content:
        if device["deviceName"] == ied_name:
            return device["deviceId"]
    print(f"Device {ied_name} not found in IEM ")
    sys.exit(1)


def search_app_in_device(ie_url, token, app_name, device):
    for app in api.listIEDApps(ie_url, token, device).content:
        if app["title"] == app_name:
            return app["applicationId"]
    return None


def install_application(app_id, appVersionid, ie_url=None, username=None, password=None, ied_name=None):
    if not ie_url:
        ie_url = os.environ["IE_URL"]
    if not username:
        username = os.environ["IE_USER"]
    if not password:
        password = os.environ["IE_PASSWORD"]
    if not ied_name:
        ied_name = os.environ["IED_NAME"]

    token = api.loginDirect(ie_url, username, password).content
    print(ied_name)
    device = getDeviceIdbyName(ie_url, token, ied_name)
    api.deployAppToIED(ie_url, token, app_id, appVersionid, device)


if __name__ == "__main__":
    if args.type == "pipeline":
        devices = args.devices.replace(" ", "").split(",")
        appVersionid = args.appVersionID
        app_id = os.environ["APP_ID"]
        for d in devices:
            install_application(app_id, appVersionid, ied_name=d)
    elif args.type == "standalone":
        install_application(args.app_name, args.ie_url,
                            args.username, args.password, args.devices)
