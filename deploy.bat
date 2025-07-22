@echo off
title CatatUang - Deployment Helper

echo.
echo ==========================================
echo    CatatUang - Deployment Helper
echo ==========================================
echo.

:menu
echo Select an option:
echo.
echo 1. Deploy to Vercel (Production)
echo 2. Deploy to Vercel (Preview)
echo 3. Test Local Development
echo 4. Setup Environment Variables
echo 5. Check Deployment Status
echo 6. Open Vercel Dashboard
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto deploy_prod
if "%choice%"=="2" goto deploy_preview
if "%choice%"=="3" goto test_local
if "%choice%"=="4" goto setup_env
if "%choice%"=="5" goto check_status
if "%choice%"=="6" goto open_dashboard
if "%choice%"=="7" goto exit
goto menu

:deploy_prod
echo.
echo 🚀 Deploying to Production...
echo.
echo Make sure you have:
echo ✅ Edited .env.local with your credentials
echo ✅ Logged in to Vercel (vercel login)
echo ✅ Set environment variables in Vercel Dashboard
echo.
pause
vercel --prod
echo.
echo ✅ Production deployment complete!
goto menu

:deploy_preview
echo.
echo 🔍 Deploying Preview...
echo.
vercel
echo.
echo ✅ Preview deployment complete!
goto menu

:test_local
echo.
echo 🧪 Testing Local Development...
echo.
echo Starting local development server...
vercel dev
goto menu

:setup_env
echo.
echo ⚙️ Environment Variables Setup
echo.
echo Required environment variables:
echo.
echo 1. GOOGLE_SERVICE_ACCOUNT_KEY
echo    - Get from Google Cloud Console
echo    - Service Account JSON (base64 encoded)
echo.
echo 2. GOOGLE_SHEETS_ID  
echo    - Get from Google Sheets URL
echo    - Format: https://docs.google.com/spreadsheets/d/{ID}/edit
echo.
echo 3. WHATSAPP_VERIFY_TOKEN
echo    - Set this to: catatuang_2025
echo.
echo 4. WHATSAPP_TOKEN (Optional)
echo    - Get from Meta for Developers
echo    - Only needed for production WhatsApp
echo.
echo Set these in:
echo - Local: .env.local file
echo - Production: Vercel Dashboard > Project > Settings > Environment Variables
echo.
pause
goto menu

:check_status
echo.
echo 📊 Checking Deployment Status...
echo.
vercel ls
echo.
echo Recent deployments:
vercel logs --since=1h
pause
goto menu

:open_dashboard
echo.
echo 🌐 Opening Vercel Dashboard...
start https://vercel.com/dashboard
goto menu

:exit
echo.
echo Thank you for using CatatUang! 👋
echo.
pause
exit
