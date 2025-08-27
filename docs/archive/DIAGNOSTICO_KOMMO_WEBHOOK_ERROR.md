# Diagnóstico Detalhado: Erro de JSON no Webhook do Kommo

## 1. Resumo do Problema

O endpoint do webhook que recebe eventos do Kommo CRM (`app/api/kommo_webhook.py`) está falhando com um erro `json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.

Isso indica que o endpoint está recebendo requisições com um corpo vazio ou em um formato que não é JSON, mas o código tenta forçar a leitura como JSON, causando uma exceção não tratada que impede o funcionamento do webhook.

## 2. Análise da Causa Raiz

A causa raiz é uma **regressão de código** introduzida durante a última modificação.

1.  **Lógica Frágil:** A versão atual do webhook assume que 100% das requisições `POST` do Kommo terão um `Content-Type` de `application/json` e um corpo de requisição válido.
2.  **Comportamento do Kommo:** É uma prática padrão para sistemas de webhook (incluindo o Kommo) enviar requisições de "ping" ou "teste" para validar que o endpoint está ativo. Essas requisições frequentemente têm um corpo vazio ou um `Content-Type` diferente.
3.  **Regressão:** A versão anterior do arquivo `kommo_webhook.py` continha uma lógica que verificava o `Content-Type` da requisição e tratava diferentes formatos (JSON, formulário, corpo vazio). Ao reescrever o arquivo para adicionar a funcionalidade de pausa do Redis, essa lógica de tratamento robusto foi removida acidentalmente, tornando o endpoint frágil.

**Conclusão:** O erro não é uma falha na lógica de negócio, mas sim na camada de entrada da API, que não é resiliente o suficiente para lidar com a variedade de requisições que um serviço de webhook como o Kommo pode enviar.

## 3. A Solução Inteligente: Reintroduzir a Robustez

A solução é reintroduzir e aprimorar a lógica de parsing da requisição, garantindo que ela possa lidar com diferentes cenários antes de tentar processar os dados.

### 3.1. Ação Proposta

Modificar a função `kommo_webhook` em `app/api/kommo_webhook.py`.

-   **Lógica:**
    1.  Antes de chamar `await request.json()`, verificar o header `Content-Type`.
    2.  Se for `application/json`, tentar fazer o parse do JSON. Se falhar, tratar o erro graciosamente.
    3.  Se for `application/x-www-form-urlencoded`, ler os dados do formulário.
    4.  Se o corpo estiver vazio ou o `Content-Type` for desconhecido, registrar um evento de "ping" ou "aviso" e encerrar o processamento sem erro, retornando um status `200 OK`.
    5.  Apenas se os dados forem parseados com sucesso, passá-los para a função de processamento em background (`process_lead_status_change`).

### 3.2. Vantagens da Solução

-   **Resiliência:** O endpoint se torna imune a pings de teste e requisições com corpo vazio, que são comuns e esperadas.
-   **Compatibilidade:** Garante a compatibilidade com diferentes formatos de dados que o Kommo possa enviar no futuro.
-   **Prevenção de Erros:** Evita que a aplicação registre erros desnecessários para requisições que são, na verdade, operacionais (como testes de conectividade).
-   **Código Correto:** Restaura a funcionalidade que nunca deveria ter sido removida, alinhando o código com as melhores práticas para a criação de webhooks.
