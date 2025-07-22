# Google Service Account Base64 Encoder for Windows
# Usage: powershell -File encode_credentials.ps1 [path_to_json_file]

param(
    [string]$JsonFilePath
)

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function ConvertTo-Base64ServiceAccount {
    param($FilePath)
    
    try {
        # Read JSON file
        $jsonContent = Get-Content -Path $FilePath -Raw -Encoding UTF8
        
        # Validate JSON
        $jsonData = $jsonContent | ConvertFrom-Json
        
        $requiredKeys = @('type', 'project_id', 'private_key_id', 'private_key', 'client_email')
        foreach ($key in $requiredKeys) {
            if (-not $jsonData.$key) {
                Write-Error "Missing required key '$key' in service account JSON"
                return $null
            }
        }
        
        if ($jsonData.type -ne 'service_account') {
            Write-Error "JSON file is not a service account file"
            return $null
        }
        
        # Encode to base64
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
        $encoded = [Convert]::ToBase64String($bytes)
        
        Write-Success "Service account JSON successfully encoded!"
        Write-Host "📧 Service Account Email: $($jsonData.client_email)" -ForegroundColor Yellow
        Write-Host "🏗️ Project ID: $($jsonData.project_id)" -ForegroundColor Yellow
        
        Write-Host "`n$('='*60)" -ForegroundColor Cyan
        Write-Host "📋 Copy this base64 string to your environment variable:" -ForegroundColor Cyan
        Write-Host "$('='*60)" -ForegroundColor Cyan
        Write-Host $encoded -ForegroundColor White -BackgroundColor DarkBlue
        Write-Host "$('='*60)" -ForegroundColor Cyan
        
        Write-Host "`n📝 Instructions:" -ForegroundColor Yellow
        Write-Host "1. Copy the base64 string above"
        Write-Host "2. Set as GOOGLE_SERVICE_ACCOUNT_KEY in:"
        Write-Host "   - Local: .env.local file"
        Write-Host "   - Vercel: Dashboard > Settings > Environment Variables"
        Write-Host "3. Make sure to share your Google Sheets with this email:"
        Write-Host "   $($jsonData.client_email)" -ForegroundColor Green
        
        return $encoded
        
    } catch {
        Write-Error "Error processing file: $($_.Exception.Message)"
        return $null
    }
}

# Main script
Write-Host "🔐 Google Service Account Base64 Encoder" -ForegroundColor Cyan
Write-Host "$('='*50)" -ForegroundColor Cyan

# Get file path
if (-not $JsonFilePath) {
    Write-Host "`n📁 Please provide the path to your service account JSON file:" -ForegroundColor Blue
    Write-Host "Example: .\service-account.json"
    Write-Host "Example: C:\path\to\service-account.json"
    
    $JsonFilePath = Read-Host "`nFile path"
    $JsonFilePath = $JsonFilePath.Trim().Trim('"', "'")
    
    if (-not $JsonFilePath) {
        Write-Error "No file path provided"
        exit 1
    }
}

# Check if file exists
if (-not (Test-Path $JsonFilePath)) {
    Write-Error "File not found: $JsonFilePath"
    
    # Look for common files
    Write-Host "`n💡 Looking for common service account file locations..." -ForegroundColor Blue
    $commonNames = @(
        "credentials.json",
        "service-account.json",
        "service_account.json", 
        "google-credentials.json"
    )
    
    $foundFiles = @()
    foreach ($name in $commonNames) {
        if (Test-Path $name) {
            $foundFiles += $name
        }
    }
    
    if ($foundFiles.Count -gt 0) {
        Write-Host "Found these files in current directory:"
        for ($i = 0; $i -lt $foundFiles.Count; $i++) {
            Write-Host "  $($i + 1). $($foundFiles[$i])"
        }
        
        $choice = Read-Host "`nSelect file (1-$($foundFiles.Count)) or Enter to exit"
        if ($choice -and $choice -match '^\d+$') {
            $selectedIdx = [int]$choice - 1
            if ($selectedIdx -ge 0 -and $selectedIdx -lt $foundFiles.Count) {
                $JsonFilePath = $foundFiles[$selectedIdx]
            } else {
                Write-Error "Invalid selection"
                exit 1
            }
        } else {
            exit 1
        }
    } else {
        exit 1
    }
}

# Encode the file
$encoded = ConvertTo-Base64ServiceAccount -FilePath $JsonFilePath

if ($encoded) {
    # Ask to save to file
    $saveChoice = Read-Host "`n💾 Save base64 string to file? (y/n)"
    if ($saveChoice.ToLower() -eq 'y') {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($JsonFilePath)
        $outputFile = "${baseName}_base64.txt"
        
        try {
            $encoded | Out-File -FilePath $outputFile -Encoding utf8
            Write-Success "Base64 string saved to: $outputFile"
        } catch {
            Write-Error "Error saving file: $($_.Exception.Message)"
        }
    }
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
