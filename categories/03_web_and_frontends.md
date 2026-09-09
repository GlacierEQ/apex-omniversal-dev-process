# 💻 CATEGORY 03: Modern Web Applications & Frontends

## 1. Scope & Architectural Mandate
Governs high-performance, accessible, responsive, server-rendered and client-hydrated web user interfaces.

- **Domains**: Next.js App Router (React Server Components), streaming SSR, progressive web apps (PWA), micro-frontends, state stores (Zustand/Signals), web vitals optimization (LCP, INP, CLS).
- **Key Constraints**: Initial load under 1.5s, 60fps interaction responsiveness, zero Cumulative Layout Shift, full WCAG 2.1 AA accessibility compliance, zero hydration mismatches.

---

## 2. Polyglot Technology Stack
- **Primary Languages**: TypeScript, JavaScript, CSS / Tailwind CSS v4.
- **Frameworks & Libraries**: Next.js 15+, React 19, Radix UI, TanStack Query, Vitest, Playwright.
- **Build & Bundler**: Turbopack, Vite, esbuild.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Hydration Invariant**:
   - Zero non-deterministic rendering between server and client (e.g., date formatting, random IDs, or client-only cookies without explicit `useEffect` or dynamic boundaries).
2. **Type Safety & Data Fetching**:
   - Zero unchecked `any` types.
   - All server actions and API payloads must be validated at the boundary with Zod or TypeBox before consumption.
3. **Refusal Reason Codes**:
   - `ERR_WEB_INVALID_PAYLOAD`: Schema validation failed on input form or mutation.
   - `ERR_WEB_UNAUTHORIZED_SESSION`: User session invalid, expired, or missing required capability.
   - `ERR_WEB_RATE_LIMITED`: Excessive client requests detected.
   - `ERR_WEB_SSR_RENDER_TIMEOUT`: Server-side component streaming exceeded timeout limit.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Define target devices (mobile, tablet, desktop), browser matrix (Chrome, Safari, Firefox), and Core Web Vitals thresholds.
- Detail user authorization roles and access matrix.

### Stage 1: Architectural Modeling
- Separate server-only components (`async function Component()`) from client interactive islands (`'use client'`).
- Define atomic design hierarchy: Atoms -> Molecules -> Organisms -> Templates -> Pages.

### Stage 2: Pro-Code Implementation
- Implement strict accessible semantics (`aria-*`, `role`, keyboard focus traps).
- Wrap data fetching in React Suspense and Error Boundaries with dedicated fallback UI.

### Stage 3: Adversarial Verification
- Run headless browser tests with Playwright simulating high-latency 3G networks.
- Test keyboard navigation: verify complete flow without mouse interaction.
- Inject XSS vectors into form inputs; verify automatic HTML sanitization.

---

## 5. Reference Pattern: Fail-Closed Next.js Server Action
```typescript
import { z } from 'zod';

const ActionSchema = z.object({
  entityId: z.string().uuid(),
  actionType: z.enum(['ACTIVATE', 'DEACTIVATE', 'PURGE']),
  metadata: z.record(z.string()).default({}),
});

export type ActionInput = z.infer<typeof ActionSchema>;

export interface ActionResult {
  success: boolean;
  code: string;
  message: string;
  timestamp: string;
}

export async function executeSecureAction(rawInput: unknown): Promise<ActionResult> {
  // Fail-closed input parsing
  const parsed = ActionSchema.safeParse(rawInput);
  if (!parsed.success) {
    return {
      success: false,
      code: 'ERR_WEB_INVALID_PAYLOAD',
      message: parsed.error.issues.map(i => i.message).join(', '),
      timestamp: new Date().toISOString(),
    };
  }

  try {
    // Perform validated domain operation
    const { entityId, actionType } = parsed.data;
    // ... execute logic ...
    return {
      success: true,
      code: 'SUCCESS',
      message: `Action ${actionType} completed for ${entityId}`,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      success: false,
      code: 'ERR_WEB_OPERATION_FAILED',
      message: error instanceof Error ? error.message : 'Unknown server error',
      timestamp: new Date().toISOString(),
    };
  }
}
```
