# Projeto Rifa - REST API

## Sumário
- [Como instalar](#como-rodar)

## Como rodar
Para executar o projeto você precisa ter o python instalado, garanta que esteja pelo menos 
na versão 3.10.

Verifique com:

```bash
python -V
# ou
python3 -V
```

1. Clone o repositório.

```bash
git clone git@github.com:medina325/projeto-rifa-backend.git <opcional-diretório>
```

2. Crie um ambiente virtual python:

```bash
python -m venv .venv
```

2.1. Se o venv não estiver instalado no sistema, instale com:

```bash
sudo apt install python3.10-venv
```

3. Ative o ambiente virtual com:

```
source .venv/bin/activate
```

Verifique o .venv está ativado executando:

```bash
which pip # A saída deve ser algo do tipo /home/.../.venv/bin/pip
```

4. Instale as dependências com:

```bash
pip install -r requirements.txt
```

5. Pronto! Rode a API com:

```bash
python main.py
```