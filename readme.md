# ⚡ Painel de Controle de Energia Inteligente

![Versão do Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-Flask-red.svg)
![Licença](https://img.shields.io/badge/License-MIT-yellow.svg)

Este projeto é um protótipo de um sistema de gerenciamento de energia inteligente, desenvolvido como prova de conceito para demonstrar a integração de simulação de componentes, automação e visualização de dados em tempo real.

---

## 🎯 Funcionalidades Principais

* **Dashboard Interativo:** Uma interface web em tempo real construída com Flask e Chart.js para monitorar todos os aspectos do sistema.
* **Simulação de Componentes:** Simula a geração de energia de um painel solar, o armazenamento e uso de uma bateria, o consumo de aparelhos domésticos e a utilização da rede elétrica externa.
* **Controle Remoto:** Permite ligar e desligar dispositivos simulados através de botões no painel, simulando a ação de um assistente virtual ou de um aplicativo de controle.
* **Automação Inteligente (Load Shedding):** Implementa uma lógica de priorização de consumo que desliga automaticamente aparelhos não essenciais quando o nível da bateria está criticamente baixo, garantindo a autonomia para cargas prioritárias.
* **Visualização de Dados e Alertas:** Exibe o fluxo de energia (geração, consumo, uso da rede) e o estado da bateria, além de mostrar alertas visuais em situações críticas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.11
* **Servidor Web:** Flask
* **Programação Concorrente:** Módulo `threading` do Python
* **Frontend:** HTML5, CSS3, JavaScript
* **Visualização de Dados:** Chart.js (carregado via CDN)
* **Versionamento:** Git e GitHub

---

## 🏛️ Arquitetura do Sistema

O diagrama abaixo ilustra a arquitetura geral da aplicação, mostrando como o frontend, o backend e a simulação contínua interagem.

```mermaid
graph TD
    subgraph "Usuário"
        A[👨‍💻 Usuário]
    end

    subgraph "Frontend (Navegador)"
        B[🌐 Dashboard - index.html]
    end

    subgraph "Backend (Servidor Python)"
        C[🐍 Servidor Flask - app.py]
        D[🔄 Thread de Simulação]
        E[(📊 Estado do Sistema<br>GerenciadorEnergia<br>Dispositivos, Bateria)]
    end

    A -- "Acessa e clica nos botões" --> B
    B -- "POST /comando/..." --> C
    B -- "GET /api/data (a cada 2s)" --> C
    
    C -- "Lê/Escreve dados" --> E
    D -- "Atualiza dados (a cada 1s)" --> E

---

## 📁 Estrutura do Projeto

```
/SPRINT2SERS/
├── .venv/                   # Ambiente virtual do Python
├── templates/
│   └── index.html           # Arquivo principal do dashboard web
├── app.py                   # Lógica principal, servidor Flask e simulação
├── modelos.py               # Definição das classes Bateria e DispositivoInteligente
├── .gitignore               # Arquivos e pastas a serem ignorados pelo Git
└── README.md                # Este arquivo
```

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para executar o projeto em um ambiente local.

### Pré-requisitos
* [Python 3.9+](https://www.python.org/downloads/) instalado
* [Git](https://git-scm.com/downloads/) instalado

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_AQUI]
    cd SPRINT2SERS
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Cria o ambiente
    python -m venv .venv

    # Ativa o ambiente (Windows)
    .venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    O arquivo `requirements.txt` contém todas as bibliotecas Python necessárias.
    ```bash
    pip install -r requirements.txt
    ```
    *(**Nota:** Se você não tem um `requirements.txt`, crie-o com o comando: `pip freeze > requirements.txt`)*


4.  **Execute a aplicação:**
    ```bash
    python app.py
    ```

5.  **Acesse o Dashboard:**
    * Abra seu navegador de internet e acesse o endereço:
        `http://127.0.0.1:5000`

---

##  license

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

**Desenvolvido por Rafael Vaz, André Eduardo Martins e Felipe Hui**