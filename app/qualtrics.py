# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:23:38 2020

@author: Hugo
"""

# Code from the Qualtrics API documentation:
# https://api.qualtrics.com/docs/getting-survey-responses-via-the-new-export-apis

import requests
import zipfile
import json
import io, os
import sys
import re

def exportSurvey(apiToken,surveyId, dataCenter, fileFormat):

    surveyId = surveyId
    fileFormat = fileFormat
    dataCenter = dataCenter 

    # Setting static parameters
    requestCheckProgress = 0.0
    progressStatus = "inProgress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
    headers = {
    "content-type": "application/json",
    "x-api-token": apiToken,
    }

    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '"}'
    downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
    progressId = downloadRequestResponse.json()["result"]["progressId"]
    print(downloadRequestResponse.text)

    # Step 2: Checking on Data Export Progress and waiting until export is ready
    while progressStatus != "complete" and progressStatus != "failed":
        print ("progressStatus=", progressStatus)
        requestCheckUrl = baseUrl + progressId
        requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
        requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
        print("Download is " + str(requestCheckProgress) + " complete")
        progressStatus = requestCheckResponse.json()["result"]["status"]

    #step 2.1: Check for error
    if progressStatus is "failed":
        raise Exception("export failed")

    fileId = requestCheckResponse.json()["result"]["fileId"]

    # Step 3: Downloading file
    requestDownloadUrl = baseUrl + fileId + '/file'
    requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)

    # Step 4: Unzipping the file
    zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("qualtrics_survey")
    print('Complete')


def main():
    
    try:
      apiToken = "KJxEdAFzoTLWpdLdBzy0hnmD6jeYiFw1Xrph3RhK"  # Temporary
      dataCenter = "stanforduniversity.ca1"
    except KeyError:
      print("[ERROR] Set environment variables APIKEY and DATACENTER")
      sys.exit(2)

    try:
        surveyId = "SV_23QKD9ueJfXlQrz"
        fileFormat = "csv"
    except IndexError:
        print ("[ERROR] Usage: surveyId fileFormat")
        sys.exit(2)

    if fileFormat not in ["csv", "tsv", "spss"]:
        print ("[ERROR] fileFormat must be either csv, tsv, or spss")
        sys.exit(2)
 
    r = re.compile('^SV_.*')
    m = r.match(surveyId)
    if not m:
       print ("[ERROR] surveyId must match ^SV_.*")
       sys.exit(2)

    exportSurvey(apiToken, surveyId,dataCenter, fileFormat)
 
if __name__== "__main__":
    main()
