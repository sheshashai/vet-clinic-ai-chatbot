param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Custom Render CLI - PowerShell Edition" -ForegroundColor Cyan
    Write-Host "Commands:"
    Write-Host "  deploy    - Deploy current project to Render"
    Write-Host "  status    - Check deployment status"
    Write-Host "  create    - Create new service"
}

function Deploy-ToRender {
    Write-Host "Deploying to Render..." -ForegroundColor Cyan
    
    # Check git status
    $status = git status --porcelain
    if ($status) {
        Write-Host "You have uncommitted changes:" -ForegroundColor Yellow
        git status --short
        $commit = Read-Host "Commit and push changes? (y/N)"
        if ($commit -eq "y") {
            git add .
            git commit -m "Deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            git push origin main
            Write-Host "Changes pushed to GitHub" -ForegroundColor Green
        }
    }
    
    Write-Host "Deployment Options:"
    Write-Host "1. Auto-deploy via GitHub"
    Write-Host "2. Open Render Dashboard"
    
    $choice = Read-Host "Select option (1 or 2)"
    
    if ($choice -eq "1") {
        Write-Host "Auto-deployment triggered" -ForegroundColor Green
        Write-Host "Monitor at: https://dashboard.render.com"
    }
    elseif ($choice -eq "2") {
        Start-Process "https://dashboard.render.com"
    }
}

function Show-Status {
    Write-Host "Deployment Status" -ForegroundColor Cyan
    $lastCommit = git log -1 --format="%h - %s (%cr)"
    Write-Host "Last Commit: $lastCommit"
    Write-Host "Check status at: https://dashboard.render.com"
}

# Main execution
switch ($Command.ToLower()) {
    "deploy" { Deploy-ToRender }
    "status" { Show-Status }
    "create" { 
        Write-Host "Go to: https://dashboard.render.com"
        Start-Process "https://dashboard.render.com"
    }
    default { Show-Help }
}
