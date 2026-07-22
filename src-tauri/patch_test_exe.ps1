$exe = "D:\learn\trae\tauri_app\src-tauri\target\debug\deps\medicine_system_lib-87d48804e249cebd.exe"
$patchedExe = "D:\learn\trae\tauri_app\src-tauri\target\debug\deps\medicine_system_lib_patched.exe"

$bytes = [System.IO.File]::ReadAllBytes($exe)
Write-Host "Original exe size: $($bytes.Length) bytes"

$target = [System.Text.Encoding]::ASCII.GetBytes("api-ms-win-core-synch-l1-2-0.dll")
$replacement = [System.Text.Encoding]::ASCII.GetBytes("kernelbase.dll")

$targetLen = $target.Length
$replLen = $replacement.Length

Write-Host "Target length: $targetLen"
Write-Host "Replacement length: $replLen"

$positions = @()
$end = $bytes.Length - $targetLen
for ($i = 0; $i -le $end; $i++) {
    $match = $true
    for ($j = 0; $j -lt $targetLen; $j++) {
        if ($bytes[$i + $j] -ne $target[$j]) {
            $match = $false
            break
        }
    }
    if ($match) {
        $positions += $i
        Write-Host ("Found at: 0x{0:X8}" -f $i)
        $i = $i + $targetLen - 1
    }
}

Write-Host "Total found: $($positions.Count)"

foreach ($pos in $positions) {
    for ($k = 0; $k -lt $replLen; $k++) {
        $bytes[$pos + $k] = $replacement[$k]
    }
    $bytes[$pos + $replLen] = 0
    $startNull = $replLen + 1
    for ($k = $startNull; $k -lt $targetLen; $k++) {
        $bytes[$pos + $k] = 0
    }
}

[System.IO.File]::WriteAllBytes($patchedExe, $bytes)
Write-Host "Patched exe: $patchedExe"
Write-Host "Size: $((Get-Item $patchedExe).Length) bytes"
