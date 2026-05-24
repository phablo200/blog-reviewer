---
title: "Criando Meu Próprio Revisor de Blog com FastAPI e Langchain"
date: "2026-05-15"
summary: "Aprenda como desenvolvi um revisor de blog usando FastAPI e Langchain para otimizar meu processo de escrita e tradução."
tags: ["Python", "FastAPI", "AI", "LLM"]
published: true
---

## Introdução

Como um blogueiro iniciante, sempre busquei maneiras de aprimorar meu processo de escrita. Meu objetivo é criar conteúdo envolvente enquanto garanto que minhas postagens sejam polidas e bem estruturadas. Além disso, traduzir meu conteúdo para o português apresentou um desafio. Essa necessidade me inspirou a criar meu próprio revisor de blog usando FastAPI e Langchain. Neste post, detalharei este projeto e explicarei como ele transformou meu fluxo de trabalho de escrita.

## Visão Geral do Projeto

O principal objetivo deste projeto foi desenvolver um agente inteligente capaz de revisar minhas postagens de blog em inglês e traduzi-las para o português. Aproveitando Python, FastAPI para o backend e Langchain para a integração do modelo de linguagem, criei um fluxo de trabalho simplificado que melhora tanto o processo de escrita quanto o de tradução.

## Começando

Para iniciar o projeto, criei um ambiente virtual e configurei as dependências necessárias. Aqui está como você pode replicar minha configuração:

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

# Stack LLM
openai==1.14.3
langchain==0.1.16
langchain-openai==0.1.3
langchain-groq==0.1.0

# Cliente HTTP assíncrono
httpx==0.27.0
```

## Construindo os Agentes

Desenvolvi três agentes principais para lidar com diferentes tarefas dentro do processo de revisão do blog:

### 1. Agente Escritor de Postagens de Blog

Esse agente transforma anotações brutas em uma postagem de blog estruturada, organizando o conteúdo e gerando um arquivo Markdown.

```python
class BlogPostWriterAgent:
    """Agente responsável por transformar anotações em esboço em postagens de blog estruturadas."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)
        self.blog_reviewer = BlogReviewerAgent()

    # Métodos adicionais para processamento de conteúdo...
```

### 2. Agente Revisor de Blog

Esse agente revisa a postagem de blog gerada, sugerindo melhorias e identificando erros.

```python
class BlogReviewerAgent:
    """Agente responsável por revisar postagens de blog em Markdown."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.GROQ)

    # Métodos adicionais para revisar conteúdo...
```

### 3. Agente Tradutor de Postagens de Blog

Esse agente traduz as postagens em inglês revisadas para o português brasileiro.

```python
class BlogPostTranslatorAgent:
    """Agente responsável por traduzir postagens revisadas para pt-BR."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)

    # Métodos adicionais para tradução...
```

## Processamento do Conteúdo

Uma vez que o código foi escrito, o fluxo de trabalho se desenrolou da seguinte maneira:

1. A postagem de blog em rascunho foi criada e revisada três vezes pelo Agente Revisor de Blog.
2. A saída final foi traduzida para o português pelo Agente Tradutor de Postagens de Blog.
3. O resultado foi dois arquivos Markdown:
   - `public/labs/your-roots-are-not-controllers_reviewed_pt_br.md`: A versão em português.
   - `public/labs/your-roots-are-not-controllers_reviewed.md`: A versão em inglês.
4. Criei versões em PDF baseadas no Markdown para meus estudos, utilizando `markdown` e `weasyprint` para conversão:
   - `public/labs/your-roots-are-not-controllers_reviewed_pt_br.pdf`: A versão em português.
   - `public/labs/your-roots-are-not-controllers_reviewed.pdf`: A versão em inglês.

Além disso, configurei endpoints para expor esses arquivos para download:
- `content/markdown/<filename>`
- `content/pdf/<filename>`

## Log para Insights

Para monitorar as operações e entender as interações entre os agentes, implementei um sistema de log. Aqui está um exemplo da saída do log:

```bash
2026-05-16 09:43:25,880 | INFO | httpx | Requisição HTTP: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-16 09:43:25,919 | INFO | blog.agents.blog_post_writer.agent | blog_post_writer: ciclo 1/3 - revisão recebida (erros=0, dicas=0, checklist=0)
# Entradas adicionais do log...
```

Esse sistema de log fornece insights sobre a operação de cada agente, facilitando a solução de problemas e a otimização do fluxo de trabalho.

## Desafios Enfrentados

Um desafio significativo foi garantir que o revisor fornecesse feedback construtivo. Modelos de IA frequentemente se concentram em corrigir problemas em vez de destacar pontos fortes, complicando o processo de revisão. Após experimentar vários modelos, incluindo Grok, descobri que o GPT-4 da OpenAI gerou os melhores resultados.

No futuro, planejo aprimorar o processo de seleção de modelos, optando por modelos mais avançados para o revisor e mais simples para as tarefas de tradução. Essa abordagem melhorará a qualidade geral das revisões e traduções.

## Conclusão

Criar meu próprio revisor de blog melhorou significativamente meu processo de escrita e aprofundou meu entendimento sobre como a IA pode ajudar na criação de conteúdo. Eu encorajo qualquer pessoa interessada em explorar mais este projeto a conferir o código completo no meu [repositório GitHub](https://github.com/phablo200/blog-reviewer).

Este projeto demonstra o potencial de combinar FastAPI e Langchain para desenvolver aplicações práticas que aumentam a produtividade e a qualidade da escrita. Ao iniciar seus próprios projetos, considere como a tecnologia pode apoiar seu processo criativo.
