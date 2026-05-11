# Projeto: Sistema de Oficina Mecânica Distribuído
**Integrantes:** Gabriel R. Ikegami, Gustavo S. de Flores, Matheus F. Merlos

Este projeto foi desenvolvido para a disciplina de **Sistemas Operacionais**. Consiste em um ambiente de microsserviços simulado utilizando **Docker**, **Docker Compose** e **Python**.

## Tecnologias Utilizadas
* **Linguagem:** Python (FastAPI)
* **Containers:** Docker
* **Orquestração:** Docker Compose
* **Bancos de Dados:** PostgreSQL e MongoDB
* **Comunicação:** Requisições HTTP via Rede Docker

## Arquitetura do Sistema
O ambiente é composto por **5 containers**:
1. **api-clientes**: Gerencia dados de clientes e veículos, utilizando **PostgreSQL** para armazenamento relacional.
2. **api-produtos**: Gerencia o estoque de peças da oficina, utilizando **MongoDB** para armazenamento NoSQL.
3. **api-pedidos**: Atua como o orquestrador do sistema, consumindo dados das outras APIs para gerar ordens de serviço.
4. **postgres-db**: Container do banco de dados relacional.
5. **mongo-db**: Container do banco de dados não-relacional.

## Funcionamento do Sistema
O sistema opera de forma distribuída, simulando um ambiente real de microsserviços:

* **Isolamento de Dados**: Cada serviço possui sua própria base de dados, garantindo que a falha de um banco não derrube o sistema inteiro. Os dados são persistidos através de **Volumes Docker**, garantindo a persistência mesmo após o encerramento dos containers.
* **Comunicação Inter-Processos**: Quando um "Pedido" é gerado, a `api-pedidos` realiza chamadas HTTP internas para a `api-clientes` (validar proprietário) e para a `api-produtos` (verificar peça).
* **Resiliência**: A `api-clientes` implementa uma lógica de *retry* na inicialização, aguardando o banco de dados estar pronto antes de aceitar conexões, resolvendo condições de corrida comuns em sistemas distribuídos.
* **Descoberta de Serviço**: A comunicação utiliza os **nomes dos serviços** definidos no Docker Compose em vez de IPs fixos, aproveitando o DNS interno do Docker.

## Como Executar
1. Certifique-se de ter o Docker e Docker Compose instalados.
2. Na raiz do projeto, execute o comando:
   ```bash
   docker-compose up --build

## Como Testar
Com os containers rodando, você pode testar as funcionalidades através das interfaces Swagger:

Cadastrar Cliente: Acesse http://localhost:8001/docs, utilize o POST /clientes e insira os dados do cliente e veículo.

Cadastrar Produto: Acesse http://localhost:8002/docs, utilize o POST /produtos e insira uma peça (ex: "Amortecedor").

Verificar Integração: Acesse http://localhost:8003/resumo-oficina. Esta página exibirá um JSON com o resumo de clientes e produtos, provando que a comunicação entre containers via rede Docker está funcionando.

