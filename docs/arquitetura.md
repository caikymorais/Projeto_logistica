# Arquitetura Distribuída do Sistema de Logística e Rastreamento

## 1. Visão geral

A aplicação implementa um sistema distribuído para rastreamento de entregas, baseado na **Opção 2: Sistema distribuído de logística e rastreamento** definida na lauda do projeto. 

O sistema é composto por múltiplos processos que cooperam por rede: um servidor central responsável por consolidar o estado das entregas, vários agentes distribuídos simulando veículos/entregadores e um cliente monitor para consulta de informações. 

## 2. Estilo arquitetural adotado

O estilo arquitetural escolhido é **cliente-servidor**, um dos modelos clássicos em sistemas distribuídos. 

- O **servidor central** atua como coordenador, recebendo e processando eventos.
- Os **agentes** funcionam como clientes produtores de eventos.
- O **monitor** funciona como cliente consumidor de consultas.

Essa escolha facilita o controle centralizado do estado e simplifica o protocolo de comunicação, o que é adequado para o escopo acadêmico do projeto.

## 3. Componentes principais

### 3.1. Servidor central (`server.py`)

Responsabilidades:

- Escutar conexões TCP de agentes e do monitor.
- Receber eventos de status enviados pelos agentes.
- Verificar a ordem e a duplicidade dos eventos por meio do campo de sequência (`seq`).
- Atualizar o estado atual das entregas.
- Registrar o histórico completo de eventos.
- Manter marcação do último contato de cada agente.
- Calcular métricas de desempenho (eventos, uptime, vazão, entregas ativas, agentes conhecidos).
- Responder consultas do monitor sobre estado atual, histórico, lista de entregas, agentes inativos e métricas.

### 3.2. Agentes distribuídos (`agent.py`)

Responsabilidades:

- Simular veículos/entregadores distribuídos.
- Enviar periodicamente eventos de status (coleta, em rota, atraso, entregue etc.).
- Anexar identificador do agente (`agent_id`) e da entrega (`delivery_id`) em cada mensagem.
- Utilizar um contador de sequência (`seq`) crescente para cada par agente/entrega, apoiando um mecanismo simples de consistência.
- Medir o tempo de resposta do servidor para cada evento enviado.

### 3.3. Cliente monitor (`monitor.py`)

Responsabilidades:

- Permitir interação com o sistema via menu em linha de comando.
- Enviar consultas ao servidor para:
  - obter estado atual de uma entrega específica;
  - obter histórico de eventos de uma entrega;
  - listar todas as entregas ativas;
  - listar agentes inativos, com base em timeout;
  - obter métricas gerais do sistema.

## 4. Diagrama de arquitetura (visão lógica)

Diagrama textual simplificado da interação entre os componentes:

```text
                 +----------------------+
                 |      Monitor         |
                 |    (monitor.py)      |
                 +----------+-----------+
                            |
                            |  TCP / JSON (consultas)
                            v
 +--------------------------+---------------------------+
 |                    Servidor Central                  |
 |                      (server.py)                     |
 |                                                      |
 |  - Escuta em porta TCP                               |
 |  - Recebe status_update dos agentes                  |
 |  - Mantém estado atual das entregas                  |
 |  - Armazena histórico de eventos                     |
 |  - Controla último contato de cada agente            |
 |  - Calcula métricas de desempenho                    |
 +----------+---------------------+---------------------+
            ^                     ^ 
            |                     |
            | TCP / JSON (eventos)| TCP / JSON (eventos)
            |                     |
   +--------+------+      +-------+--------+      ...
   |    Agente 1   |      |   Agente 2     |
   |  (agent.py)   |      |   (agent.py)   |
   +---------------+      +----------------+

```

Cada agente se conecta ao servidor usando sockets TCP, envia eventos de status para rastreamento e recebe confirmações. O monitor também se conecta ao servidor via TCP para realizar consultas. 

## 5. Protocolo de comunicação

### 5.1. Transporte

