# Augment Guidelines: Full-Stack Development

**Purpose:** To guide AI-assisted ("vibe") coding by grounding it in project documentation, best practices, and explicit standards. This file ensures a "highly prepared" approach, mitigating risks associated with unguided AI code generation while leveraging its speed.

**Core Principles:**

- **Documentation First:** ALWAYS consult relevant project documentation (Requirements, Architecture Docs, API Specs, Style Guides) _before_ prompting the AI. Ground prompts in documented facts.
- **Review is Mandatory:** ALL AI-generated code _must_ be reviewed for correctness, security, performance, and adherence to these guidelines before committing. Treat AI as a pair programmer whose work needs checking.
- **Understand the Output:** Do not commit code you cannot explain. Use the AI to help understand complex generated code if necessary.
- **Log Assumptions:** If documentation is unclear or missing, explicitly log any assumptions made when prompting the AI or accepting its suggestions in the commit message or a designated log.
- **Iterative Refinement:** Use AI for initial drafts ("vibe") but expect to refine, refactor, and test thoroughly.

---

## 1. Documentation Usage Policy

- **Reference Specific Docs:** When prompting for code related to specific features, APIs, or components, reference the relevant document and section (e.g., "Implement the user authentication flow as described in `docs/auth.md#jwt-flow`").
- **Translate Docs to Prompts:** Extract key requirements, constraints, data structures, and logic from documentation to form specific, actionable prompts.
- **Ask About Ambiguities:** If documentation is unclear, use the AI to explore potential interpretations, but _log the ambiguity and chosen path_.

---

## 2. General Coding Standards

- **Naming Conventions:**
  - Variables/Functions: `camelCase` (JavaScript/TypeScript), `snake_case` (Python/Ruby - adjust per backend language)
  - Classes/Components: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Use descriptive names; avoid single letters or overly generic terms (e.g., `data`, `handleStuff`).
- **Formatting:**
  - Indentation: 4 spaces (or project standard).
  - Line Length: Max 120 characters (or project standard).
  - Brace Style: Consistent (e.g., opening brace on the same line).
  - Use linters/formatters (e.g., Prettier, ESLint, Black) and configure the AI to adhere to their rules if possible.
- **Comments:**
  - Explain _why_, not _what_, for complex logic.
  - Mandatory for non-obvious AI-generated algorithms or complex business rules.
  - Use standard formats (e.g., JSDoc, Python docstrings) for functions/classes.
