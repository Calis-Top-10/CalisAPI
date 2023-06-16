# CalisAPI
## Introduction
This repository contains many stuffs for handling requests from clients, performs authentication and authorization, applies security policies, and routes the requests to the appropriate backend services.

## Example of Usage
To use this API, follow instructions bellow :
```
curl -X GET "https://gateway-calis-46kwzo0x.an.gateway.dev/v1/login" -H "accept: application/json"
```
The API will provide login as a JSON-formatted response
```
{
  "createdAt": "string",
  "email": "string",
  "children": {
    "random_uuid_value": {
      "yearOfBirth": 0,
      "createdAt": "string",
      "photoUrl": "string",
      "childName": "string"
    }
  }
}
```
For any further API documentation, you can visit [this link](https://gateway-calis-46kwzo0x.an.gateway.dev/v1/docs#/) and see various API endpoints
