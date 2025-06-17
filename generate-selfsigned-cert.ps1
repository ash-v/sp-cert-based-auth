# Define certificate properties
$certName = "ADFAppCert"
$certPath = "C:\Certificates"
$certPassword = ConvertTo-SecureString -String "YourStrongPassword123!" -Force -AsPlainText

# Create folder if it doesn't exist
New-Item -ItemType Directory -Force -Path $certPath

# Generate self-signed certificate
$cert = New-SelfSignedCertificate `
-Subject "CN=$certName" `
-CertStoreLocation "Cert:\CurrentUser\My" `
-KeyExportPolicy Exportable `
-KeySpec Signature `
-KeyLength 2048 `
-NotAfter (Get-Date).AddYears(2)


# Export .pfx (includes private key)
Export-PfxCertificate `
-Cert $cert `
-FilePath "$certPath\$certName.pfx" `
-Password $certPassword

# Export .cer (public key only)
Export-Certificate `
-Cert $cert `
-FilePath "$certPath\$certName.cer"

Write-Output "Certificate files created at $certPath"