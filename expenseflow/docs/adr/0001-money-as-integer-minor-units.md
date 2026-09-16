# ADR 0001: Store money as integer minor units

## Status

Accepted.

## Context

ExpenseFlow stores and moves monetary amounts (`amount_minor`, `amount_base_minor`) between the database, the API, and the UI. We needed a single representation used everywhere, chosen before any endpoint was written.

## Decision

All monetary amounts are stored and transmitted as **integers in minor currency units** (e.g. paise for INR, cents for USD) — never as floating-point numbers. `amount_minor` is the amount as submitted in its original `currency`; `amount_base_minor` is the same amount normalised to the base currency (INR). Conversion to a human-readable decimal amount (dividing by 100) happens only at the UI display layer, and never round-trips back into storage.

## Alternatives considered

- **Floating-point (`float`/`double`) amounts.** Rejected: binary floating-point cannot represent most decimal fractions exactly (e.g. `0.1 + 0.2 != 0.3`), which silently corrupts money values after repeated arithmetic — unacceptable for anything approval-related.
- **Fixed-point / `Decimal` type end-to-end**, including over the wire in JSON. Rejected for this PoC: JSON has no native decimal type, so `Decimal` values still serialize as either strings (extra parsing burden on every client) or floats (reintroducing the same problem). Integers are simpler and unambiguous across the API boundary.
- **Store as a string** (e.g. `"25.00"`). Rejected: pushes parsing and validation into every consumer and every language binding, with no arithmetic safety gained over integers.

## Consequences

- Every arithmetic operation on money (this PoC currently does none beyond the FX stub) works with plain integers, so it is exact.
- Every display surface (the Streamlit UI, any future report) must remember to divide by 100 and format with two decimals; this is a manual convention, not enforced by the type system. A missed conversion would display an amount 100x too large — this is the main risk of the decision and needs a code-review discipline or a shared formatting helper if the UI surface grows.
- The API contract requires clients to know the amount is in minor units; this must be documented (see `README.md`), since a naive client could otherwise multiply or divide incorrectly.
- Multi-currency arithmetic (e.g. summing amounts across currencies) is only valid on `amount_base_minor`, never on `amount_minor` directly, since the latter is currency-specific.
