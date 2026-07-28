$ErrorActionPreference = "Stop"
$HomeworkRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $HomeworkRoot
try {
    python pipeline.py
    if ($LASTEXITCODE -ne 0) {
        throw "Pipeline failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
