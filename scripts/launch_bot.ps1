$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$envFile = Join-Path $projectRoot ".env"

$tokenLine = $null
if (Test-Path -LiteralPath $envFile) {
    $tokenLine = Get-Content -LiteralPath $envFile |
        Where-Object { $_ -match "^TELEGRAM_BOT_TOKEN=" } |
        Select-Object -First 1
}

if (-not $tokenLine -or [string]::IsNullOrWhiteSpace($tokenLine.Substring("TELEGRAM_BOT_TOKEN=".Length))) {
    $secureToken = Read-Host "Enter the Telegram bot token (saved locally for next time)" -AsSecureString
    if ($secureToken.Length -eq 0) {
        throw "A Telegram bot token is required."
    }

    $tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try {
        $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
        if ($tokenLine) {
            $envLines = Get-Content -LiteralPath $envFile
            for ($index = 0; $index -lt $envLines.Count; $index++) {
                if ($envLines[$index] -match "^TELEGRAM_BOT_TOKEN=") {
                    $envLines[$index] = "TELEGRAM_BOT_TOKEN=$token"
                    break
                }
            }
        }
        else {
            $envLines = @()
            if (Test-Path -LiteralPath $envFile) {
                $envLines = @(Get-Content -LiteralPath $envFile)
            }
            $envLines += "TELEGRAM_BOT_TOKEN=$token"
        }
        Set-Content -LiteralPath $envFile -Value $envLines -Encoding ASCII
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
        $token = $null
    }
}

$tokenLine = Get-Content -LiteralPath $envFile |
    Where-Object { $_ -match "^TELEGRAM_BOT_TOKEN=" } |
    Select-Object -First 1
if (-not $tokenLine) {
    throw "The local .env file does not contain TELEGRAM_BOT_TOKEN."
}

$env:TELEGRAM_BOT_TOKEN = $tokenLine.Substring("TELEGRAM_BOT_TOKEN=".Length).Trim()
if ([string]::IsNullOrWhiteSpace($env:TELEGRAM_BOT_TOKEN)) {
    throw "The Telegram bot token in .env is empty."
}

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $pythonPath = $pythonCommand.Source
}
elseif (Test-Path -LiteralPath "C:\Python314\python.exe") {
    $pythonPath = "C:\Python314\python.exe"
}
else {
    throw "Python was not found. Install Python or add python.exe to PATH."
}

$apiReady = $false
try {
    $null = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -TimeoutSec 2
    $apiReady = $true
}
catch {
    $apiReady = $false
}

if (-not $apiReady) {
    $apiProcess = Start-Process -FilePath $pythonPath `
        -ArgumentList @("-m", "uvicorn", "tourist_routes.api.main:app", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $projectRoot -PassThru

    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Seconds 1
        if ($apiProcess.HasExited) {
            throw "The API process exited before it became ready. Check its window for errors."
        }

        try {
            $null = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -TimeoutSec 2
            $apiReady = $true
            break
        }
        catch {
            $apiReady = $false
        }
    }

    if (-not $apiReady) {
        throw "The API did not become ready at http://127.0.0.1:8000/."
    }
}

$null = Start-Process -FilePath $pythonPath `
    -ArgumentList @("-m", "tourist_routes.bot") `
    -WorkingDirectory $projectRoot -PassThru

Write-Host "The routes API and Telegram bot have been started."
Write-Host "Keep their terminal windows open. Close them to stop the services."
