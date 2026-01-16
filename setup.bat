@echo off
REM Criar ambiente virtual
python -m venv venv

REM Ativar ambiente virtual
call venv\Scripts\activate

REM Atualizar pip e instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

REM Criar pasta Fotos
mkdir Fotos

echo Ambiente pronto! Para ativar novamente use: call venv\Scripts\activate
