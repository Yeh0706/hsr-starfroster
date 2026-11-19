# Build Starfroster with PyInstaller (folder version).
# Builds in %TEMP% (Python may not write into Documents because of Controlled Folder Access),
# trims unused Qt files, then copies the result to .\dist\Starfroster
# Usage:  powershell -ExecutionPolicy Bypass -File .\build.ps1

$ErrorActionPreference = "Stop"
$proj  = $PSScriptRoot
$entry = (Get-ChildItem $proj -Filter *.pyw | Select-Object -First 1).FullName
$tmp   = Join-Path $env:TEMP "starfroster_build"
New-Item -ItemType Directory -Force $tmp | Out-Null

$excludes = @(
  "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
  "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
  "PySide6.Qt3DCore", "PySide6.QtQuick", "PySide6.QtQml", "PySide6.QtQuickWidgets",
  "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtBluetooth", "PySide6.QtPositioning",
  "tkinter", "PIL", "numpy", "scipy", "colorthief"
) | ForEach-Object { "--exclude-module"; $_ }

python -m PyInstaller --noconfirm --clean --windowed --name Starfroster `
  --icon "$proj\assets\icon.ico" `
  --add-data "$proj\assets;assets" `
  --paths "$proj" `
  --collect-data qfluentwidgets `
  --collect-data opencc `
  @excludes `
  --distpath "$tmp\dist" --workpath "$tmp\work" --specpath "$tmp" `
  "$entry"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

# Trim files the editor never uses
$int = "$tmp\dist\Starfroster\_internal\PySide6"
$trim = @("opengl32sw.dll", "Qt6Pdf.dll", "Qt6Quick.dll", "Qt6Qml.dll", "Qt6QmlModels.dll", "Qt6QmlMeta.dll",
          "Qt6QmlWorkerScript.dll", "Qt6VirtualKeyboard.dll", "translations",
          "plugins\imageformats\qpdf.dll", "plugins\imageformats\qtiff.dll", "plugins\imageformats\qicns.dll",
          "plugins\imageformats\qtga.dll", "plugins\imageformats\qwbmp.dll", "plugins\platforminputcontexts")
foreach ($t in $trim) { $p = Join-Path $int $t; if (Test-Path $p) { Remove-Item $p -Recurse -Force } }

$dest = Join-Path $proj "dist\Starfroster"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
New-Item -ItemType Directory -Force (Join-Path $proj "dist") | Out-Null
Copy-Item "$tmp\dist\Starfroster" $dest -Recurse
$size = (Get-ChildItem $dest -Recurse | Measure-Object Length -Sum).Sum / 1MB
"Done: $dest  ({0:N0} MB)" -f $size

# Zip for sharing / backup
$zip = Join-Path $proj "dist\Starfroster.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $dest -DestinationPath $zip -CompressionLevel Optimal
"Zip:  $zip  ({0:N0} MB)" -f ((Get-Item $zip).Length / 1MB)
