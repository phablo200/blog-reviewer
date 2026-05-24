---
title: "Refatorando Sua API Node.js: Por Que Suas Rotas Não Devem Ser Controladores"
date: "2026-05-15"
summary: "Aprenda como refatorar sua API Node.js separando rotas de controladores para melhorar a manutenibilidade e legibilidade."
tags: ["Node.js", "API", "Refatoração", "Melhores Práticas"]
published: true
---

# Refatorando Sua API Node.js: Por Que Suas Rotas Não Devem Ser Controladores

Por dois anos, permiti que a lógica de negócio residisse dentro dos meus arquivos de rota em uma API Node.js. Essa abordagem sobrecarregou minhas definições de rota e tornou difícil gerenciar e escalar a aplicação de maneira eficaz. Neste post, compartilharei como refatorei minha API Node.js introduzindo uma camada de controlador adequada e migrando a lógica de negócio para fora das rotas.

## O Problema da Lógica de Negócio nas Rotas

Integrar a lógica de negócio nos manipuladores de rota pode levar a vários problemas:

1. **Manutenibilidade**: À medida que a aplicação cresce, as rotas se tornam difíceis de gerenciar.
2. **Testes**: Testar rotas com lógica embutida é complicado e pode gerar testes frágeis.
3. **Separação de Preocupações**: Misturar lógica de roteamento com lógica de negócio complica a compreensão da estrutura da aplicação.

## Benefícios de Separar Rotas e Controladores

Separar rotas de controladores oferece várias vantagens:

- **Melhor Legibilidade**: Uma clara distinção entre lógica de roteamento e lógica de negócio torna o código mais fácil de ler e entender.
- **Aprimoramento na Testabilidade**: Funções de controlador isoladas podem ser testadas independentemente, resultando em testes mais robustos.
- **Manutenção Facilitada**: Alterações na lógica de negócio podem ser feitas nos arquivos de controlador sem afetar a estrutura de roteamento.

## Refatorando a Arquitetura

Para abordar os problemas identificados, migrei a lógica de negócio dos arquivos de rota para arquivos de controlador dedicados. O objetivo era garantir que os arquivos de rota apenas lidassem com as requisições HTTP e delegassem o processamento real para os métodos do controlador.

### Processo de Migração

O processo de migração envolveu os seguintes passos:

1. **Identificar Manipuladores de Rota**: Revisar arquivos de rota para encontrar manipuladores que contêm lógica inline.
2. **Criar Arquivos de Controlador**: Para cada arquivo de rota, criar um arquivo de controlador correspondente, se ainda não existir.
3. **Mover Lógica para os Controladores**: Transferir a lógica dos manipuladores de rota para funções nomeadas adequadamente nos arquivos de controlador.
4. **Atualizar Arquivos de Rota**: Substituir manipuladores inline nos arquivos de rota por referências às funções correspondentes do controlador.
5. **Testes**: Após a migração, testar manualmente todos os endpoints para garantir que a funcionalidade permaneça intacta.

### Exemplo de Migração

Aqui está uma visão detalhada do processo de migração:

#### Antes da Migração (auth.routes.ts)

```typescript
router.post('/signin', async (request: Request, response: Response) => {
    const { email, password } = request.body;
    // Lógica para logar
});
```

#### Depois da Migração (auth.routes.ts)

```typescript
import { authController } from '../controllers/auth.controller';

router.post('/signin', authController.signIn);
```

#### Arquivo de Controlador (auth.controller.ts)

```typescript
import { Request, Response } from 'express';
import authService from '../services/auth.service';
import { STATUS } from '../util/status.util';

export async function signIn(req: Request, res: Response) {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(STATUS.BAD_REQUEST).send({ error: 'Login inválido' });
    }

    try {
        const user = await authService.signIn(email, password);
        return res.send({ data: user });
    } catch (e) {
        return res.status(STATUS.BAD_REQUEST).send({ error: 'Login inválido' });
    }
}
```

## Estrutura do Projeto

Após concluir a migração de todos os arquivos de rota para controladores, a estrutura do projeto agora é a seguinte:

### Arquivos de Rota (`src/routes`)

- `audio.routes.ts`
- `auth.routes.ts`
- `bugreport.routes.ts`
- `cards.routes.ts`
- `category.routes.ts`
- `deck.routes.ts`
- `healthcheck.routes.ts`
- `internal.routes.ts`

### Arquivos de Controlador (`src/controllers`)

- `audio.controller.ts`
- `auth.controller.ts`
- `bugreport.controller.ts`
- `cards.controller.ts`
- `category.controller.ts`
- `deck.controller.ts`
- `internal.controller.ts`

## Armadilhas Comuns a Evitar

Ao refatorar seus arquivos de rota, esteja atento às seguintes armadilhas comuns:

- **Negligenciar Testes**: Sempre certifique-se de testar todos os endpoints após a refatoração para identificar quaisquer problemas potenciais.
- **Convenções de Nomenclatura Inconsistentes**: Mantenha uma convenção de nomenclatura consistente para seus arquivos de controlador e serviço para aumentar a clareza.
- **Pular Documentação**: Atualize qualquer documentação para refletir a nova estrutura, facilitando a compreensão das mudanças pela sua equipe.

## Conclusão

Refatorar minha API Node.js para separar rotas de controladores melhorou significativamente a manutenibilidade e legibilidade. A nova estrutura está em conformidade com as melhores práticas, tornando mais fácil testar e escalar a aplicação. Se você se encontrar com arquivos de rota confusos, repletos de lógica de negócio, considere aplicar uma estratégia de refatoração semelhante. Seu código—e seu eu futuro—agradecerão!

## Melhores Práticas para Refatoração de Arquivos de Rota

Ao refatorar seus arquivos de rota, mantenha estas melhores práticas em mente:

- Adira ao princípio da separação de preocupações, mantendo sua lógica de roteamento e lógica de negócio em arquivos separados.
- Mantenha uma convenção de nomenclatura consistente para seus arquivos de controlador e serviço para aumentar a clareza.
- Revise e refatore regularmente seu código para evitar a acumulação de lógica inline em suas rotas.
- Implemente testes rigorosos após a refatoração para garantir que toda a funcionalidade permaneça intacta.
- Atualize a documentação para refletir a nova estrutura, facilitando a compreensão das mudanças pela sua equipe.
