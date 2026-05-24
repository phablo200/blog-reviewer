---
title: "Refactoring Your Node.js API: Why Your Routes Should Not Be Controllers"
date: "2026-05-15"
summary: "Learn how to refactor your Node.js API by separating routes from controllers to enhance maintainability and readability."
tags: ["Node.js", "API", "Refactoring", "Best Practices"]
published: true
---

# Refactoring Your Node.js API: Why Your Routes Should Not Be Controllers

For two years, I allowed business logic to reside within my route files in a Node.js API. This approach cluttered my route definitions and made it challenging to manage and scale the application effectively. In this post, I will share how I refactored my Node.js API by introducing a proper controller layer and migrating the business logic out of the routes.

## The Problem with Business Logic in Routes

Embedding business logic in route handlers can lead to several issues:

1. **Maintainability**: As the application grows, routes become unwieldy and difficult to manage.
2. **Testing**: Testing routes with embedded logic is cumbersome and can lead to fragile tests.
3. **Separation of Concerns**: Mixing routing logic with business logic complicates understanding the application's structure.

## Benefits of Separating Routes and Controllers

Separating routes from controllers offers several advantages:

- **Improved Readability**: A clear distinction between routing and business logic makes the code easier to read and understand.
- **Enhanced Testability**: Isolated controller functions can be tested independently, leading to more robust tests.
- **Easier Maintenance**: Changes to business logic can be made in the controller files without affecting the routing structure.

## Refactoring the Architecture

To address the identified issues, I migrated the business logic from route files into dedicated controller files. The goal was to ensure that route files only handle HTTP requests and delegate the actual processing to controller methods.

### Migration Process

The migration process involved the following steps:

1. **Identify Route Handlers**: Review route files to find handlers containing inline logic.
2. **Create Controller Files**: For each route file, create a corresponding controller file if it doesn't already exist.
3. **Move Logic to Controllers**: Transfer the logic from route handlers to appropriately named functions in the controller files.
4. **Update Route Files**: Replace inline handlers in route files with references to the corresponding controller functions.
5. **Testing**: After migration, manually test all endpoints to ensure functionality remains intact.

### Example Migration

Here's a detailed look at the migration process:

#### Before Migration (auth.routes.ts)

```typescript
router.post('/signin', async (request: Request, response: Response) => {
    const { email, password } = request.body;
    // Logic for signing in
});
```

#### After Migration (auth.routes.ts)

```typescript
import { authController } from '../controllers/auth.controller';

router.post('/signin', authController.signIn);
```

#### Controller File (auth.controller.ts)

```typescript
import { Request, Response } from 'express';
import authService from '../services/auth.service';
import { STATUS } from '../util/status.util';

export async function signIn(req: Request, res: Response) {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(STATUS.BAD_REQUEST).send({ error: 'Invalid login' });
    }

    try {
        const user = await authService.signIn(email, password);
        return res.send({ data: user });
    } catch (e) {
        return res.status(STATUS.BAD_REQUEST).send({ error: 'Invalid login' });
    }
}
```

## Project Structure

After completing the migration of all route files to controllers, the project structure now looks like this:

### Route Files (`src/routes`)

- `audio.routes.ts`
- `auth.routes.ts`
- `bugreport.routes.ts`
- `cards.routes.ts`
- `category.routes.ts`
- `deck.routes.ts`
- `healthcheck.routes.ts`
- `internal.routes.ts`

### Controller Files (`src/controllers`)

- `audio.controller.ts`
- `auth.controller.ts`
- `bugreport.controller.ts`
- `cards.controller.ts`
- `category.controller.ts`
- `deck.controller.ts`
- `internal.controller.ts`

## Common Pitfalls to Avoid

When refactoring your route files, be aware of the following common pitfalls:

- **Neglecting Testing**: Always ensure that you test all endpoints after refactoring to catch any potential issues.
- **Inconsistent Naming Conventions**: Maintain a consistent naming convention for your controller and service files to enhance clarity.
- **Skipping Documentation**: Update any documentation to reflect the new structure, making it easier for your team to understand the changes.

## Conclusion

Refactoring my Node.js API to separate routes from controllers has significantly improved maintainability and readability. The new structure adheres to best practices, making it easier to test and scale the application. If you find yourself with convoluted route files packed with business logic, consider applying a similar refactoring strategy. Your code—and your future self—will thank you!

## Best Practices for Refactoring Route Files

When refactoring your route files, keep these best practices in mind:

- Adhere to the principle of separation of concerns by keeping your routing logic and business logic in separate files.
- Maintain a consistent naming convention for your controller and service files to enhance clarity.
- Regularly review and refactor your codebase to prevent the accumulation of inline logic in your routes.
- Implement thorough testing after refactoring to ensure all functionality remains intact.
- Update documentation to reflect the new structure, making it easier for your team to understand the changes.
