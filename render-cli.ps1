#!/usr/bin/env powershell
# Custom Render CLI - PowerShell Implementation
# Usage: .\render-cli.ps1 [command] [options]

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Action = "",
    
    [string]$ApiKey = "",
    [string]$ServiceId = "",
    [string]$RepoUrl = ""
)

$RENDER_API_BASE = "https://api.render.com/v1"

function Show-Help {
    Write-Host "Custom Render CLI - PowerShell Edition" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  deploy              - Deploy current project to Render"
    Write-Host "  status              - Check deployment status"
    Write-Host "  services            - List your services"
    Write-Host "  logs                - Get service logs"
    Write-Host "  auth                - Setup authentication"
    Write-Host "  create              - Create new service"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\render-cli.ps1 deploy"
    Write-Host "  .\render-cli.ps1 status"
    Write-Host "  .\render-cli.ps1 create"
    Write-Host ""
    Write-Host "Note: For full functionality, use the web dashboard at render.com" -ForegroundColor Yellow
}

function Test-GitRepo {
    if (!(Test-Path ".git")) {
        Write-Host "Error: Not a git repository" -ForegroundColor Red
        return $false
    }
    return $true
}

function Get-RepoInfo {
    try {
        $remote = git remote get-url origin
        $branch = git branch --show-current
        return @{
            remote = $remote
            branch = $branch
            status = "ok"
        }
    }
    catch {
        return @{
            status = "error"
            message = "Failed to get git info"
        }
    }
}

function Deploy-ToRender {
    Write-Host "🚀 Deploying to Render..." -ForegroundColor Cyan
    Write-Host ""
    
    if (!(Test-GitRepo)) {
        return
    }
    
    $repoInfo = Get-RepoInfo
    if ($repoInfo.status -eq "error") {
        Write-Host "Error: $($repoInfo.message)" -ForegroundColor Red
        return
    }
    
    Write-Host "📋 Repository Information:" -ForegroundColor Yellow
    Write-Host "  Remote: $($repoInfo.remote)"
    Write-Host "  Branch: $($repoInfo.branch)"
    Write-Host ""
    
    # Check for uncommitted changes
    $status = git status --porcelain
    if ($status) {
        Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
        git status --short
        Write-Host ""
        $commit = Read-Host "Commit and push changes? (y/N)"
        if ($commit -eq "y" -or $commit -eq "Y") {
            git add .
            $message = Read-Host "Commit message (or press Enter for default)"
            if (!$message) {
                $message = "Deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            }
            git commit -m $message
            git push origin $repoInfo.branch
            Write-Host "✅ Changes pushed to GitHub" -ForegroundColor Green
        }
    }
    
    Write-Host "🌐 Deployment Options:" -ForegroundColor Yellow
    Write-Host "1. Auto-deploy via GitHub (Recommended)"
    Write-Host "2. Manual deploy via Render Dashboard"
    Write-Host ""
    
    $choice = Read-Host "Select option (1 or 2)"
    
    switch ($choice) {
        "1" {
            Write-Host "📤 Triggering auto-deployment..." -ForegroundColor Cyan
            Write-Host ""
            Write-Host "✅ If your service is connected to GitHub, it will auto-deploy" -ForegroundColor Green
            Write-Host "🔗 Monitor at: https://dashboard.render.com" -ForegroundColor Cyan
            Write-Host "⏱️  Deployment typically takes 3-5 minutes" -ForegroundColor Yellow
        }
        "2" {
            Write-Host "🖥️  Opening Render Dashboard..." -ForegroundColor Cyan
            Start-Process "https://dashboard.render.com"
            Write-Host "✅ Render Dashboard opened in browser" -ForegroundColor Green
        }
        default {
            Write-Host "ℹ️  No action taken. Use option 1 or 2." -ForegroundColor Yellow
        }
    }
}

function Show-Status {
    Write-Host "📊 Deployment Status" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-GitRepo) {
        $repoInfo = Get-RepoInfo
        Write-Host "📁 Local Repository:" -ForegroundColor Yellow
        Write-Host "  Remote: $($repoInfo.remote)"
        Write-Host "  Branch: $($repoInfo.branch)"
        
        $lastCommit = git log -1 --format="%h - %s (%cr)"
        Write-Host "  Last Commit: $lastCommit"
        Write-Host ""
    }
    
    Write-Host "🌐 Check deployment status at:" -ForegroundColor Yellow
    Write-Host "  https://dashboard.render.com" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Your project files:" -ForegroundColor Yellow
    Get-ChildItem -Name "*.py", "*.txt", "*.yaml", "*.json", "*.md" | ForEach-Object {
        Write-Host "  ✓ $_" -ForegroundColor Green
    }
}

function Create-Service {
    Write-Host "🆕 Create New Render Service" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "📋 Service Creation Steps:" -ForegroundColor Yellow
    Write-Host "1. Go to https://dashboard.render.com" -ForegroundColor White
    Write-Host "2. Click 'New +' → 'Web Service'" -ForegroundColor White
    Write-Host "3. Connect your GitHub repository" -ForegroundColor White
    Write-Host "4. Configure deployment settings" -ForegroundColor White
    Write-Host ""
    
    $open = Read-Host "Open Render Dashboard? (y/N)"
    if ($open -eq "y" -or $open -eq "Y") {
        Start-Process "https://dashboard.render.com"
        Write-Host "✅ Render Dashboard opened" -ForegroundColor Green
    }
}

function Show-Services {
    Write-Host "📝 Your Render Services" -ForegroundColor Cyan
    Write-Host "=======================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 View all services at: https://dashboard.render.com" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Tip: Use the web dashboard for full service management" -ForegroundColor Yellow
}

# Main execution
switch ($Command.ToLower()) {
    "deploy" { Deploy-ToRender }
    "status" { Show-Status }
    "services" { Show-Services }
    "create" { Create-Service }
    "logs" { 
        Write-Host "📄 View logs at: https://dashboard.render.com" -ForegroundColor Cyan
        Start-Process "https://dashboard.render.com"
    }
    "auth" {
        Write-Host "🔐 Authentication is handled via the web dashboard" -ForegroundColor Yellow
        Write-Host "Go to: https://dashboard.render.com/settings" -ForegroundColor Cyan
    }
    default { Show-Help }
}
