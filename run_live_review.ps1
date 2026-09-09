$ErrorActionPreference = "Stop"

Write-Host "Synthetic AEB V&V — OpenAI LLM Reviewer"
Write-Host "The API key will be held only in this PowerShell process and will not be written to the repo."

$secure = Read-Host "Paste OPENAI_API_KEY" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)

try {
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)

    if ([string]::IsNullOrWhiteSpace($plainKey) -or -not $plainKey.StartsWith("sk-")) {
        throw "The value entered does not look like an OpenAI API key. Paste the actual key beginning with 'sk-' at the key prompt, not the PowerShell command."
    }

    $env:OPENAI_API_KEY = $plainKey

    Write-Host ""
    Write-Host "[1/2] Running live LLM review..."
    python scripts/llm_review_openai.py --model gpt-5.6-luna
    if ($LASTEXITCODE -ne 0) { throw "LLM review failed." }

    Write-Host ""
    Write-Host "[2/2] Evaluating against fixed ground truth..."
    python scripts/evaluate_llm_review.py
    if ($LASTEXITCODE -ne 0) { throw "Evaluation failed." }

    Write-Host ""
    Write-Host "Done."
    Write-Host "Review: findings/llm_review_openai.json"
    Write-Host "Metrics: evidence/llm_evaluation_v0.4.json"
}
finally {
    Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
    $plainKey = $null
    if ($bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}
