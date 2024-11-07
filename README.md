# ✈️ Sistema de API para Aeroporto

Este projeto é uma API desenvolvida para gerenciamento de operações de um sistema de aeroportos, permitindo que usuários realizem reservas de voos, gerenciem sessões, consultem informações sobre aeroportos e voos, entre outros recursos. A API foi construída com **Python** utilizando o framework **FastAPI** e integra-se a um banco de dados relacional **PostgreSQL**.

## 🗂️ Estrutura de Dados

O sistema contém cinco tabelas principais:

1. **Aeroportos** 🛫:
   - Campos: `id`, `nome`, `cidade`, `estado`, `pais`, `endereco`, `cep`, `codigo_iata`, `companhias`
   - Armazena informações sobre cada aeroporto, incluindo a lista de companhias parceiras.

2. **Reservas** 🧳:
   - Campos: `id`, `id_usuario`, `id_voo`, `quantidade_passageiros`, `tarifa_total`, `data_reserva`, `status`, `e_tickets`
   - Contém os detalhes das reservas feitas pelos usuários.

3. **Sessões** 🔐:
   - Campos: `id`, `id_usuario`, `chave_sessao`, `data_criacao`, `data_expiracao`, `ip_acesso`
   - Gerencia as sessões de usuários para garantir a segurança e autenticação.

4. **Usuários** 👤:
   - Campos: `id`, `nome`, `email`, `senha`, `cpf`, `tipo_usuario`
   - Registra os dados dos usuários do sistema, incluindo as credenciais de login.

5. **Voos** 🛩️:
   - Campos: `id`, `id_aeroporto_org`, `id_aeroporto_dest`, `numero_voo`, `tarifa_por_passageiro`, `data_partida`, `data_chegada`, `vagas`, `status`
   - Armazena informações detalhadas dos voos disponíveis.

## 🚀 Endpoints Disponíveis

### 🔎 Endpoints de Funcionalidades

- **`/aeroportos/companhias/{companhia}`**: Retorna uma lista de aeroportos que possuem parceria com uma determinada companhia aérea.
- **`/voos/reserva`**: Realiza a compra/reserva de um voo. (Necessita de sessão ativa - usuário logado).
- **`/sessao/validar/{id}`**: Valida uma sessão com base no `id` da sessão, verificando se `data_expiracao` é posterior à data atual.
- **`/login`**: Realiza o login de um usuário.
- **`/logout`**: Realiza o logout de um usuário.
- **`/aeroportos/destinos/{aeroporto_origem_nome}`**: Dado o nome de um aeroporto de origem, retorna uma lista de aeroportos de destino partindo do aeroporto informado.
- **`/voos/companhia/data_partida`**: Retorna uma lista de voos de uma determinada companhia aérea com base na data de partida informada.
- **`/voos/tarifa_minima/{num_passageiros}`**: Lista voos com a menor tarifa para uma determinada quantidade de passageiros.

### 🔧 Endpoints de CRUD

Cada tabela possui seus endpoints de CRUD para facilitar a manipulação dos dados:

- **Aeroportos**:
  - `/aeroportos`: Retorna todos os aeroportos (GET).
  - `/aeroporto`: Adiciona um novo aeroporto (POST).
  - `/aeroporto/{id}`: Atualiza um aeroporto específico (PUT).
  - `/aeroporto/{id}`: Exclui um aeroporto específico (DELETE).

- **Reservas**:
  - `/reservas`: Retorna todas as reservas (GET).
  - `/reserva`: Adiciona uma nova reserva (POST).
  - `/reserva/{id}`: Atualiza uma reserva específica (PUT).
  - `/reserva/{id}`: Exclui uma reserva específica (DELETE).

- **Sessões**:
  - `/sessoes`: Retorna todas as sessões (GET).
  - `/sessao`: Cria uma nova sessão (POST).
  - `/sessao/{id}`: Atualiza uma sessão específica (PUT).
  - `/sessao/{id}`: Exclui uma sessão específica (DELETE).

- **Usuários**:
  - `/usuarios`: Retorna todos os usuários (GET).
  - `/usuario`: Adiciona um novo usuário (POST).
  - `/usuario/{id}`: Atualiza um usuário específico (PUT).
  - `/usuario/{id}`: Exclui um usuário específico (DELETE).

- **Voos**:
  - `/voos`: Retorna todos os voos (GET).
  - `/voo`: Adiciona um novo voo (POST).
  - `/voo/{id}`: Atualiza um voo específico (PUT).
  - `/voo/{id}`: Exclui um voo específico (DELETE).

## 💻 Tecnologias Utilizadas

- **FastAPI**: Framework para desenvolvimento de APIs rápidas e seguras em Python.
- **PostgreSQL**: Banco de dados relacional para armazenamento persistente.
- **Docker**: Utilizado para containerizar a aplicação e o banco de dados.

## 🐳 Estrutura de Containers

O sistema é executado em dois containers Docker, configurados para comunicação por meio de uma rede do tipo `bridge`:
- Um container para a aplicação FastAPI.
- Um container para o banco de dados PostgreSQL.

## ⚙️ Como Executar

Para executar o projeto, é necessário ter o **Docker** e o **Docker Compose** instalados. No diretório raiz do projeto (onde se encontra o arquivo `docker-compose.yaml`), execute o seguinte comando:

```bash
docker-compose up
