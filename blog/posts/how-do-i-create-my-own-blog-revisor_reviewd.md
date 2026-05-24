---
title: "Creating My Own Blog Revisor with FastAPI and Langchain"
date: "2026-05-15"
summary: "Discover how I built a blog revisor using FastAPI and Langchain to enhance my writing and translation processes."
tags: ["Python", "FastAPI", "AI", "LLM"]
published: true
---

## Introduction

As a budding blogger, I have always sought ways to improve my writing process. Crafting engaging content while ensuring that my posts are polished and well-structured is my goal. Additionally, translating my content into Portuguese posed a challenge. This need sparked the idea of creating my own blog revisor using FastAPI and Langchain. In this post, I will share the details of this project and how it has transformed my writing workflow.

## Project Overview

The main objective of this project was to develop an intelligent agent capable of revising my English blog posts and translating them into Portuguese. By leveraging Python, FastAPI for the backend, and Langchain for language model integration, I created a streamlined workflow that enhances both writing and translation processes.

## Getting Started

To kick off the project, I created a virtual environment and set up the necessary dependencies. Here’s how you can replicate my setup:

```bash
python3 -m venv venv
source venv/bin/activate

# Create a new requirements.txt file
touch requirements.txt

# Install dependencies
pip install -r requirements.txt
```

Here’s the content of my `requirements.txt` file:

```
fastapi==0.110.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.1
pydantic==2.6.4
python-multipart==0.0.9

# LLM stack
openai==1.14.3
langchain==0.1.16
langchain-openai==0.1.3
langchain-groq

# Async HTTP client (useful for integrations)
httpx==0.27.0

# RAG stack
chromadb
langchain-chroma
langchain-core
```

## Building the Agents

I developed three main agents to handle different tasks:

### 1. Blog Post Writer Agent

This agent transforms raw notes into a structured blog post, organizing the content and generating a markdown file.

```python
class BlogPostWriterAgent:
    """Agent responsible for turning sketch notes into structured blog posts."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)
        self.blog_reviewer = BlogReviewerAgent()

    # ... [Rest of the code]
```

### 2. Blog Reviewer Agent

This agent reviews the generated blog post, suggesting improvements and identifying any errors.

```python
class BlogReviewerAgent:
    """Agent responsible for revising blog posts in Markdown."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.GROQ)

    # ... [Rest of the code]
```

### 3. Blog Post Translator Agent

This agent translates the reviewed English posts into Brazilian Portuguese.

```python
class BlogPostTranslatorAgent:
    """Agent responsible for translating reviewed posts to pt-BR."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)

    # ... [Rest of the code]
```

## Processing the Content

Once the code was written, the workflow unfolded as follows:

1. The draft blog post was created and revised three times by the Blog Reviewer Agent.
2. The final output was translated into Portuguese by the Blog Post Translator Agent.
3. The result was two markdown files:
   - `your-roots-are-not-controllers_reviewed_pt_br.md`: The Portuguese version.
   - `your-roots-are-not-controllers_reviewed.md`: The English version.

## Logging for Insights

To monitor operations and understand the interactions between the agents, I implemented logging. Here’s an example of the log output:

```bash
2026-05-16 09:43:25,880 | INFO | httpx | HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-16 09:43:25,919 | INFO | blog.agents.blog_post_writer.agent | blog_post_writer: cycle 1/3 - revision received (errors=0, tips=0, checklist=0)
# ... [More log entries]
```

## Challenges Faced

A significant challenge was ensuring the reviewer provided constructive feedback. AI models often focus on correcting issues rather than highlighting strengths, complicating the revision process. After experimenting with various models, including Grok, I found that OpenAI's GPT-4 yielded the best results. 

In the future, I plan to enhance the model selection process, opting for more advanced models for the reviewer and simpler ones for translation tasks.

## Conclusion

Creating my own blog revisor has significantly improved my writing process and deepened my understanding of how AI can assist in content creation. I encourage anyone interested in exploring this project further to check out the complete code in my GitHub repository: [phablo200/blog-reviewer](https://github.com/phablo200/blog-reviewer).

This project showcases the potential of combining FastAPI and Langchain to develop practical applications that enhance productivity and the quality of writing. As you embark on your own projects, consider how technology can support your creative process.
