# Path to the temporary files directory
$tempPath = "C:\Users\ryanl\affirmAI\temp"

# Path to the log file
$logPath = "C:\Users\ryanl\affirmAI\logs\maintenance.log"

# Get a list of all files older than 7 days
$files = Get-ChildItem $tempPath -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }

# Delete the old files and write to the log
foreach ($file in $files) {
    Write-Host "Deleting file: $($file.FullName)"
    Remove-Item $file.FullName -Force

    # Log the deletion
    $logEntry = "{0} - Deleted: {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $file.FullName
    Add-Content $logPath $logEntry
}

Write-Host "Clean up completed."
