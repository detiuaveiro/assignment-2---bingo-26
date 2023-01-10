# Projeto 2 - "Secure Game"

Neste projeto, os alunos foram incumbidos de implementar um protocolo robusto para um Bingo distribuído, ao nível das operações, e centralizado, ao nível das comunicações, atuando o *Caller* como servidor, os *Players* como clientes e a *PlayingArea* como intermediária.

[Consultar documentação/relatório aqui](Documentation.md)

## Instalação de dependências
```sh
sudo apt install pcscd
sudo apt install swig

python3 -m venv venv                # criação de um ambiente virtual (opcional)
source venv/bin/activate            # ativação do ambiente virtual (opcional)
pip install -r requirements.txt     # instalação dos módulos necessários
```

>**Nota**: Foi utilizado o módulo `python-dotenv`, para injetar as variáveis de ambiente do ficheiro [PROJECT_ROOT/.env](.env), nos scripts Python.

## Execução dos scripts 
Na *root* do projeto,
- **PlayingArea** -> `python3 playing_area.py`
- **Caller** -> `python3 caller.py -n caller`
- **Player** -> `python3 player.py -n player1`

A flag `-h` imprime no terminal os argumentos dos scripts.

<br>

## Créditos
| Nº mec. | Nome |
|--|--|
| 102534 | Rafael Gonçalves |
| 102536 | Leonardo Almeida |
| 102778 | Pedro Rodrigues |
| 103740 | Anzhelika Tosheva |