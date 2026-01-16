# ??? NeuralGuard AI - Estação de Comando

**Versão Atual:** v8.8 (Enterprise Edition)  
**Status:** Estável / Captura & Persistência Ativa

## ?? Propósito do Projeto
O **NeuralGuard AI** é um sistema avançado de monitoramento e segurança patrimonial que utiliza Visão Computacional de ponta e Inteligência Artificial Generativa (Google Gemini) para identificar e analisar rostos em tempo real a partir de streams de vídeo RTSP.

Diferente de sistemas de segurança comuns, o NeuralGuard não apenas detecta movimento, mas "entende" quem está diante da câmera, avaliando níveis de risco e características físicas para auxiliar na tomada de decisão de segurança.

---

## ??? Arquitetura do Sistema

O projeto é dividido em três pilares fundamentais:
1.  **Frontend (Dashboard):** Interface em React de alta performance que processa os frames, renderiza a UI de detecção e comunica-se com a API do Gemini.
2.  **Bridge (Ponte Python):** Um servidor Flask rodando em ambiente local (Ubuntu/GLPI) que utiliza OpenCV para ler streams RTSP de câmeras IP e expor esses dados via HTTP/MJPEG.
3.  **Tunneling (Cloudflare):** Camada de rede que permite o acesso remoto seguro e resolve conflitos de segurança de navegador (CORS/Mixed Content).

---

## ?? Jornada de Desenvolvimento & Superações

### 1. O Desafio da Conectividade (HTTP vs HTTPS)
**Problema:** Ao rodar o Dashboard em um ambiente moderno, o navegador bloqueava o acesso direto ao IP local da câmera (HTTP) por motivos de segurança (Mixed Content).  
**Superação:** Implementamos o **Cloudflare Tunnel**. Isso nos deu um endereço HTTPS válido e seguro, permitindo que o Dashboard e a Bridge conversassem sem restrições de segurança do navegador.

### 2. A Barreira do Stream RTSP
**Problema:** Muitas câmeras IP bloqueiam o stream principal (Subtype 0) se ele já estiver sendo usado por um NVR ou outro software.  
**Superação:** Desenvolvemos na **v8.7** um motor de **Auto-Scan**. A Bridge agora tenta automaticamente diferentes subtipos de canal até encontrar um sinal disponível, garantindo compatibilidade com Intelbras, Hikvision e outras marcas.

### 3. Persistência e Feedback Visual
**Problema:** Identificar um rosto na tela era fácil, mas salvar essa evidência no disco do servidor e confirmar o salvamento para o operador era complexo.  
**Superação:** Na **v8.8**, criamos um sistema de persistência ativa. Agora, cada rosto detectado é enviado via Base64 para a Bridge, gravado na pasta `/Fotos` e o Dashboard exibe um ícone de **DISCO** azul em tempo real, confirmando que a prova foi salva.

---

## ?? Onde Estamos no Momento?

-   ? **Bridge v8.8 Estável:** Servidor Python robusto com multi-threading.
-   ? **Captura Inteligente:** Detecção facial nativa do navegador integrada ao Gemini 3 Flash.
-   ? **Análise de Risco:** IA categoriza indivíduos entre Baixo, Médio e Alto Risco.
-   ? **Gravação Local:** Todos os rostos identificados são armazenados fisicamente no servidor GLPI.
-   ? **Túnel de Dados:** Acesso via URL externa sem necessidade de abrir portas no roteador.

---

## ??? Como Executar

### Pré-requisitos
- Python 3.10+
- Bibliotecas: `opencv-python`, `flask`, `flask-cors`
- Cloudflared instalado

### Comandos Rápidos
1.  **Inicie a Bridge:**
    ```bash
    python3 bridge.py
    ```
2.  **Inicie o Túnel:**
    ```bash
    cloudflared tunnel --url http://localhost:5050
    ```
3.  **Configuração:**
    Copie a URL `.trycloudflare.com` gerada e cole no menu **SET** do Dashboard.

---

## ????? Desenvolvedor
Projeto em constante evolução. Foco atual: *Refinamento do Reconhecimento Facial e Sincronização em Nuvem.*
