# Sistema Distribuído de Logística e Rastreamento

Este projeto implementa um sistema distribuído simples para rastreamento de entregas, desenvolvido como trabalho da disciplina de Programação Distribuída e Paralela (Ciência da Computação). O sistema simula múltiplos agentes (veículos/entregadores) enviando eventos de status para um servidor central, enquanto um cliente monitor permite consultar o estado atual e o histórico das entregas. 

A solução adota arquitetura cliente-servidor, comunicação via sockets TCP e inclui mecanismos básicos de consistência, tolerância a falha simples e coleta de métricas de desempenho. 

---

## 1. Objetivos do projeto

- Resolver um problema de aplicabilidade real na área de logística e rastreamento de entregas. 
- Implementar execução distribuída com múltiplos processos cooperando por rede.
- Utilizar sockets TCP para comunicação entre nós, justificando a escolha do protocolo. 
- Incluir mecanismos típicos de sistemas distribuídos (consistência simples e tolerância a falha).
- Realizar testes experimentais em diferentes cenários com métricas de tempo de resposta, vazão e comportamento sob falha simples. 

---

## 2. Arquitetura distribuída

A arquitetura adotada é do tipo **cliente-servidor**, composta por três tipos de nós: 

- **Servidor central (`server.py`)**
  - Recebe eventos de status dos agentes via sockets TCP.
  - Mantém o estado atual de cada entrega e o histórico de eventos.
  - Calcula métricas simples (total de eventos, uptime, vazão, entregas ativas, agentes conhecidos).
  - Atende requisições do monitor (estado atual, histórico, lista de entregas, agentes inativos, métricas).

- **Agentes de entrega (`agent.py`)**
  - Representam veículos ou entregadores distribuídos.
  - Enviam periodicamente eventos de localização/status para o servidor.
  - Utilizam numeração de sequência (`seq`) crescente em cada evento para apoiar um mecanismo simples de consistência. 
  - Medem o tempo de resposta do servidor por evento.

- **Cliente monitor (`monitor.py`)**
  - Permite consultar, via linha de comando:
    - estado atual de uma entrega específica;
    - histórico de eventos de uma entrega;
    - lista de entregas ativas;
    - lista de agentes inativos (detecção por timeout);
    - métricas gerais do sistema.

---

## 3. Tecnologias utilizadas

- **Linguagem:** Python 
- **Comunicação:** sockets TCP (`socket`, `bind`, `listen`, `accept`, `connect`, `send`, `recv`). 
- **Formato de mensagens:** JSON (codificado em UTF-8, delimitação por linha).
- **Arquivos principais:**
  - `server.py` — servidor central.
  - `agent.py` — simulador de agente/veículo.
  - `monitor.py` — cliente de monitoramento.
  - `protocol.py` — funções de montagem/codificação/decodificação de mensagens.
  - `storage.py` — armazenamento em memória de estado, histórico, seq, timestamps e métricas.

A escolha de TCP foi feita porque o projeto exige comunicação confiável e ordenada, simplificando o tratamento de eventos de rastreamento em comparação com UDP, que não garante entrega nem ordenação. 

---

## 4. Estrutura do repositório

Exemplo de organização sugerida:

```bash
projeto-distribuido-logistica/
├── server.py
├── agent.py
├── monitor.py
├── protocol.py
├── storage.py
├── README.md
└── docs/
    ├── relatorio.md
    ├── arquitetura.md
    └── testes.md
```

---

## 5. Como executar o sistema

### 5.1. Pré-requisitos

- Python 3 instalado.
- Repositório clonado em uma pasta local.

### 5.2. Iniciar o servidor

Em um terminal:

```bash
python server.py
```

O servidor ficará escutando conexões na porta configurada (por padrão, `127.0.0.1:5000`).

### 5.3. Iniciar agentes

Abra um terminal para cada agente que desejar rodar.

Exemplo com 3 agentes (cada um em um terminal separado):

```bash
python agent.py veiculo_01 entrega_001 2
python agent.py veiculo_02 entrega_002 2
python agent.py veiculo_03 entrega_003 2
```

Parâmetros:
- `veiculo_XX`: identificador do agente.
- `entrega_XXX`: identificador da entrega.
- `2`: intervalo em segundos entre envios de eventos.

### 5.4. Iniciar o monitor

Em outro terminal:

```bash
python monitor.py
```

O monitor apresenta um menu interativo com as seguintes opções:

1. Consultar estado atual de uma entrega  
2. Consultar histórico de uma entrega  
3. Listar entregas  
4. Listar agentes inativos  
5. Ver métricas  
0. Sair  

---

## 6. Protocolo de mensagens

As mensagens entre agentes, servidor e monitor são trocadas em JSON, uma por linha, usando UTF-8. Alguns exemplos:

### 6.1. Evento de status enviado por um agente

