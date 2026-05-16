# Suas Rotas Não São Controladores (E Isso Está Te Custando)

Por dois anos, permiti que a lógica de negócios residisse diretamente dentro dos manipuladores de rotas em uma API Node.js. Essa abordagem resultou em um emaranhado de código que era difícil de manter e escalar. Recentemente, embarquei em uma jornada de refatoração para separar as preocupações e introduzir uma camada de controladores adequada, o que melhorou significativamente a arquitetura da minha aplicação. Neste post, vou descrever os passos que tomei para refatorar minha API Node.js, movendo a lógica de negócios para fora das rotas e para controladores dedicados.

## Identificando os Problemas com Lógica Inline

A estrutura inicial da minha API integrava a lógica de negócios diretamente dentro dos arquivos de rota. Essa mescla de responsabilidades tornava desafiador gerenciar e testar o código. Por exemplo, no arquivo `auth.routes.ts`, múltiplos endpoints lidavam com vários aspectos da autenticação enquanto continham lógica inline que complicava as rotas.

Aqui está um exemplo da antiga estrutura de rota para fazer login de usuários:

```typescript
router.post('/signin', async (request: Request, response: Response) => {
    const { email, password } = request.body;
    if (!email || !password) {
        return response.status(STATUS.BAD_REQUEST).send({ data: 'Login inválido' });
    }
    try {
        const user = await authService.signIn(email, password);
        return response.send({ data: user });
    } catch (e) {
        return response.status(STATUS.BAD_REQUEST).send({ error: 'Login inválido' });
    }
});
```

Essa lógica inline dificultava o acompanhamento e os testes. Para melhorar a clareza e a manutenibilidade, decidi migrar a lógica para controladores dedicados.

## O Processo de Refatoração: Passos para o Sucesso

### Passo 1: Estabelecer uma Camada de Controladores Dedicada

O primeiro passo foi criar um novo arquivo de controlador para cada arquivo de rota. Por exemplo, criei `auth.controller.ts` para as rotas de autenticação. Cada arquivo de controlador agora contém funções que lidam com a lógica de negócios da respectiva rota.

```typescript
// src/controllers/auth.controller.ts
import { Request, Response } from 'express';
import authService from '../services/auth.service';

export async function signIn(req: Request, res: Response) {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(STATUS.BAD_REQUEST).send({ data: 'Login inválido' });
    }
    try {
        const user = await authService.signIn(email, password);
        return res.send({ data: user });
    } catch (e) {
        return res.status(STATUS.BAD_REQUEST).send({ error: 'Login inválido' });
    }
}
```

### Passo 2: Atualizar os Arquivos de Rota para Referenciar Controladores

Em seguida, modifiquei os arquivos de rota para referenciar os novos métodos do controlador em vez de conter a lógica de negócios. Por exemplo, o arquivo `auth.routes.ts` foi atualizado da seguinte forma:

```typescript
import { Router } from 'express';
import * as authController from '../controllers/auth.controller';

const router = Router();

router.post('/signin', authController.signIn);
```

### Passo 3: Migrar Todos os Arquivos de Rota de Forma Consistente

Seguindo o mesmo padrão, migrei cada arquivo de rota para seu respectivo arquivo de controlador, incluindo rotas de cartões, rotas de categorias e outras. O objetivo era garantir que cada arquivo de rota apenas conectasse caminhos HTTP a funções do controlador sem qualquer lógica de negócios embutida.

Aqui está um exemplo da migração para o `cards.routes.ts`:

**Antes da migração:**

```typescript
router.post('/', async (request: Request, response: Response) => {
    const cardData = request.body;
    const cardSaved = await cardService.createCard(cardData);
    return response.status(STATUS.CREATED).send(cardSaved);
});
```

**Após a migração:**

```typescript
import * as cardController from '../controllers/cards.controller';

router.post('/', cardController.createCard);
```

### Passo 4: Teste Abrangente dos Endpoints

Após migrar as rotas para os controladores, realizei testes manuais em cada endpoint para garantir que tudo funcionasse corretamente. Este passo foi crucial para identificar quaisquer problemas que surgiram durante o processo de migração.

## Conclusão: Os Benefícios da Refatoração

Ao migrar a lógica de negócios dos meus manipuladores de rotas para arquivos de controladores dedicados, alcancei um código mais limpo e fácil de manter. Essa separação de preocupações simplifica os testes e a escalabilidade da aplicação.

Essa jornada de refatoração não apenas melhorou a estrutura da minha API, mas também aprofundou meu entendimento sobre a arquitetura adequada de aplicações. Se você ainda está misturando a lógica de negócios com suas rotas, recomendo fortemente que reserve um tempo para refatorar seu código. Os benefícios a longo prazo, incluindo clareza, manutenibilidade e testabilidade aprimoradas, valem muito a pena!