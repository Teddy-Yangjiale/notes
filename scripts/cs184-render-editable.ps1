param([string]$TaskFile = "$PSScriptRoot\..\.work\cs184\render-tasks.json")
$ErrorActionPreference = 'Stop'
$tasks = Get-Content -LiteralPath $TaskFile -Raw -Encoding UTF8 | ConvertFrom-Json
$ppt = New-Object -ComObject PowerPoint.Application
$hadPresentations = $ppt.Presentations.Count -gt 0
$done = 0
try {
    foreach ($task in $tasks) {
        $presentation = $null
        try {
            $presentation = $ppt.Presentations.Open($task.pptx, $true, $false, $false)
            $presentation.Slides.Item(1).Export($task.png, 'PNG', 1575, 627)
            $done += 1
            if (($done % 20) -eq 0) { Write-Output "Rendered $done / $($tasks.Count) figures" }
        }
        finally {
            if ($null -ne $presentation) { $presentation.Close() }
        }
    }
}
finally {
    if ((-not $hadPresentations) -and ($ppt.Presentations.Count -eq 0)) { $ppt.Quit() }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)
}
