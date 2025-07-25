@echo off
REM Render CLI Wrapper
PowerShell -ExecutionPolicy Bypass -File "%~dp0render-cli.ps1" %*
