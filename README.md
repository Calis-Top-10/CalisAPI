# CalisAPI

## Introduction
This repository contains many stuffs for handling requests from clients, performs authentication and authorization, applies security policies, and routes the requests to the appropriate backend services.

## Example of Usage
To use this API, follow instructions bellow:
```
curl -X GET "https://gateway-calis-46kwzo0x.an.gateway.dev/v1/whoami" -H "accept: application/json" -H "Authorization: Bearer <your_id_token>"
```
The API will provide a JSON-formatted response.
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
For any further API documentation, you can visit [API Documentation](https://gateway-calis-46kwzo0x.an.gateway.dev/v1/docs#/) and see various API endpoints.
