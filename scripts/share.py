#!/usr/bin/env python

import json
import requests
import sys
import mimetypes
import math
import os
from sharelib import auth
from datetime import datetime, timedelta

def callApiWithKey(url, data):
    return requests.put(url, data=data).headers["Etag"]

def splitFileForUpload(filePath, response):
    totalSize = os.stat(filePath).st_size

    file = open(filePath, "rb")
    filesize = int(math.ceil(totalSize/len(response.uploadUrls)))
    parts = []
    currentByte = 0

    for x in range(0,len(response.uploadUrls)):
        file.seek(currentByte)
        data = file.read(filesize)
        currentByte += filesize
        print("Uploading Package " + str(x+1) + " out of " + str(len(response.uploadUrls)) + "...")
        etag = callApiWithKey(response.uploadUrls[x], data)
        parts.append({"ETag": etag, "PartNumber": x+1})

    file.close()
    return parts

class RequestTypes:
    file = "FILE"
    link = "LINK"
    file_request = "FILE_REQUEST"

class File:

    def __init__(self, name, size, type):
        self.fileName = name
        self.fileSize = size
        self.fileType = type


class AddShareRequestDTO():

    def __init__(self, title, type, file, forceDownload):
        self.title = title
        self.type = type
        self.file = file
        self.forceDownload = forceDownload
        self.expires = (datetime.now().astimezone() + timedelta(days=1)).isoformat()

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__)

class addReturnObject:
    def __init__(self, uploadUrls, shareId):
        self.shareId = shareId
        self.uploadUrls = uploadUrls

def main():
    session = requests.Session()
    session.auth = auth.get_authorization()

    filePath = sys.argv[1]

    mimetype = mimetypes.guess_type(filePath)[0]
    if mimetype == "":
        mimetype = "application/octet-stream"
    file = File(filePath, os.stat(filePath).st_size, mimetype)

    requestBody = toJSON(AddShareRequestDTO(filePath, RequestTypes.file, file, False))
    response = session.post("https://api.share.kirschbaum.cloud/add", headers={"Content-Type": "application/json"}, data=requestBody)

    if response.status_code == 201:
        jsonResponse = response.json()
        test = addReturnObject(jsonResponse["uploadUrls"], jsonResponse["shareId"])
        print("UploadId: " + test.shareId)

        parts = splitFileForUpload(filePath, test)
        test3 = json.dumps({"parts": parts})

        print("Calling Upload Complete... ")
        completeResponse = session.post("https://api.share.kirschbaum.cloud/completeUpload/" + test.shareId, headers={"Content-Type": "application/json"}, data=test3)
        if completeResponse.status_code != 201:
            print(str(completeResponse.status_code) + completeResponse.text)
        else:
            print("https://share.kirschbaum.cloud/d/" + test.shareId)

    else:
        print(str(response.status_code) + response.text)
        exit()


if __name__ == "__main__":
    main()

