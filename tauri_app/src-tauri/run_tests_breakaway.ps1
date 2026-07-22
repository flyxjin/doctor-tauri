# 通过 CreateProcess 与 CREATE_BREAKAWAY_FROM_JOB 标志启动测试 exe
# 这会让子进程脱离父进程的 Job 对象，避免沙箱 DLL 注入

Add-Type -Name "Kernel32" -Namespace "Win32" -MemberDefinition @'
[StructLayout(LayoutKind.Sequential)]
public struct STARTUPINFO
{
    public int cb;
    public string lpReserved;
    public string lpDesktop;
    public string lpTitle;
    public uint dwX;
    public uint dwY;
    public uint dwXSize;
    public uint dwYSize;
    public uint dwXCountChars;
    public uint dwYCountChars;
    public uint dwFillAttribute;
    public uint dwFlags;
    public ushort wShowWindow;
    public ushort cbReserved2;
    public IntPtr lpReserved2;
    public IntPtr hStdInput;
    public IntPtr hStdOutput;
    public IntPtr hStdError;
}

[StructLayout(LayoutKind.Sequential)]
public struct PROCESS_INFORMATION
{
    public IntPtr hProcess;
    public IntPtr hThread;
    public uint dwProcessId;
    public uint dwThreadId;
}

[StructLayout(LayoutKind.Sequential)]
public struct SECURITY_ATTRIBUTES
{
    public int nLength;
    public IntPtr lpSecurityDescriptor;
    public bool bInheritHandle;
}

public const uint CREATE_BREAKAWAY_FROM_JOB = 0x01000000;
public const uint CREATE_NO_WINDOW = 0x08000000;
public const uint CREATE_SUSPENDED = 0x00000004;
public const uint NORMAL_PRIORITY_CLASS = 0x00000020;
public const int STILL_ACTIVE = 259;

[DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
public static extern bool CreateProcessW(
    string lpApplicationName,
    string lpCommandLine,
    ref SECURITY_ATTRIBUTES lpProcessAttributes,
    ref SECURITY_ATTRIBUTES lpThreadAttributes,
    bool bInheritHandles,
    uint dwCreationFlags,
    IntPtr lpEnvironment,
    string lpCurrentDirectory,
    ref STARTUPINFO lpStartupInfo,
    out PROCESS_INFORMATION lpProcessInformation);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool GetExitCodeProcess(IntPtr hProcess, out uint lpExitCode);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool CloseHandle(IntPtr hObject);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool ReadFile(IntPtr hFile, [Out] byte[] lpBuffer, uint nNumberOfBytesToRead, out uint lpNumberOfBytesRead, IntPtr lpOverlapped);

[DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
public static extern IntPtr CreateFileW(string lpFileName, uint dwDesiredAccess, uint dwShareMode, IntPtr lpSecurityAttributes, uint dwCreationDisposition, uint dwFlagsAndAttributes, IntPtr hTemplateFile);

public const uint GENERIC_READ = 0x80000000;
public const uint GENERIC_WRITE = 0x40000000;
public const uint CREATE_ALWAYS = 2;
public const uint OPEN_EXISTING = 3;
public const uint FILE_ATTRIBUTE_NORMAL = 0x80;
'@

$exe = "D:\learn\trae\tauri_app\src-tauri\target\debug\deps\medicine_system_lib-5add84c37ef0f634.exe"
$outFile = "D:\learn\trae\tauri_app\src-tauri\test_output.log"
$errFile = "D:\learn\trae\tauri_app\src-tauri\test_error.log"

Remove-Item -Path $outFile, $errFile -ErrorAction SilentlyContinue

# 创建输出文件句柄
$startupInfo = New-Object Win32.Kernel32+STARTUPINFO
$startupInfo.cb = [System.Runtime.InteropServices.Marshal]::SizeOf($startupInfo)

$pi = New-Object Win32.Kernel32+PROCESS_INFORMATION

$cmdLine = "`"$exe`" --nocapture"

# 创建用于重定向的文件句柄
$outHandle = [Win32.Kernel32]::CreateFileW($outFile, [Win32.Kernel32]::GENERIC_WRITE, 0, [IntPtr]::Zero, [Win32.Kernel32]::CREATE_ALWAYS, [Win32.Kernel32]::FILE_ATTRIBUTE_NORMAL, [IntPtr]::Zero)
$errHandle = [Win32.Kernel32]::CreateFileW($errFile, [Win32.Kernel32]::GENERIC_WRITE, 0, [IntPtr]::Zero, [Win32.Kernel32]::CREATE_ALWAYS, [Win32.Kernel32]::FILE_ATTRIBUTE_NORMAL, [IntPtr]::Zero)

if ($outHandle -eq [IntPtr]::new(-1)) {
    Write-Host "Failed to create output file handle"
    exit 1
}

$startupInfo.dwFlags = 0x100  # STARTF_USESTDHANDLES
$startupInfo.hStdOutput = $outHandle
$startupInfo.hStdError = $errHandle
$startupInfo.hStdInput = [IntPtr]::Zero

$sa = New-Object Win32.Kernel32+SECURITY_ATTRIBUTES
$sa.nLength = [System.Runtime.InteropServices.Marshal]::SizeOf($sa)
$sa.bInheritHandle = $true

Write-Host "Creating process with CREATE_BREAKAWAY_FROM_JOB..."
Write-Host "Command: $cmdLine"

$success = [Win32.Kernel32]::CreateProcessW(
    $exe,
    $cmdLine,
    [ref]$sa,
    [ref]$sa,
    $true,
    [Win32.Kernel32]::CREATE_BREAKAWAY_FROM_JOB -bor [Win32.Kernel32]::CREATE_NO_WINDOW -bor [Win32.Kernel32]::NORMAL_PRIORITY_CLASS,
    [IntPtr]::Zero,
    "d:\learn\trae\tauri_app\src-tauri",
    [ref]$startupInfo,
    [ref]$pi
)

if (-not $success) {
    $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
    Write-Host "CreateProcessW failed with error: $err"
    [Win32.Kernel32]::CloseHandle($outHandle) | Out-Null
    [Win32.Kernel32]::CloseHandle($errHandle) | Out-Null
    exit 1
}

Write-Host "Process created. PID: $($pi.dwProcessId)"
Write-Host "Waiting for process to exit..."

$waitResult = [Win32.Kernel32]::WaitForSingleObject($pi.hProcess, 60000)
Write-Host "Wait result: $waitResult"

$exitCode = 0
[void][Win32.Kernel32]::GetExitCodeProcess($pi.hProcess, [ref]$exitCode)
Write-Host ("Exit code: 0x{0:X8}" -f $exitCode)

[Win32.Kernel32]::CloseHandle($pi.hProcess) | Out-Null
[Win32.Kernel32]::CloseHandle($pi.hThread) | Out-Null
[Win32.Kernel32]::CloseHandle($outHandle) | Out-Null
[Win32.Kernel32]::CloseHandle($errHandle) | Out-Null

Write-Host "===== STDOUT ====="
if (Test-Path $outFile) {
    Get-Content $outFile
} else {
    Write-Host "No output file"
}
Write-Host "===== STDERR ====="
if (Test-Path $errFile) {
    Get-Content $errFile
} else {
    Write-Host "No error file"
}
