#!/bin/bash
# Script: auto_commit.sh
# Uso: ./auto_commit.sh "mensagem do commit"

# Caminho do projeto
PROJECT_DIR="/opt/Porteiro"

# Vai até o diretório do projeto
cd $PROJECT_DIR || exit

# Adiciona todas as alterações
git add .

# Cria commit com a mensagem passada como argumento
if [ -z "$1" ]; then
  COMMIT_MSG="Atualização automática"
else
  COMMIT_MSG="$1"
fi

git commit -m "$COMMIT_MSG"

# Faz push para o branch main
git push origin main
