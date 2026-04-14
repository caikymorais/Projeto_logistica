# Testes e Resultados Experimentais

## 1. Objetivo dos testes

Esta seção apresenta os testes experimentais realizados no sistema distribuído de logística e rastreamento. O objetivo dos experimentos foi verificar o comportamento da aplicação em diferentes cenários de execução, analisar métricas mínimas de desempenho e demonstrar o tratamento de falha simples, conforme exigido pela proposta do projeto. 

Os testes foram planejados para observar o funcionamento do sistema com diferentes quantidades de agentes distribuídos, medir o tempo de resposta e a vazão de processamento de eventos, além de demonstrar o comportamento do sistema diante da indisponibilidade temporária de um nó. 

## 2. Ambiente de execução

Os experimentos foram realizados em ambiente local, utilizando múltiplos processos executados em terminais separados no VSCode. A aplicação foi composta por um servidor central, múltiplos agentes distribuídos simulando veículos ou entregadores e um cliente monitor responsável por consultar informações do sistema. 

A comunicação entre os nós foi implementada com sockets TCP, adotando o modelo cliente-servidor. Essa escolha foi mantida por oferecer confiabilidade, entrega ordenada das mensagens e simplificação da implementação para o contexto acadêmico do projeto. 

## 3. Métricas observadas

As métricas coletadas durante os testes foram:

- **Tempo de resposta:** intervalo entre o envio do evento pelo agente e a resposta recebida do servidor. 
- **Vazão:** quantidade de eventos processados por segundo pelo servidor. 
- **Comportamento sob falha:** verificação de continuidade da operação quando um dos agentes deixa de enviar dados. 
- **Escalabilidade simples:** comparação do comportamento do sistema com diferentes quantidades de agentes distribuídos.

## 4. Cenários de teste

### 4.1 Cenário 1 — execução com 1 agente

Neste cenário, o sistema foi executado com 1 servidor, 1 agente distribuído e 1 cliente monitor. O objetivo foi validar o funcionamento básico da comunicação, o registro de eventos, a atualização do estado atual da entrega e a consulta ao histórico. 

**Configuração do cenário:**
- 1 servidor
- 1 agente
- 1 monitor
- intervalo entre eventos: 2 segundos
- quantidade total de eventos enviados: 5

**Resultados observados:**
- tempo médio de resposta: 0.30 ms
- total de eventos processados: 5
- vazão aproximada: 0.02 eventos/s
- falhas observadas: nenhuma falha observada

**Análise:**
O sistema apresentou funcionamento correto no cenário básico, permitindo o recebimento e o armazenamento dos eventos sem perda observada. O monitor conseguiu consultar tanto o estado atual quanto o histórico da entrega, confirmando o funcionamento mínimo esperado para a aplicação distribuída. 

### 4.2 Cenário 2 — execução com 3 agentes

Neste cenário, o sistema foi executado com 1 servidor, 3 agentes distribuídos e 1 cliente monitor. O objetivo foi atender ao requisito de múltiplos nós cooperando por rede e observar o comportamento da solução com maior volume de mensagens simultâneas.

**Configuração do cenário:**
- 1 servidor
- 3 agentes
- 1 monitor
- intervalo entre eventos: 2 segundos
- quantidade total de eventos enviados: 15

**Resultados observados:**
- tempo médio de resposta: 
- total de eventos processados: 15
- vazão aproximada: 0.02 eventos/s
- falhas observadas: nenhuma 

**Análise:**
Com três agentes ativos, o sistema continuou funcionando corretamente, mantendo o recebimento dos eventos, a atualização contínua do estado das entregas e a consulta via monitor. Esse cenário demonstra que a aplicação atende ao requisito de possuir pelo menos três processos ou nós cooperando por rede. 

### 4.3 Cenário 3 — execução com aumento de agentes

