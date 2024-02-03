#!/usr/bin/env python

import json
import requests
import sys
import mimetypes
import math
import os
import pytz
from datetime import datetime, timedelta

test = pytz.timezone("Europe/Berlin")

def callApiWithKey(url, data):
    print("Calling: URL")
    print("Response: ")
    return requests.put(url, data=data).headers["Etag"]


def splitFileForUpload(filePath, response):
    totalSize = os.stat(filePath).st_size

    file = open(filePath, "rb")
    filesize = int(math.ceil(totalSize/len(response.uploadUrls)))
    parts = []

    print(totalSize)
    print(filesize)
    print("Split into " + str(filesize) + "bytes size")
    currentByte = 0

    for x in range(0,len(response.uploadUrls)):
        file.seek(currentByte)
        data = file.read(filesize)
        currentByte += filesize
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
        self.expires = (datetime.now() + timedelta(days=1)).isoformat()

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__)

class addReturnObject:
    def __init__(self, uploadUrls, shareId):
        self.shareId = shareId
        self.uploadUrls = uploadUrls

def main():
    token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJCOXNySzRBWkpyZXN4Vmd5SUVoQkRsNjlvc1otbGl6cDFiSWtfT2xFZFFvIn0.eyJleHAiOjE3MDY5MjI4MTgsImlhdCI6MTcwNjkyMjUxOCwiYXV0aF90aW1lIjoxNzAzNzQ4OTEyLCJqdGkiOiJlZjhiMTg2NC1mNDMzLTRlZTktODBhYi02ZGMwODgyNzI0YWYiLCJpc3MiOiJodHRwczovL2lkLmVsaXRlMTIuZGUvcmVhbG1zL2VsaXRlMTIiLCJhdWQiOiJjbG91ZC1zaGFyZS1iYWNrZW5kIiwic3ViIjoiMjFiNTFmZmEtYjUzNi00ZDBiLTljYTUtYWVhZTFhZGQ5MzMyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY2xvdWQtc2hhcmUtZnJvbnRlbmQiLCJzZXNzaW9uX3N0YXRlIjoiYzg5NDhkY2MtNzY3Ni00YWRjLWE3NjEtOWE0ZjU3YmNkOTY0Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6ImM4OTQ4ZGNjLTc2NzYtNGFkYy1hNzYxLTlhNGY1N2JjZDk2NCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJyb2xlcyI6WyJtZW1iZXIiXSwibmFtZSI6IkxhcnMgS2lyc2NoYmF1bSIsInByZWZlcnJlZF91c2VybmFtZSI6ImxhcnMiLCJnaXZlbl9uYW1lIjoiTGFycyIsImZhbWlseV9uYW1lIjoiS2lyc2NoYmF1bSIsImVtYWlsIjoibGFyc0BlbGl0ZTEyLmRlIn0.OxDZZ8FAQma9gK9y-zOiX_GCLDCbi45Ya0qTJ5f3V1mCYZ_IoTzwIddww1cioJeFxb9oN6ryebIS3aXA6ERxYwk3fPir19Pft9HsikaSrN90fmLlROfRJ4KdMGMz2qXyETbkiMOdZddKoFWAbP--dfxD74_7i9zM1Av599kuKpB0gMjIBzt1BvUYXOpuseK9EfkR2aRCBGhr8XtlzEuf2lLydPuTurU6CG4VpNtA2iiVa8B4-l-YaNq2rEQzyA654ZlCdg2s61GeaDNQi_dyvqMJ8MHXgbRbwVY9gayohD3CrfsZ5jtMVDDevliCeRtWVdK4QOtttqNneaZSbmXCuA"
    filePath = sys.argv[1]

    mimetype = mimetypes.guess_type(filePath)[0]
    file = File(filePath, sys.getsizeof(filePath), mimetype)

    requestBody = toJSON(AddShareRequestDTO(filePath, RequestTypes.file, file, False))

    response = requests.post("https://api.share.kirschbaum.cloud/add", headers={"Authorization": token, "Content-Type": "application/json"},data=requestBody)
    if response.status_code == 201:
        jsonResponse = response.json()
        test = addReturnObject(jsonResponse["uploadUrls"], jsonResponse["shareId"])
        print("UploadId: " + test.shareId)

        parts = splitFileForUpload(filePath, test)
        test3 = json.dumps({"parts": parts})

        print("Calling Upload Complete: ")
        print(requests.post("https://api.share.kirschbaum.cloud/completeUpload/" + test.shareId, headers={"Authorization": token, "Content-Type": "application/json"}, data=test3))
    else:
        print(str(response.status_code) + response.text)
        return


if __name__ == "__main__":
    main()

