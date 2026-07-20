# JavaLog Agent

Agente de diagnóstico para logs Java e Spring Boot, implementado com Python, LangGraph, LangChain e saída estruturada com Pydantic.

O fluxo valida o arquivo, lê o log por uma ferramenta restrita, extrai eventos e exceções, classifica o problema, produz um diagnóstico e grava um relatório Markdown.

## Funcionalidades

- validação determinística do arquivo de entrada;
- leitura restrita ao diretório `examples/logs`;
- suporte a arquivos `.log` e `.txt`;
- limite máximo de 5 MB por arquivo;
- extração de exceções Java e eventos `ERROR` e `WARN`;
- classificação determinística do log;
- diagnóstico estruturado com LLM;
- fallback determinístico quando o LLM falha ou não está configurado;
- validação da saída com Pydantic;
- escrita restrita ao diretório `output`;
- testes com FakeLLM, sem chamadas externas.

## Arquitetura

Fluxo principal:

    START
      |
      v
    validar_entrada
      |
      +-- inválida --> gerar_resposta_erro --> END
      |
      v
    ler_log
      |
      +-- erro --> gerar_resposta_erro --> END
      |
      v
    extrair_eventos
      |
      v
    classificar_log
      |
      +-- Clean --> gerar_resultado_sem_erros
      |
      +-- erro --> diagnosticar
                      |
                      v
                  validar_saida
                      |
                      +-- inválida --> tratar_saida_invalida
                      |
                      v
               escrever_relatorio
                      |
                     END

O LLM é injetado no grafo por `create_graph(llm=...)`. Sem uma instância injetada, o nó cria `ChatOpenAI` em tempo de execução.

## Estrutura

    java-log-agent/
    ├── docs/
    │   └── prompts/
    ├── examples/
    │   ├── logs/
    │   └── results/
    ├── output/
    ├── src/
    │   ├── graph.py
    │   ├── main.py
    │   ├── nodes.py
    │   ├── schemas.py
    │   ├── state.py
    │   ├── tools.py
    │   └── validation.py
    ├── tests/
    │   ├── fake_llm.py
    │   ├── test_routing.py
    │   ├── test_tools.py
    │   └── test_validation.py
    ├── .env.example
    ├── .gitignore
    └── requirements.txt

## Requisitos

- Python 3.12;
- dependências listadas em `requirements.txt`;
- chave da OpenAI opcional.

## Instalação no PowerShell

~~~powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
~~~

Para usar o diagnóstico com OpenAI:

~~~powershell
Copy-Item .env.example .env
~~~

Depois, informe a chave no arquivo `.env`:

~~~text
OPENAI_API_KEY=sua_chave
~~~

Sem a chave, logs com erros seguem para o fallback determinístico.

## Execução

Log com exceção:

~~~powershell
.\.venv\Scripts\python.exe -m src.main `
    examples\logs\null-pointer-exception.log
~~~

Log com erro de criação de bean:

~~~powershell
.\.venv\Scripts\python.exe -m src.main `
    examples\logs\bean-creation-error.log
~~~

Log sem erros relevantes:

~~~powershell
.\.venv\Scripts\python.exe -m src.main `
    examples\logs\application-clean.log
~~~

Os relatórios são gravados em `output`.

## Exemplos versionados

Entradas:

- `examples/logs/application-clean.log`;
- `examples/logs/bean-creation-error.log`;
- `examples/logs/null-pointer-exception.log`.

Saídas correspondentes:

- `examples/results/report_application-clean.md`;
- `examples/results/report_bean-creation-error.md`;
- `examples/results/report_null-pointer-exception.md`.

Os relatórios em `examples/results` demonstram a execução sem uma chave real da OpenAI. Por isso, os logs com erros usam o modo `fallback`, enquanto o log limpo usa o modo `deterministic`.

## Testes

Executar a suíte completa:

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
~~~

Resultado validado:

~~~text
26 passed
~~~

Cobertura funcional da suíte:

- 7 testes de roteamento do StateGraph;
- 11 testes das ferramentas;
- 8 testes de validação de entrada.

## Segurança e limites

- arquivos de entrada devem estar em `examples/logs`;
- somente extensões `.log` e `.txt` são aceitas;
- arquivos vazios, inexistentes ou acima de 5 MB são rejeitados;
- path traversal é bloqueado antes da leitura;
- relatórios são gravados somente em `output`;
- nomes de relatório são sanitizados;
- o modelo não recebe acesso a shell ou escrita irrestrita;
- a FakeLLM é injetada somente pelos testes;
- falhas do LLM são convertidas em estado observável;
- o fallback permite concluir o diagnóstico sem chamada externa.

## Estados finais principais

| Status | Significado |
|---|---|
| `success` | Diagnóstico válido produzido pelo LLM |
| `success_fallback` | Diagnóstico determinístico após falha ou ausência do LLM |
| `success_no_errors` | Log sem erros relevantes |
| `error` | Entrada inválida ou falha de leitura |
