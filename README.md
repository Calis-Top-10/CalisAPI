# CalisAPI

## Introduction
This repository contains many stuffs for handling requests from clients, performs authentication and authorization, applies security policies, and routes the requests to the appropriate backend services.

## Architecture
![architecture_image](https://github.com/Calis-Top-10/CalisAPI/blob/main/cloud%20architecture.png)  
In the cloud architecture, there are mainly 3 components: API Gateway, Cloud Functions, and Google Datastore. 
-  API Gateway  
   API Gateway is needed to serve the API. Currently, all endpoints backend are powered by cloud functions, we may need other backend in the future.
-  Cloud Functions  
   All cloud functions are private (except for login/whoami). This means that even if we have the url and the token, we won't be able to invoke/call the functions. So, we must call the API through the API Gateway.
-  Google Datastore  
  Google Datastore is used to store all user data.

## Development Flow
- Create a function in appropriate module, you may create new module if necessary
- Make sure wrap your function with `auth` decorator, indicating that it's a private API
- Link/import your function to `main.py`
- Test your function locally `functions-framework --debug --target your_func`
- Commit and pull to **make sure you got the lattest terraform state**
- Update the `main.tf` to include your new function
- Do plan and apply the terraform, **please dont manually deploy the function**
- Update `calisgateway.yaml` to route the new endpoint (don't forget to also give detailed documentation) to your new function
- Update gateway configuration with the new calisgateway.yaml
- Wait til the update is complete
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
