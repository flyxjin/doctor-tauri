# 通过 cmd.exe 重定向运行测试 exe
$exe = "D:\learn\trae\tauri_app\src-tauri\target\debug\deps\medicine_system_lib-87d48804e249cebd.exe"
$outFile = "D:\learn\trae\tauri_app\src-tauri\test_output.log"

# 删除旧输出文件
Remove-Item -Path $outFile -ErrorAction SilentlyContinue

# 使用 cmd.exe 重定向
$cmdLine = "`"$exe`" --nocapture > `"$outFile`" 2>&1"
Write-Host "Executing: $cmdLine"

$proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $cmdLine -NoNewWindow -PassThru -Wait

Write-Host "Exit code: 0x$($proc.ExitCode.ToString('X8'))"

# 读取输出文件
if (Test-Path $outFile) {
    Write-Host "===== Test Output ====="
    Get-Content -Path $outFile
} else {
    Write-Host "No output file generated"
}
