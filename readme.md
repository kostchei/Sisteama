# Sisteama

A modular system for orchestrating agentic workflows combining deterministic logic and AI models.

> First use case: **Tale Keeper** – a narrative engine and adjudicator for Dungeons & Dragons (5e/2024 rules), enabling character creation, adventure generation, and automated gameplay.

---

## Vision

**Sisteama** is a flexible framework designed to support AI-augmented, agent-based systems for structured, decision-driven tasks. It merges:

- 🧠 **Model Context Protocol (MCP)** — structured memory and scoped reasoning
- 🧭 **Agentic Flow** — composable steps with local agents
- ⚙️ **Deterministic Tools** — rulesets, validation, logic trees
- 🤖 **LLM-Aware Agents** — prompt-driven reasoning, storytelling, classification

The architecture is domain-agnostic. Our first case study is in the realm of **TTRPGs**: creating, guiding, and narrating tabletop adventures.

---

## Use Case: Tale Keeper (D&D Agent Flow)

**Tale Keeper** is the initial implementation of Sisteama. It supports:

- 📜 **Character Creation** — using JSON profiles, alignment, background, and mechanics
- 🧭 **Adventure Building** — procedural and authored story modules
- ⚔️ **Combat Adjudication** — rules-based combat flows with NPC/PC logic
- 🎲 **Skill Challenges** — group or individual checks with narrative outcome logic
- 📖 **Story Unfolding** — dynamic scene progression via agentic decision trees and prompt injection

It’s a system that acts like a co-DM or referee with memory.

---

## System Overview

```mermaid
flowchart TD
    A[User Input / Request] --> B[Agent Orchestrator]
    B --> C{Deterministic Tool?}
    C -- Yes --> D[Rule Engine / Game Logic]
    C -- No --> E[AI Agent / Prompt Chain]
    E --> F[Context Protocol (MCP)]
    D --> G[Response Builder]
    F --> G[Response Builder]
    G --> H[Output to User / Log]
