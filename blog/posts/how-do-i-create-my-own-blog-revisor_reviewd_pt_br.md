---
title: "Criando Meu Próprio Revisor de Blog com FastAPI e Langchain"
date: "2026-05-15"
summary: "Descubra como eu construí um revisor de blog usando FastAPI e Langchain para aprimorar meus processos de escrita e tradução."
tags: ["Python", "FastAPI", "IA", "LLM"]
published: true
---

## Introdução

Como um blogueiro iniciante, sempre busquei maneiras de aprimorar meu processo de escrita. Criar conteúdo envolvente enquanto garantimos que meus posts estejam polidos e bem estruturados é meu objetivo. Além disso, traduzir meu conteúdo para o português apresentou um desafio. Essa necessidade inspirou a ideia de criar meu próprio revisor de blog usando FastAPI e Langchain. Neste post, compartilharei os detalhes deste projeto e como ele transformou meu fluxo de trabalho de escrita.

## Visão Geral do Projeto

O principal objetivo deste projeto foi desenvolver um agente inteligente capaz de revisar meus posts em inglês e traduzi-los para o português. Aproveitando Python, FastAPI para o backend e Langchain para a integração do modelo de linguagem, criei um fluxo de trabalho simplificado que aprimora tanto os processos de escrita quanto de tradução.

## Começando

Para dar início ao projeto, criei um ambiente virtual e configurei as dependências necessárias. Veja como você pode replicar minha configuração:

```bash
python3 -m venv venv
source venv/bin/activate

# Crie um novo arquivo requirements.txt
touch requirements.txt

# Instale as dependências
pip install -r requirements.txt
```

Aqui está o conteúdo do meu arquivo `requirements.txt`:

```
fastapi==0.110.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.1
pydantic==2.6.4
python-multipart==0.0.9

# Pilha LLM
openai==1.14.3
langchain==0.1.16
langchain-openai==0.1.3
langchain-groq

# Cliente HTTP assíncrono (útil para integrações)
httpx==0.27.0

# Pilha RAG
chromadb
langchain-chroma
langchain-core
```

## Construindo os Agentes

Desenvolvi três agentes principais para lidar com diferentes tarefas:

### 1. Agente de Escrita de Postagem de Blog

Esse agente transforma notas brutas em uma postagem de blog estruturada, organizando o conteúdo e gerando um arquivo markdown.

```python
class BlogPostWriterAgent:
    """Agente responsável por transformar notas esboçadas em postagens de blog estruturadas."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)
        self.blog_reviewer = BlogReviewerAgent()

    # ... [Restante do código]
```

### 2. Agente Revisor de Blog

Esse agente revisa a postagem de blog gerada, sugerindo melhorias e identificando erros.

```python
class BlogReviewerAgent:
    """Agente responsável por revisar postagens de blog em Markdown."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.GROQ)

    # ... [Restante do código]
```

### 3. Agente Tradutor de Postagem de Blog

Esse agente traduz as postagens em inglês revisadas para o português brasileiro.

```python
class BlogPostTranslatorAgent:
    """Agente responsável por traduzir postagens revisadas para pt-BR."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)

    # ... [Restante do código]
```

## Processando o Conteúdo

Uma vez que o código foi escrito, o fluxo de trabalho se desenrolou da seguinte forma:

1. A postagem de blog inicial foi criada e revisada três vezes pelo Agente Revisor de Blog.
2. A saída final foi traduzida para o português pelo Agente Tradutor de Postagem de Blog.
3. O resultado foram dois arquivos markdown:
   - `your-roots-are-not-controllers_reviewed_pt_br.md`: A versão em português.
   - `your-roots-are-not-controllers_reviewed.md`: A versão em inglês.

## Registro para Insights

Para monitorar as operações e entender as interações entre os agentes, implementei o registro. Aqui está um exemplo da saída de log:

```bash
2026-05-16 09:43:25,880 | INFO | httpx | Requisição HTTP: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-16 09:43:25,919 | INFO | blog.agents.blog_post_writer.agent | blog_post_writer: ciclo 1/3 - revisão recebida (erros=0, dicas=0, checklist=0)
# ... [Mais entradas de log]
```

## Desafios Enfrentados

Um desafio significativo foi garantir que o revisor fornecesse feedback construtivo. Modelos de IA frequentemente se concentram em corrigir problemas em vez de destacar pontos fortes, complicando o processo de revisão. Após experimentar vários modelos, incluindo Grok, descobri que o GPT-4 da OpenAI gerou os melhores resultados.

No futuro, pretendo aprimorar o processo de seleção de modelos, optando por modelos mais avançados para o revisor e modelos mais simples para as tarefas de tradução.

## Conclusão

Criar meu próprio revisor de blog melhorou significativamente meu processo de escrita e aprofundou minha compreensão de como a IA pode ajudar na criação de conteúdo. Eu encorajo qualquer pessoa interessada em explorar este projeto mais a fundo a conferir o código completo em meu repositório do GitHub: [phablo200/blog-reviewer](https://github.com/phablo200/blog-reviewer).

Este projeto demonstra o potencial de combinar FastAPI e Langchain para desenvolver aplicações práticas que aprimoram a produtividade e a qualidade da escrita. Ao iniciar seus próprios projetos, considere como a tecnologia pode apoiar seu processo criativo.