- **Protocolo de transporte:** TCP. 
- **Justificativa:**
  - entrega confiável das mensagens;
  - preservação da ordem dos dados;
  - simplificação da lógica de tratamento de erros para o contexto do trabalho, em comparação com o uso direto de UDP, que não garante entrega nem ordenação. 

### 5.2. Formato das mensagens

- Todas as mensagens trocadas entre agentes, servidor e monitor usam **JSON**.
- Cada mensagem JSON é enviada como uma linha separada, codificada em UTF-8.
- A delimitação é feita por `\n`, permitindo ao servidor reconstruir as mensagens a partir do stream recebido.

Exemplo de evento de status:

```json
{
  "type": "status_update",
  "agent_id": "veiculo_01",
  "delivery_id": "entrega_001",
  "seq": 10,
  "timestamp": "2026-04-13T22:30:00",
  "status": "em_rota",
  "latitude": -1.3617,
  "longitude": -48.2442
}
```

Exemplos de consultas do monitor:

- Estado atual:
  ```json
  { "type": "query_status", "delivery_id": "entrega_001", "timestamp": "..." }
  ```

- Histórico:
  ```json
  { "type": "query_history", "delivery_id": "entrega_001", "timestamp": "..." }
  ```

- Lista de entregas:
  ```json
  { "type": "list_deliveries", "timestamp": "..." }
  ```

- Agentes inativos:
  ```json
  { "type": "list_inactive_agents", "timestamp": "..." }
  ```

- Métricas:
  ```json
  { "type": "query_metrics", "timestamp": "..." }
  ```

## 6. Mecanismos distribuídos e requisitos da opção 2

A opção 2 da lauda define requisitos específicos para sistemas de logística e rastreamento. A arquitetura adotada atende a esses pontos da seguinte forma: 

1. **Múltiplos agentes distribuídos enviando eventos de localização/status**  
   - Atendido pelos múltiplos processos `agent.py` simultaneamente conectados ao servidor, cada um com seu próprio `agent_id` e `delivery_id`. 

2. **Atualização contínua do estado de entregas ou rotas**  
   - Atendida pela lógica do servidor que atualiza o estado atual da entrega a cada `status_update` recebido. 

3. **Registro de eventos relevantes (coleta, saída, atraso, falha, conclusão)**  
   - Cada evento inclui um campo `status` que pode assumir esses valores, e todos são registrados em histórico pelo servidor. 

4. **Mecanismo de consistência**  
   - Implementado por meio do campo `seq` e da verificação no servidor:
     - para cada par `(agent_id, delivery_id)` o servidor guarda o último `seq` aceito;
     - mensagens com `seq` menor ou igual ao último são ignoradas, evitando duplicidade ou regressão de estado. 

5. **Consultas ao estado atual e histórico de eventos**  
   - Implementadas por `monitor.py` usando mensagens `query_status`, `query_history` e `list_deliveries`, atendidas pelo servidor. 

6. **Estratégia para lidar com indisponibilidade temporária de algum nó**  
   - O servidor atualiza a cada evento o momento do último contato de cada agente.
   - Um timeout (por exemplo, 10 s) é utilizado para considerar um agente como inativo se ficar muito tempo sem enviar dados.
   - Essa informação é acessível via `list_inactive_agents`. 

7. **Avaliação do impacto do aumento de agentes/eventos no desempenho**  
   - A arquitetura permite executar cenários com diferentes números de agentes conectados simultaneamente e medir métricas de vazão e tempo de resposta, conforme documentado na seção de testes. 

## 7. Considerações finais sobre a arquitetura

A arquitetura cliente-servidor com servidor centralizado simplifica o controle do estado global das entregas e facilita o desenvolvimento de testes para avaliação de desempenho e robustez. 

Dentro do escopo acadêmico proposto, a solução equilibra simplicidade de implementação e cobertura dos conceitos da disciplina: comunicação via sockets, estrutura distribuída real, mecanismo de consistência, tratamento de falha simples e coleta de métricas de desempenho. 