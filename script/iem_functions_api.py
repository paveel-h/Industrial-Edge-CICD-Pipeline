import os
import requests
from requests_toolbelt import MultipartEncoder
import json
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RelevantResponse:
    def __init__(self, success, statusCode, contentName, content):
        self.success = success
        self.statusCode = statusCode
        self.contentName = contentName
        self.content = content

    def __str__(self):
        return "The Response was successful: {0} \tStatus Code: {1}\tContent Name: {2} \tContent: {3}".format(self.success, self.statusCode, self.contentName, self.content)


baseUrl = "/portal/api/v1"
devUrl = "/p.service/api/v4"


def loginDirect(iemUrl, username, password):
    """
    Short: Log in with username and password
    Description: This method logs in a user to the edge management with the username, password, and verification code ( if multi-
    factor verification is enabled ).
    : param iemUrl:    (str) the address of iem [required]
    : param username:   (str) the username for login [required]
    : param password:   (str) the the password for login [required]
    """

    url = f"{iemUrl}{baseUrl}/login/direct"

    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "username": username,
        "password": password
    }
    query = {
    }

    try:
        response = requests.post(url, headers=headers,
                                 verify=False, json=payload, params=query)
    except Exception as e:
        print(f'Unexpected error: {e}')
        return RelevantResponse(False, -1, 'error', e)

    if response.status_code == 200:
        return RelevantResponse(True, response.status_code, "bearertoken", response.json()['data']['access_token'])
    else:
        return RelevantResponse(False, response.status_code, "Error Message", response.json()['errors'][0]['message'])


def listApps(iem_url, bearertoken):
    """ Short: List apps.
    Description: This method returns a list of applications in catalog.
    : param iem_url:  (str) address of IEM [required]
    : param bearertoken:  (str) auth token, obtained via login [required]
    """
    url = f"{iem_url}{baseUrl}/applications"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return RelevantResponse(True, str(response.status_code), "Apps list", response.json()['data'])
        else:
            return RelevantResponse(False, str(response.status_code), "Apps list", response.json()['errors'][0]['message'])
    except Exception as e:
        print(f'Unexpected error during list apps: {str(e)}')
        return RelevantResponse(False, -1, 'error', e)


def listAllIEDs(iemUrl, bearertoken):
    return listIEDs(iemUrl, bearertoken, 100, 1)


def listIEDs(iemUrl, bearerToken, size="", page=""):
    """
    Short: List Edge Devices
    Description: This method returns a list of all Edge Devices available for the current user
    : param iemUrl:        (str) the address of iem [required]
    : param bearerToken:    (str) the authorication token [required]
    : param size:           (str) the size of the page. Default value: 10 [optional]
    : param page:           (str) the page number. Default value: 1 [optional]
    """

    url = f"{iemUrl}{baseUrl}/devices"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearerToken
    }
    payload = {
    }
    query = {
    }
    if size:
        query["size"] = size
    if page:
        query["page"] = page

    try:
        response = requests.get(url, headers=headers,
                                verify=False, json=payload, params=query)
    except Exception as e:
        print(f'Unexpected error: {e}')
        return RelevantResponse(False, -1, 'error', e)

    if response.status_code == 200:
        return RelevantResponse(True, response.status_code, "List", response.json()["data"])
    else:
        return RelevantResponse(False, response.status_code, "Error Message", response.json()['errors'][0]['message'])


def installAppWithoutConf(iem_url, bearertoken, deviceid, appid, schedule=""):
    """ Short: Install App without any configuration.
    Description: This method install an application without config and return the batch ID of the operation.
    : param iem_url:  (str) address of IEM [required]
    : param bearertoken:  (str) auth token, obtained via login [required]
    : param deviceid:  (str) unique id of device where the app command is executed [required]
    : param appid:  (str) unique app id [required]
    : param schedule: (str) Time in ticks,Unix Time in Microseconds UTC [optional]
    """
    url = f"{iem_url}{baseUrl}/batches"
    command = "installApplication"
    query = {
        "appid": appid,
        "operation": command
    }
    if schedule:
        query["schedule"] = schedule
    infomap = {"devices": [deviceid]}
    m = MultipartEncoder({"infoMap": str(infomap)})
    headers = {
        'Authorization': bearertoken,
        'Content-Type': m.content_type,
    }
    try:
        response = requests.post(url, headers=headers,
                                 verify=False, params=query, data=m)
        if response.status_code == 200:
            return RelevantResponse(True, str(response.status_code), "Install App without Conf Batch ID", response.json()['data'])
        else:
            return RelevantResponse(False, str(response.status_code), "Install App without Conf Error", response.json()['errors'][0]['message'])
    except Exception as e:
        print(f'Unexpected error during app command: {str(e)}')
        return RelevantResponse(False, -1, 'error', e)