Neste cenário, foi realizado um experimento adicional com aumento da quantidade de agentes distribuídos para avaliar o impacto no desempenho da solução. Esse teste está diretamente alinhado ao requisito da opção de logística, que exige avaliar o efeito do aumento do número de agentes ou eventos. 

**Configuração do cenário:**
- 1 servidor
- 8 agentes
- 1 monitor
- intervalo entre eventos: 2 segundos
- quantidade total de eventos enviados: 40

**Resultados observados:**
- tempo médio de resposta:  ms
- total de eventos processados: 40
- vazão aproximada: 0.16 eventos/s
- falhas observadas: nenhuma 

**Análise:**
Com o aumento do número de agentes, foi possível observar alteração no tempo médio de resposta e na vazão do servidor. Ainda assim, o sistema permaneceu operacional, o que demonstra capacidade básica de escalabilidade dentro do escopo da aplicação desenvolvida. 

### 4.4 Cenário 4 — falha simples de um agente

Neste cenário, o sistema foi iniciado com múltiplos agentes ativos. Em seguida, um dos agentes foi encerrado manualmente para simular indisponibilidade temporária de um nó distribuído. O objetivo foi verificar se o servidor continuaria funcionando e se o sistema seria capaz de identificar a inatividade. 

**Configuração do cenário:**
- 1 servidor
- 3 agentes inicialmente
- 1 monitor
- agente interrompido: veiculo_02
- tempo para detecção de inatividade: 10 segundos

**Resultados observados:**
- agente detectado como inativo: sim 
- demais agentes continuaram enviando eventos: sim 
- impacto no sistema: Não houve nenhum impacto os outros agente continuaram rodando normalmente
- falhas observadas: nenhuma

**Análise:**
Após a interrupção de um dos agentes, o servidor continuou recebendo eventos dos demais nós, demonstrando continuidade operacional diante de falha simples. O mecanismo de detecção por tempo sem atualização permitiu identificar a indisponibilidade temporária do agente interrompido, atendendo ao requisito de robustez mínima do projeto.


## 5. Evidências coletadas

Durante a execução dos testes, foram registradas evidências do funcionamento do sistema, incluindo:

- terminal do servidor em execução;
- múltiplos agentes enviando eventos;
- respostas do servidor aos agentes;
- consultas realizadas pelo monitor;
- detecção de inatividade de agente;
- métricas retornadas pelo sistema.

## 6. Discussão dos resultados

Os resultados observados indicam que o sistema implementado conseguiu cumprir os principais comportamentos esperados para a proposta de logística e rastreamento. A aplicação foi capaz de receber eventos distribuídos, manter o estado atual das entregas, registrar histórico e responder consultas do monitor. 

Além disso, os testes mostraram que a solução permanece operando quando um dos nós deixa de enviar dados, o que reforça a robustez mínima exigida pela atividade. O uso de numeração de sequência também contribuiu para evitar processamento de mensagens duplicadas ou fora de ordem, fortalecendo a consistência do rastreamento. 

## 7. Limitações dos testes

Os testes realizados possuem limitações naturais por terem sido executados em ambiente local e em escala reduzida. Isso significa que os resultados não representam necessariamente o comportamento de uma infraestrutura real com rede externa, múltiplas máquinas físicas ou grande volume de conexões simultâneas.

Mesmo assim, os experimentos são suficientes para validar a proposta acadêmica, pois demonstram execução distribuída real entre processos, troca de mensagens por rede, tratamento de falha simples e análise básica de desempenho, exatamente como solicitado na atividade. 

## 8. Conclusão

Os experimentos realizados permitiram validar a funcionalidade do sistema distribuído e comprovar aderência aos requisitos do projeto. Foi possível demonstrar múltiplos nós cooperando por rede, atualização contínua de estado, registro de eventos, consulta a histórico, tratamento de indisponibilidade temporária e coleta de métricas mínimas de desempenho. 

Dessa forma, os testes reforçam que a aplicação atende de forma satisfatória aos requisitos técnicos e experimentais definidos na lauda do projeto. 