param(
    [string]$RepoName = 'jarvis-ai',
    [string]$Owner = 'beeniko33-dotcom',
    [string]$Description = 'Jarvis AI backend bridge with resilient fallback agent and frontend test page.',
    [string]$Token = $env:GITHUB_TOKEN
)

if (-not $Token) {
    Write-Error 'Set the GITHUB_TOKEN environment variable with a Personal Access Token that has repo scope.'
    exit 1
}

$headers = @{ 
    Authorization = "token $Token"
    Accept = 'application/vnd.github+json'
    'User-Agent' = 'github-api-script'
}

$payload = @{
    name = $RepoName
    description = $Description
    private = $false
} | ConvertTo-Json

try {
    $url = 'https://api.github.com/user/repos'
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $payload -ContentType 'application/json'
    Write-Output "Created repository: $($response.full_name)"
} catch {
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode.Value__ -eq 422) {
        Write-Output 'Repository already exists or a name conflict occurred. Proceeding to set remote and push if possible.'
    } else {
        Write-Error "GitHub repo creation failed: $($_.Exception.Message)"
        exit 1
    }
}

$remoteUrl = "https://github.com/$Owner/$RepoName.git"
Write-Output "Setting remote origin to $remoteUrl"
git remote remove origin 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Output 'Removed existing remote if present.' }
git remote add origin $remoteUrl

Write-Output 'Pushing current branch to origin...'
git push origin HEAD
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Push failed. Check your authentication and remote settings.'
    exit 1
}

Write-Output 'Push complete.'