```json
{
  "type": "status_update",
  "agent_id": "veiculo_01",
  "delivery_id": "entrega_001",
  "seq": 15,
  "timestamp": "2026-04-13T22:30:00",
  "status": "em_rota",
  "latitude": -1.3617,
  "longitude": -48.2442
}
```

O servidor usa o par `(agent_id, delivery_id, seq)` para aplicar um mecanismo simples de consistência, ignorando mensagens duplicadas ou fora de ordem. 

### 6.2. Consultas do monitor

Exemplos de requisições:

- Consulta de estado atual:
  ```json
  { "type": "query_status", "delivery_id": "entrega_001", "timestamp": "..." }
  ```

- Consulta de histórico:
  ```json
  { "type": "query_history", "delivery_id": "entrega_001", "timestamp": "..." }
  ```

- Lista de entregas:
  ```json
  { "type": "list_deliveries", "timestamp": "..." }
  ```

- Lista de agentes inativos:
  ```json
  { "type": "list_inactive_agents", "timestamp": "..." }
  ```

- Métricas:
  ```json
  { "type": "query_metrics", "timestamp": "..." }
  ```

---

## 7. Mecanismos distribuídos implementados

### 7.1. Consistência simples por sequência

Cada agente envia eventos com um campo `seq` inteiro crescente. O servidor mantém o último `seq` visto para cada par `(agent_id, delivery_id)` e ignora mensagens com `seq` antigo ou repetido. Isso reduz a chance de conflitos ou processamento duplicado caso alguma mensagem seja reenviada. 

### 7.2. Tolerância a falha simples (indisponibilidade de agente)

O servidor registra o último instante em que recebeu evento de cada agente. A partir de um timeout configurado (por exemplo, 10 s), um agente passa a ser considerado inativo se ficar tempo demais sem enviar mensagens. Essa informação é exposta ao monitor na consulta de agentes inativos. 

Quando um agente “cai” (terminal fechado), os demais agentes continuam enviando normalmente, e o servidor segue operando, demonstrando tolerância a falha simples de nó. 

### 7.3. Métricas de desempenho

O servidor calcula:

- `total_events`: número de eventos recebidos desde o início da execução.
- `uptime_seconds`: tempo de atividade do servidor em segundos.
- `throughput_events_per_sec`: vazão média em eventos por segundo.
- `active_deliveries`: quantidade de entregas com estado atual armazenado.
- `known_agents`: número de agentes diferentes que já se conectaram. 

Essas métricas são usadas no relatório de testes para análise experimental.

---

## 8. Como reproduzir os cenários de teste

A lauda exige testes em diferentes cenários e análise do impacto do aumento de agentes/eventos no desempenho. 
A seguir, exemplos de como reproduzir os cenários descritos em `docs/testes.md`.

### Cenário 1 — 1 agente

- 1 servidor (`server.py`)
- 1 agente (`agent.py veiculo_01 entrega_001 2`)
- 1 monitor (`monitor.py`)

Use o monitor para:
- consultar estado atual;
- consultar histórico;
- ver métricas (tempo de resposta e vazão).

### Cenário 2 — 3 agentes

- 1 servidor
- 3 agentes:
  ```bash
  python agent.py veiculo_01 entrega_001 2
  python agent.py veiculo_02 entrega_002 2
  python agent.py veiculo_03 entrega_003 2
  ```
- 1 monitor

Compare a vazão e o comportamento com o cenário 1. 

### Cenário 3 — mais agentes

- 1 servidor
- 5 ou mais agentes (por exemplo, 8):
  ```bash
  python agent.py veiculo_01 entrega_001 2
  ...
  python agent.py veiculo_08 entrega_008 2
  ```
- 1 monitor

Coleta métricas de vazão e tempo de resposta e compare com cenários anteriores. 

### Cenário 4 — falha simples de um agente

- Inicie o servidor, 3 agentes e o monitor.
- Depois de alguns segundos, feche o terminal de um dos agentes (simulando falha).
- Aguarde o tempo de timeout (por exemplo, 10 segundos).
- No monitor, use a opção de listar agentes inativos e ver métricas. 

---

## 9. Limitações e trabalhos futuros

- A solução atual mantém os dados em memória; não há persistência em banco de dados.
- O sistema foi testado em ambiente local, com processos na mesma máquina, não em múltiplas máquinas físicas.
- Não há interface gráfica ou web; a interação é via linha de comando.

Possíveis melhorias futuras:

- Persistência em banco de dados (por exemplo, SQLite).
- Interface web para monitoramento em tempo real.
- Uso de múltiplas máquinas físicas para simular um ambiente distribuído mais realista.
- Mecanismos mais avançados de tolerância a falhas e replicação. 

---

## 10. Autores

- Nomes: Caiky Alves e Maria Eduarda

