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