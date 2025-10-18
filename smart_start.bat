@echo off
chcp 65001 >nul
title 京盛传媒企业版智能体 - 启动助手
cd /d "%~dp0"

echo 检查虚拟环境...
if exist .venv\Scripts\activate (
  call .venv\Scripts\activate
) else (
  echo 创建虚拟环境并安装依赖...
  python -m venv .venv
  call .venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
)

:: 检测端口/占用
set PORT=8501
:checkport
netstat -ano | findstr :%PORT% >nul
if %errorlevel%==0 (
  echo 端口 %PORT% 被占用，尝试下一个...
  set /a PORT+=1
  goto checkport
)

echo 启动 Streamlit...
start "" cmd /c "streamlit run run_launcher.py --server.port %PORT%"

echo 启动调度器 (后台)...
start "" cmd /c "python scheduler.py"

timeout /t 2 >nul
start http://localhost:%PORT%

echo 启动完成，浏览器已打开。

:menu
echo.
echo ====================== 功能菜单 ======================
echo 1. 启动Amazon爬虫程序 (交互式模式)
echo 2. 启动Amazon爬虫程序 (基础模式 - 仅需输入URL)
echo 3. 启动Amazon爬虫程序 (批量模式 - 处理多个URL)
echo 4. 退出菜单
echo =====================================================
echo.
set /p choice=请选择要执行的功能 (1-4): 

if "%choice%"=="1" goto amazon_crawler_interactive
if "%choice%"=="2" goto amazon_crawler_basic
if "%choice%"=="3" goto amazon_crawler_batch
if "%choice%"=="4" goto end

:amazon_crawler_interactive
cls
echo =================== Amazon爬虫程序 (交互式模式) ===================
echo 此模式允许您配置所有爬虫参数，实现完整功能。
echo ===========================================================

set /p "crawler_url=请输入Amazon搜索页面URL: "
set /p "max_items=请输入最大采集商品数量 (默认: 50): "
if "%max_items%"=="" set max_items=50

set deep_detail=n
echo.
echo 是否采集商品详细信息？
set /p "deep_detail_choice=请输入 (y/n, 默认: n): "
if /i "%deep_detail_choice%"=="y" set deep_detail=--deep-detail

set include_reviews=n
echo.
echo 是否采集商品评论？
set /p "reviews_choice=请输入 (y/n, 默认: n): "
if /i "%reviews_choice%"=="y" (
    set include_reviews=--include-reviews
    set /p "max_reviews=请输入每个商品最大评论数 (默认: 5): "
    if "%max_reviews%"=="" set max_reviews=5
    set max_reviews=--max-reviews %max_reviews%
) else (
    set max_reviews=
)

echo.
echo 正在启动Amazon爬虫程序...
echo 配置: URL=%crawler_url%, 最大商品数=%max_items%, 详细信息=%deep_detail_choice%, 评论=%reviews_choice%
echo ===========================================================

start "Amazon爬虫程序" cmd /c "python amazon_crawler.py --url "%crawler_url%" --max-items %max_items% %deep_detail% %include_reviews% %max_reviews%"
goto menu

:amazon_crawler_basic
cls
echo =================== Amazon爬虫程序 (基础模式) ===================
echo 此模式快速启动爬虫，仅需输入URL。
echo ===========================================================

set /p "crawler_url=请输入Amazon搜索页面URL: "
echo 正在启动Amazon爬虫程序 (基础模式)...
start "Amazon爬虫程序" cmd /c "python amazon_crawler.py --url "%crawler_url%" --max-items 50"
goto menu

:amazon_crawler_batch
cls
echo =================== Amazon爬虫程序 (批量模式) ===================
echo 此模式处理多个URL，请确保已准备好包含URL列表的文本文件。
echo ===========================================================

set /p "batch_file=请输入URL列表文件路径 (默认为 urls.txt): "
if "%batch_file%"=="" set batch_file=urls.txt

set /p "max_items=请输入每个URL最大采集商品数量 (默认: 50): "
if "%max_items%"=="" set max_items=50

set deep_detail=n
echo.
echo 是否采集商品详细信息？
set /p "deep_detail_choice=请输入 (y/n, 默认: n): "
if /i "%deep_detail_choice%"=="y" set deep_detail=--deep-detail

echo 正在启动Amazon爬虫程序 (批量模式)...
echo 配置: 文件=%batch_file%, 最大商品数=%max_items%, 详细信息=%deep_detail_choice%
echo ===========================================================

start "Amazon爬虫程序" cmd /c "python amazon_crawler.py --batch-file "%batch_file%" --max-items %max_items% %deep_detail%"
goto menu

:end
echo 感谢使用京盛传媒企业版智能体！
pause
