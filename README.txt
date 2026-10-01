SISTEMA DE ACIDENTES DO TRABALHO - HMA

1. Instale o Python 3 no computador.
2. Abra o terminal dentro desta pasta.
3. Execute:

   pip install -r requirements.txt

4. Depois execute:

   python app.py

5. Abra o navegador em:

   http://127.0.0.1:5000

Para acessar em outros computadores da mesma rede, execute o sistema no computador servidor e acesse pelo IP dele na porta 5000. Antes de uso real com dados pessoais, peça ao setor de TI para restringir o acesso somente à rede interna e definir backup do arquivo acidentes.db.

ARQUIVOS IMPORTANTES
- app.py: lógica do sistema
- acidentes.db: banco de dados (criado automaticamente)
- templates/: páginas HTML
- static/css/: aparência
- static/js/: gráficos do Dashboard

TELAS
- Dashboard
- Registrar acidente
- Consultar acidentes
- Detalhes / edição do registro
