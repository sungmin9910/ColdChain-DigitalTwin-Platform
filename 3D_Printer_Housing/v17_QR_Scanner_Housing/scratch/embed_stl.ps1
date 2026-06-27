$dir = "c:\Users\yuyub\Desktop\hsm\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v17_QR_Scanner_Housing"
$leftB64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("$dir\17_qr_scanner_housing_left_half.stl"))
$rightB64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("$dir\17_qr_scanner_housing_right_half.stl"))
$htmlPath = "$dir\viewer.html"
$html = [IO.File]::ReadAllText($htmlPath, [Text.Encoding]::UTF8)
if ($html -match "<!-- EMBEDDED STL DATA START -->") {
    $html = ($html -split "<!-- EMBEDDED STL DATA START -->")[0]
    if (-not $html.Trim().EndsWith("</html>")) { $html += "`n</html>" }
}
$embed = "<!-- EMBEDDED STL DATA START -->`n<script>`n    const LEFT_HALF_STL_BASE64 = `"$leftB64`";`n    const RIGHT_HALF_STL_BASE64 = `"$rightB64`";`n</script>`n</html>"
$newHtml = $html.Replace("</html>", $embed)
[IO.File]::WriteAllText($htmlPath, $newHtml, [Text.Encoding]::UTF8)
Write-Output "Successfully embedded STL inside HTML via PowerShell!"
