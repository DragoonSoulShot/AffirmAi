# Update all Chocolatey packages
choco upgrade all -y

# Update any other specific tools or drivers
winget upgrade --all --accept-source-agreements --accept-package-agreements
