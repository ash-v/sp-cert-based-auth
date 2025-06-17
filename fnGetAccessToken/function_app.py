import os
import logging
import uuid
import time
import jwt
import json
import requests
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
import azure.functions as func
from azure.identity import DefaultAzureCredential
import base64
from dotenv import load_dotenv
load_dotenv()

app = func.FunctionApp()


def get_access_token_from_b64(client_id, tenant_id, pfx_b64, pfx_password):
    # Decode base64-encoded PFX
    pfx_data = base64.b64decode(pfx_b64)

    # Load private key and certificate
    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        pfx_data, pfx_password.encode()
    )

    # Compute SHA-1 thumbprint for x5t header
    thumbprint = certificate.fingerprint(hashes.SHA1())
    x5t = base64.urlsafe_b64encode(thumbprint).decode("utf-8").rstrip("=")

    # JWT payload
    now = int(time.time())
    payload = {
        "aud": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        "iss": client_id,
        "sub": client_id,
        "jti": str(uuid.uuid4()),
        "nbf": now,
        "exp": now + 600,
        "iat": now
    }

    # JWT header with x5t
    headers = {
        "alg": "RS256",
        "typ": "JWT",
        "x5t": x5t
    }

    # Encode JWT
    client_assertion = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)
    if isinstance(client_assertion, bytes):
        client_assertion = client_assertion.decode("utf-8")

    # Token request
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": client_assertion,
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, headers=headers, data=body)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    response_data = json.loads(response.text)

    # Extract the token
    access_token = response_data["access_token"]
    test_token(access_token=access_token)
    response.raise_for_status()
    
    return response.json()["access_token"]


def test_token(access_token:str):
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://graph.microsoft.com/v1.0/users", headers=headers)

    print("Tess token Status Code:", response.status_code)
    print("Test token Response:", response.json())
 


@app.function_name(name="GetAccessToken")
@app.route(route="get-access-token", auth_level=func.AuthLevel.FUNCTION)
def get_access_token_http(req: func.HttpRequest) -> func.HttpResponse:
    try:
        client_id = req.params.get("client_id") or os.environ["CLIENT_ID"]
        tenant_id = req.params.get("tenant_id") or os.environ["TENANT_ID"]
        pfx_b64 = os.environ["PFX_BASE64"]  # <-- base64 version of .pfx
        pfx_password = os.environ["PFX_PASSWORD"]

        token = get_access_token_from_b64(client_id, tenant_id, pfx_b64, pfx_password)
        return func.HttpResponse(token, status_code=200)

    except Exception as e:
        logging.exception("Token generation failed")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