def listIEDApps(iemUrl, bearerToken, deviceID):
    """
    Short: List Edge Device apps
    Description: This method returns a list of all applications installed on a specific Edge Device. If the Edge Device ID is not provided, 
    then it lists all applications installed on all the Edge Devices assigned to the logged-in user.
    : param iemUrl:        (str) the address of iem [required]
    : param bearerToken:    (str) the authorication token [required]
    : param deviceID:       (str) UUID of the device [required]
    """

    url = f"{iemUrl}{baseUrl}/devices/installed-apps"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearerToken
    }
    payload = {
    }
    query = {
        "deviceid": deviceID
    }

    try:
        response = requests.get(url, headers=headers,
                                verify=False, json=payload, params=query)
    except Exception as e:
        print(f'Unexpected error: {e}')
        return RelevantResponse(False, -1, 'error', e)

    if response.status_code == 200:
        return RelevantResponse(True, response.status_code, "Installed Apps", response.json()["data"])
    else:
        return RelevantResponse(False, response.status_code, "Error Message", response.json()['errors'][0]['message'])


def uninstallApp(iem_url, bearertoken, deviceid, appid, schedule=""):
    """ Short: Uninstall app.
    Description: This method uninstalls an application from the specified device,return the batch ID of the operation.
    : param iem_url:  (str) address of IEM [required]
    : param bearertoken:  (str) auth token, obtained via login [required]
    : param deviceid:  (str) unique id of device where the app command is executed [required]
    : param appid:  (str) unique app id [required]
    : param schedule: (str) Time in ticks,Unix Time in Microseconds UTC [optional]
    """
    url = f"{iem_url}{baseUrl}/batches"
    command = "uninstallApplication"
    query = {
        "appid": appid,
        "operation": command
    }
    if schedule:
        query["schedule"] = schedule

    infomap = {"devices": [deviceid],
               }
    m = MultipartEncoder({"infoMap": str(infomap)})
    headers = {
        'Authorization': bearertoken,
        'Content-Type': m.content_type,
    }
    try:
        response = requests.post(url, headers=headers,
                                 verify=False, params=query, data=m)
        if response.status_code == 200:
            return RelevantResponse(True, str(response.status_code), "Uninstall App Batch ID", response.json()['data'])
        else:
            return RelevantResponse(False, str(response.status_code), "Uninstall App Error", response.json()['errors'][0]['message'])
    except Exception as e:
        print(f'Unexpected error during app command: {str(e)}')
        return RelevantResponse(False, -1, 'error', e)


def getAppId(iem_url, bearertoken, appTitle):
    url = f"{iem_url}/p.service/api/v4/applications/names/{appTitle}"
    payload = {}
    headers = {
        'Authorization': bearertoken
    }
    response = requests.request(
        "GET", url, headers=headers, verify=False, data=payload)
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "appId", response.json()['data']['applicationId'])
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def deleteApp(iem_url, bearertoken, app_id):
    """ Short: Delete apps.
    Description: This method Delete the specified app from IEM.
    : param iem_url:  (str) address of IEM [required]
    : param bearertoken:  (str) auth token, obtained via login [required]
    : param appId:  (str) unique identifier of app [required]
    """
    url = f"{iem_url}{devUrl}/dev-apps/{app_id}"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 200:
            return RelevantResponse(True, str(response.status_code), "Deleted App", response.json()['data'])
        else:
            return RelevantResponse(False, str(response.status_code), "Deleted App Error", response.json()['errors'][0]['message'])
    except Exception as e:
        print(f'Unexpected error during app deletion: {str(e)}')
        return RelevantResponse(False, -1, 'error', e)


