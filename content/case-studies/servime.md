---
id: servime
title: ServiME
related: [servime]
period: "2025-06"
role: Lead developer
stack: [Laravel, PHP, MySQL, Blade, Tailwind CSS, Alpine.js, OpenAI, Gemini]
lang: en
---

# ServiME

## Summary

ServiME is a multi-tenant SaaS that turns a restaurant's menu, uploaded as a PDF or a photo, into a digital menu with a QR code. The menu comes with an AI assistant that answers questions about the real dishes, a pre-order list, table orders for the waiter's screen and analytics for the owner. Leonardo Mannanice designed and built the platform, which is in production at Azopardo Café Bar, where it improved service speed by 20%.

## Context and problem

Restaurant menus are usually PDFs: heavy and hard to read on a phone. Customers keep asking the waiter the same things, such as what a dish contains, whether it is safe for people with celiac disease or what the staff recommends. The business, in turn, does not know what its customers look at or ask about. ServiME is sold as a subscription, so each business needs to start without typing its dishes one by one, and the cost of the AI has to stay under the price of its plan.

## Leonardo's role

Leonardo is the lead developer of ServiME. He designed and built the whole platform: the Laravel backend, the Blade and Tailwind CSS frontend, the database, the integration with the AI providers and the automated deploy. He also made the choices about AI costs, security and plans described below.

## Architecture

ServiME is a Laravel 12 application (PHP 8.2) with MySQL, a Blade, Tailwind CSS and Alpine.js frontend built with Vite, and Laravel Breeze for sign-in. Every business lives under its own address, `/menu/{slug}`, and the system keeps the history of each slug so printed QR codes never break.

From a menu file to an answer:

```
PDF or photo -> background job -> Gemini reads the menu -> categories, dishes, prices
                                                               |
Customer scans the QR -> search in PHP -> OpenAI answers -> dish cards with photo and price
```

- **Menu processing.** A queued job sends the file to Google Gemini, which extracts categories, dishes, descriptions and prices. The menu moves through the states processing, ready and error. Stuck menus are rescued automatically and the owner gets an email when the menu is ready.
- **Chat.** The assistant is hybrid: PHP searches the menu first and only then calls OpenAI. The model answers with markers (`[[PLATOS]]` for dishes, `[[FALTA]]` for something the menu does not have) that the system turns into real dish cards. The answer is streamed.
- **Plans.** Five plans (Free, Mínimo, Básico, Pro and Premium) are stored in the database and edited by the super admin without a deploy. A plan sets the monthly AI message quota, the number of menus, the OpenAI model, the token limit and the features available. A quota of 0 means no assistant: the menu opens directly on the classic list.
- **Restaurant operations.** Each table has its own QR with a rotating token. The waiter uses a screen protected by a PIN, without a user account, to open tables, edit orders and close them. Inactive orders are closed automatically every 15 minutes.
- **Analytics.** Conversations and menu events feed a panel per business and a general one, with a funnel, a heatmap and an AI classification of what customers want.
- **Deploy.** A push to `main` runs a GitHub Actions workflow that deploys to Hostinger over SSH.

## Key decisions and trade-offs

- **Search in PHP before calling the model.** ServiME searches the menu itself and gives the model only the relevant dishes. This lowers the cost and the chance of invented answers, and the assistant says "we don't have that" instead of making something up. The trade-off is more code to maintain than sending the whole menu in the prompt.
- **Two AI providers for different tasks.** Gemini reads the menus, which is cheap and good with PDFs. OpenAI handles the chat. Leonardo picked the Gemini model by processing the same menus with four versions and comparing the results.
- **Plans in the database.** Prices, quotas, models and features are data, not code. Changing a plan needs no deploy, and each plan chooses its OpenAI model, so the cost of the AI follows its price. The trade-off is a validation layer for dependencies between features, for example table orders require tables.
- **A fixed stack Leonardo knows well.** Laravel with Blade, instead of a separate frontend, keeps one codebase and a simple deploy on shared hosting.

## Challenges

- **Cost control.** The chat has a monthly quota per business and a rate limit of 20 messages per minute per device, plus a limit per IP. The limit counts devices because all the customers of a restaurant share one Wi-Fi network and share an IP address.
- **Search engines using the AI.** Search engine robots ran the page's JavaScript and consumed AI messages. Leonardo closed it with `robots.txt` and a middleware that blocks robots.
- **Silent downgrade.** If Gemini fails, the menu processor falls back to OpenAI Vision, which can invent prices, so a disabled model gives worse menus instead of an error. This is documented in the project and kept in mind when changing models.
- **Heavy images on mobile data.** Dish photos are shrunk and converted to WebP automatically, which typically saves 89% of their size.
- **Security.** Protection against path traversal when serving logos, rotating table tokens, a PIN for the waiter, no trust in proxy headers to find the client IP, and no secrets in the repository.

## Results

- ServiME is in production at Azopardo Café Bar, where it improved service speed by 20%.
- The platform covers the whole cycle: menu, chat, pre-order, table, waiter and analytics.
- Customers need no app and no registration: they scan the QR and enter.
- The project has 433 commits since June 2025 and a PHPUnit test suite.
- The current goal is to start charging for the plans.
