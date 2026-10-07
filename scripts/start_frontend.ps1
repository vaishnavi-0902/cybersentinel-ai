$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
streamlit run frontend/app.py
