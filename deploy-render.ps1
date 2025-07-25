# Render Deployment PowerShell Script
param(
    [string]$Action = "deploy"
)

Write-Host "Render CLI Alternative - PowerShell Edition" -ForegroundColor Cyan
Write-Host "=================================================="

function Show-DeploymentInfo {
    Write-Host "Your project is ready for Render deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files ready for deployment:" -ForegroundColor Green
    Get-ChildItem -Name "*.py", "*.txt", "*.yaml", "*.md" | ForEach-Object {
        Write-Host "  * $_" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Deployment Methods:" -ForegroundColor Yellow
    Write-Host "1. Web Dashboard (Recommended):"
    Write-Host "   - Go to https://render.com"
    Write-Host "   - Connect GitHub: sheshashai/vet-clinic-ai-chatbot"
    Write-Host "   - Auto-deploy with render.yaml"
    Write-Host ""
    Write-Host "2. Manual Git Deploy:"
    Write-Host "   - Push changes to main branch"
    Write-Host "   - Render auto-deploys on git push"
    Write-Host ""
    Write-Host "Environment Variables to set in Render:"
    Write-Host "   OPENAI_API_KEY=sk-proj-..."
    Write-Host "   FLASK_ENV=production"
    Write-Host "   SECRET_KEY=(auto-generated)"
}

function Test-Prerequisites {
    $missing = @()
    
    if (!(Test-Path "server.py")) { $missing += "server.py" }
    if (!(Test-Path "requirements.txt")) { $missing += "requirements.txt" }
    if (!(Test-Path "render.yaml")) { $missing += "render.yaml" }
    
    if ($missing.Count -gt 0) {
        Write-Host "Missing files: $($missing -join ', ')" -ForegroundColor Red
        return $false
    }
    
    Write-Host "All required files present" -ForegroundColor Green
    return $true
}

function Push-ToGitHub {
    Write-Host "Pushing latest changes to GitHub..." -ForegroundColor Yellow
    
    git add .
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Deploy: Updated at $timestamp"
    git push origin main
    
    Write-Host "Changes pushed to GitHub" -ForegroundColor Green
    Write-Host "Render will auto-deploy in 1-2 minutes" -ForegroundColor Cyan
}

# Main execution
switch ($Action.ToLower()) {
    "deploy" {
        if (Test-Prerequisites) {
            Show-DeploymentInfo
            $response = Read-Host "`nPush changes to GitHub for auto-deploy? (y/N)"
            if ($response -eq "y" -or $response -eq "Y") {
                Push-ToGitHub
            }
        }
    }
    "push" {
        Push-ToGitHub
    }
    "info" {
        Show-DeploymentInfo
    }
    default {
        Write-Host "Usage: .\deploy-render.ps1 [deploy|push|info]" -ForegroundColor Yellow
    }
}
