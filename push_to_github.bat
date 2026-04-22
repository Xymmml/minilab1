@echo off
chcp 65001 >nul
echo ============================================================
echo   GitHub 上传脚本 - Comp3006J Mini-Project 1
echo ============================================================
echo.
echo 请在浏览器中完成GitHub登录授权
echo.
echo 步骤1: 登录 GitHub
echo   打开浏览器访问: https://github.com
echo   登录你的账户
echo.
echo 步骤2: 创建仓库
echo   点击右上角 + -> New repository
echo   Repository name: Comp3006J-MiniProject1
echo   选择 Private (私有)
echo   不要勾选任何初始化选项
echo   点击 Create repository
echo.
echo 步骤3: 复制仓库URL
echo   创建完成后，复制仓库的HTTPS URL
echo   格式类似: https://github.com/你的用户名/Comp3006J-MiniProject1.git
echo.
echo 步骤4: 在下方输入仓库URL并回车
echo.
set /p REPO_URL="仓库URL: "
echo.
echo 正在添加远程仓库并推送...
git remote add origin %REPO_URL%
"C:\Program Files\Git\cmd\git.exe" remote add origin %REPO_URL%
"C:\Program Files\Git\cmd\git.exe" branch -M main
"C:\Program Files\Git\cmd\git.exe" push -u origin main
echo.
echo ============================================================
echo   上传完成！
echo ============================================================
pause
