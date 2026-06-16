# 📊 Smart ETL Logger

Um módulo Python reutilizável que combina o poder do **Loguru** para geração de logs com alertas automatizados por e-mail e **Inteligência Artificial (Google Gemini)** para análise e diagnóstico de erros.

Ideal para ser importado em pipelines de Dados (ETL) e scripts de automação, enviando um relatório HTML dinâmico com o status da execução direto para a sua equipe.

## ✨ Recursos

* 📝 **Gerenciamento de Logs Limpo:** Usa o Loguru para salvar logs organizados localmente.
* 📧 **Notificações Inteligentes:** Envia o arquivo de log anexado por e-mail com um dashboard em HTML.
* 🚦 **Status Visual:** O e-mail fica verde (Sucesso), laranja (Avisos) ou vermelho (Erros) automaticamente.
* 🤖 **Diagnóstico via IA:** Se houver erros críticos, a API do Gemini entra em ação, lê as falhas e envia no e-mail um resumo do problema e uma sugestão de correção.
* 🔒 **Seguro:** Construído para usar variáveis de ambiente (`.env`), mantendo suas senhas seguras fora do código-fonte.

---

## 🚀 Instalação e Configuração

### 1. Requisitos
Certifique-se de instalar as dependências necessárias no projeto onde você for utilizar esta classe:

```bash
pip install loguru python-dotenv google-generativeai