def addVersionedConfiguration(iem_url, bearertoken, appId, configuration):
    url = f"{iem_url}/p.service/api/v4/applications/{appId}/configs"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }
    payload = {
        "displayName": configuration['displayName'],
        "description": configuration['description'],
        "volPath": configuration['volPath'],
        "relativePath": configuration['relativePath'],
        "secured": "false",
        "versioned": "true"
    }
    response = requests.request(
        "POST", url, headers=headers, verify=False, json=payload)
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "configId", response.json()['data']['appConfigId'])
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def getAllConfigurationsOfApp(iem_url, bearertoken, appId):
    url = f"{iem_url}/p.service/api/v4/applications/{appId}/configs"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "fullConfigDetails", response.json()['data'])
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def getConfigId(iem_url, bearertoken, appId, configDisplayName):
    configurationData = getAllConfigurationsOfApp(
        iem_url, bearertoken, appId).content
    for x in configurationData:
        if x['displayName'] == configDisplayName:
            appConfigId = x['appConfigId']
            return appConfigId


def getConfigVersionId(iem_url, bearertoken, appId, configDisplayName, configVersionName):
    configurationData = getAllConfigurationsOfApp(
        iem_url, bearertoken, appId).content

    for x in configurationData:
        if x['displayName'] == configDisplayName:
            for y in x['appConfigVersionLst']:
                if y['refName'] == configVersionName:
                    appConfigVersionId = y['appConfigVersionId']
                    return appConfigVersionId


def uploadJsonAsConfigurationFile(iem_url, bearertoken, appId, appConfigId, appConfig):
    url = f"{iem_url}/p.service/api/v4/applications/{appId}/configs/{appConfigId}/versions"
    configversion = {
        "refName": appConfig['referenceName'],
        "description": appConfig['description']
    }
    m = MultipartEncoder(fields={'configversion': str(configversion), 'filename': str(
        appConfig['filename']), 'file': (str(appConfig['filename']), str(appConfig['content']), 'application/json')})

    headers = {
        'Authorization': bearertoken,
        'Content-Type': m.content_type
    }

    response = requests.request(
        "POST", url, headers=headers, verify=False, data=m)

    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "Status", "Upload was successful.")
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def createDeviceInMyEdgeCores(iem_url, bearertoken, ied_configuration):
    url = f"{iem_url}/p.service/api/v4/devices/create"

    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }
    response = requests.request(
        "POST", url, headers=headers, verify=False, json=ied_configuration)
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "onboardingFile", response.text)
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def getDeviceIdbyName(iem_url, bearertoken, ied_name):
    url = f"{iem_url}/p.service/api/v4/devices/{ied_name}/discovery"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    print(response)
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "devicebyname", response.json()["discoveryDetails"]["deviceId"])
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def getCategoryId(iem_url, category_name):
    url = f"{iem_url}/p.service/api/v4/categories"
    headers = {}
    response = requests.request("GET", url, headers=headers, verify=False)
    category_id = ""
    for items in response.json()["data"]:
        if category_name == items["name"]:
            category_id = items["categoryId"]
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "categoryid", category_id)
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)

# Not finished yet


def getNewestAppVersionId(iem_url, bearertoken, appId):
    url = f"{iem_url}/p.service/api/v4/dev-apps/{appId}"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify=False)

    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "NewestAppVersionId", response.json()['data']['devappdetail']['versions'][0]['versionId'])
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def deployAppToIED(iem_url, bearertoken, appId, appVersionId, deviceId):
    url = f"{iem_url}/p.service/api/v4/applications/{appId}/versions/{appVersionId}/batch?operation=installApplication&isRetainSecret=false&allow=true"
    file = {"devices": [deviceId]}
    m = MultipartEncoder({"infoMap": str(file)})
    headers = {
        'Authorization': bearertoken,
        'Content-Type': m.content_type
    }
    response = requests.request(
        "POST", url, headers=headers, verify=False, data=m)
    print(response.content)
    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "Status", "Application Download was triggered.")
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def getActivationStatusOfDevice(iem_url, bearertoken, deviceName):
    url = f"{iem_url}:9443/p.service/api/v4/devices"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, verify=False)

    if str(response.status_code) == "200":
        isActivated = False
        for x in response.json()['data']:
            if x['deviceName'] == deviceName:
                isActivated = x['isActivationConfirmed']
            break
        return RelevantResponse(True, str(response.status_code), "isActivated", isActivated)
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)


def logout(iem_url, bearertoken):
    url = f"{iem_url}/p.service/api/v4/logout"
    headers = {
        'Authorization': bearertoken,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, verify=False)

    if str(response.status_code) == "200":
        return RelevantResponse(True, str(response.status_code), "Status", "Logout was successful.")
    else:
        return RelevantResponse(False, str(response.status_code), "UnexpectedBehaviour", response.text)
