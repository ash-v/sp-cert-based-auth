$pfxPath = "C:\Path\To\Your\Certificate.pfx"
$base64Path = "C:\Path\To\certificate_base64.txt"

# Read the .pfx file and convert to base64
$pfxBytes = [System.IO.File]::ReadAllBytes($pfxPath)
$pfxBase64 = [System.Convert]::ToBase64String($pfxBytes)

# Write the base64 string to a file
[System.IO.File]::WriteAllText($base64Path, $pfxBase64)

Write-Output "Base64-encoded certificate saved to $base64Path"