- **Modularity:**
  - Adhere to the Single Responsibility Principle (SRP).
  - Keep functions/methods short and focused.
  - Follow the DRY (Don't Repeat Yourself) principle.

---

## 3. Version Control (Git)

- **Branching:** All AI-assisted work MUST be done in feature branches, branched from `develop` (or project standard). NEVER push directly to `main` or `develop`.
- **Commits:**
  - Commit frequently with clear, descriptive messages.
  - Prefix commits involving significant AI generation/modification (e.g., `feat(ai): Implement user profile endpoint via Copilot`).
  - Reference relevant issue numbers and logged assumptions.
- **Pull Requests (PRs):**
  - ALL code requires PR review before merging.
  - PR description should summarize changes, link issues, and note significant AI involvement.
  - Ensure code builds and passes all tests/checks before submitting PR.
- **Rebasing:** Rebase feature branches onto the target branch (`develop`) interactively before creating a PR to maintain a clean history. Resolve conflicts locally.

---

## 4. Frontend Guidelines (e.g., React/Next.js)

- **Project Structure:** Follow established project structure (e.g., feature-based folders, `components/`, `hooks/`, `utils/`, Next.js `app` dir conventions).
- **Component Design:**
  - Functional components with Hooks preferred.
  - Break down complex components into smaller, reusable ones.
  - Adhere to project's UI Kit/Design System components and styles.
- **State Management:** Use project's designated state management library/pattern (e.g., Redux Toolkit, Zustand, Context API) correctly.
- **API Interaction:** Use designated API client/hooks (potentially auto-generated from API spec if using tools like Orval). Handle loading and error states explicitly.
- **Styling:** Follow project's CSS methodology (e.g., CSS Modules, Tailwind CSS, Styled Components).
- **Accessibility (a11y):** Ensure generated components follow accessibility best practices (semantic HTML, ARIA attributes where needed, keyboard navigation).

---

## 5. Backend Guidelines (e.g., Node.js/Express)

- **Project Structure:** Follow established structure (e.g., MVC, feature-based, separate `routes/`, `controllers/`, `services/`, `models/` or `dal/`).
- **API Design:** Adhere to RESTful principles (use nouns for resources, appropriate HTTP methods, standard status codes) as defined in the API Contract.
- **Error Handling:**
  - Implement centralized error handling middleware.
  - Use specific, informative error codes and messages (consistent with API Contract).
  - Log errors effectively (include stack trace, request context, timestamp). Use `try/catch` appropriately.
- **Validation:** Implement robust input validation (request body, query params, path params) using specified library (e.g., Zod, Joi, class-validator).
- **Logging:** Use project's standard logging library and format. Log key events, errors, and relevant context.

---

## 6. API Contract Adherence

- **Canonical Source:** The OpenAPI Specification (OAS) file (`path/to/openapi.yaml` or similar) is the single source of truth for API structure.
- **Prompting:** When generating backend routes or frontend clients, explicitly instruct the AI to conform _exactly_ to the schemas, endpoints, methods, and status codes defined in the OAS file.
- **Validation:** Generated code MUST include validation against the defined request/response schemas.
- **Error Responses:** Ensure error responses match the formats specified in the OAS file.
- **Versioning:** Implement API changes according to the project's versioning strategy documented in the OAS.

---

## 7. Data Management & Database Interaction

- **Interaction Pattern:** Use the established Data Access Layer (DAL), Object-Relational Mapper (ORM - e.g., Prisma, TypeORM, SQLAlchemy), or Data Access Objects (DAO) for all database interactions. Do not write raw SQL queries directly in business logic unless absolutely necessary and approved.
- **Query Optimization:**
  - Instruct AI to generate efficient queries. Be mindful of N+1 problems.
  - Utilize database indexes appropriately – reference schema documentation.
  - Select only necessary fields; avoid `SELECT *`.
- **Data Validation:** Validate data before writing to the database according to model constraints.
- **Migrations:** Database schema changes MUST be handled through the project's migration tool (e.g., Prisma Migrate, Alembic, Knex migrations). AI should not generate direct schema-altering commands.
- **Security:** ALWAYS use parameterized queries or ORM methods that prevent SQL injection. Sanitize all inputs influencing queries.

---

## 8. Security

- **Input Validation:** Reiterate: All external input (API requests, user forms) MUST be validated on the backend.
- **Authentication/Authorization:** Implement using project's standard libraries/mechanisms (e.g., JWT, OAuth, session management). Enforce authorization checks at appropriate layers (e.g., route middleware, service layer).
- **Secrets Management:** Use environment variables or a secrets manager for API keys, database credentials, etc. DO NOT hardcode secrets.
- **Dependencies:** Use tools to scan dependencies for vulnerabilities. Keep libraries updated.
- **Rate Limiting/Security Headers:** Ensure appropriate middleware is used as per project standards.

---

## 9. Testing

- **Test Generation:** Instruct the AI to generate relevant tests (Unit, Integration) alongside feature code.
  - **Unit Tests:** Focus on individual functions/modules/components in isolation (use mocking).
  - **Integration Tests:** Test interactions between components (e.g., API endpoint hitting service layer and mock DAL).
- **Frameworks:** Use the project's standard testing frameworks (e.g., Jest, Vitest, Pytest, JUnit).
- **Coverage:** Aim for project's target code coverage. AI-generated code MUST be included in coverage metrics.
- **Assertions:** Write clear, specific assertions. Test edge cases and error conditions identified during documentation review or AI prompting.

---

## 10. Assumption Logging

- **Requirement:** When documentation is missing/ambiguous, or an AI suggestion deviates significantly from expectations, the developer MUST log the assumption made.
- **Method:** Include a clear `ASSUMPTION:` note in the relevant commit message or PR description.
  - _Example:_ `ASSUMPTION: Documentation for error code 4_xx unclear; implemented standard 400 Bad Request based on common patterns.`
- **Purpose:** Provides context for future developers and code reviewers, highlighting areas where documentation or requirements may need clarification.

---

_This document is a living guideline. Please suggest updates via PR if standards evolve or ambiguities are found._
