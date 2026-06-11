# fetch_corpus.ps1 - Récupère le corpus public data.gouv (Projet A)
# Usage : ./scripts/fetch_corpus.ps1 [-Profile open] [-Query "intelligence artificielle"] [-NItems 20]

param(
    [string]$Profile = "open",
    [string]$Query = "intelligence artificielle",
    [int]$NItems = 20
)

$OutDir = "corpus/raw"
New-Item -ItemType Directory -Force $OutDir | Out-Null

Write-Host "Récupération du corpus (profil=$Profile, query='$Query', n=$NItems)" -ForegroundColor Cyan

if ($Profile -eq "open") {
    $encoded = [System.Web.HttpUtility]::UrlEncode($Query)
    $url = "https://www.data.gouv.fr/api/1/datasets/?q=$encoded&page_size=$NItems&format=json"

    Write-Host "Appel API data.gouv : $url"
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        $datasets = $response.data

        $count = 0
        foreach ($ds in $datasets) {
            $title = $ds.title -replace '[^\w\s-]', '' -replace '\s+', '_'
            $outFile = "$OutDir\datagouv_$($ds.id).json"
            $ds | ConvertTo-Json -Depth 5 | Out-File -FilePath $outFile -Encoding utf8
            $count++
        }
        Write-Host "$count fichiers JSON sauvegardés dans $OutDir" -ForegroundColor Green
    }
    catch {
        Write-Host "Erreur lors de la récupération : $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Profil '$Profile' non supporté dans ce script (projet A = open uniquement)" -ForegroundColor Yellow
    exit 1
}

Write-Host "Corpus récupéré." -ForegroundColor Green
