$rkey = "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox"

if(-Not (Test-Path -path $rkey)){
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Start-Process powershell -verb RunAs
        Write-Output "Firefox not found, installing..."
        $url = "https://download.mozilla.org/?product=firefox-stub&os=win&lang=en-US"
        $dest = "c:\temp\firefox.exe"
        if(-Not (Test-Path c:\temp)){
            New-Item -Path c:\temp -Type Directory
        }
        Invoke-WebRequest -Uri $url -OutFile $dest
        c:\temp\firefox.exe
        Remove-Item -Path $dest
    }
    else {
        Start-Process -FilePath "powershell" -ArgumentList "$('-File ""')$(Get-Location)$('\')$($MyInvocation.MyCommand.Name)$('""')" -Verb runAs
    }
}

$Folder = '.\clevercart_env'
if(Test-Path -Path $Folder){
    .\clevercart_env\Scripts\Activate.ps1
}
else{
    Write-Output "Virtual Environment not found, creating and installing dependencies..."
    python -m venv clevercart_env
    .\clevercart_env\Scripts\Activate.ps1
    python -m pip install flask flask-sqlalchemy flask-login user_agents gevent selenium openai
}

python main.py