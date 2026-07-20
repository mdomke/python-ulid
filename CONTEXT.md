# Domain Glossary & Context: python-ulid

Welcome to the architectural domain reference for the `python-ulid` project. This document outlines the ubiquitous language, core domain entities, and structural concepts of this implementation.

---

## Core Concepts & Vocabulary

### ULID
*   **Definition**: A Universally Unique Lexicographically Sortable Identifier.
*   **Format**: A 128-bit value consisting of:
    *   **Timestamp**: 48 bits, representing epoch time in milliseconds.
    *   **Randomness**: 80 bits, representing high-entropy random generation.
*   **Representation**: Encoded as a 26-character Base32 string.
*   **Nature**: Act as an immutable, hashable **Value Object**.

### ULIDGenerator
*   **Definition**: A deep, stateful generator responsible for orchestrating the creation of new `ULID` identifiers.
*   **Responsibilities**:
    *   Sampling system or injected clocks for the **Timestamp**.
    *   Sourcing entropy for the **Randomness**.
    *   Tracking state and enforcing **Monotonicity** rules.
    *   Guaranteeing thread-safe generation across execution contexts.

### Monotonicity
*   **Definition**: The deterministic ordering property where multiple ULID instances generated within the exact same millisecond increment their randomness component by $1$ to prevent sorting collisions.
*   **Friction**: Under heavy concurrent execution, generating more identifiers than the 80-bit randomness field allows in a single millisecond will raise an overflow error.

### Base32 Engine
*   **Definition**: Crockford's Base32 translation layer.
*   **Nature**: Encodes/decodes binary representation using a restricted alphabet of 32 characters (`0123456789ABCDEFGHJKMNPQRSTVWXYZ`), omitting ambiguous characters like `I`, `L`, `O`, and `U` to guarantee maximum readability.
