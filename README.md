# sp-cert-based-auth
This repo contains code to generate access token using Azure App registration security certificate


# Steps 
1. Create an app registration in Azure Entra ID
2. Generate security certificate (.cer and .pfx)
3. Upload .cer to certificate section of you app registration 
4. On app registration page, grant it User.Read.All permsision and "Grant admin consent" under API permissions
5. Convert .pfx to base64 encoded format
6. copy/paste base64 encoded version of .pfx file to env variable of your Azure function or Keyvault, whichever approach you choose. This step assumes you have an azure function created.
7. Deploy the code in folder fnGetAccessToken to you azure function 
8. Now, when you hit this function's url... it will return a new token with an expiry of 10 mins.

