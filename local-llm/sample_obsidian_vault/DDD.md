# Domain-Driven Design (DDD) Notes

## 🧠 What is Domain-Driven Design?

**Domain-Driven Design (DDD)** is a software design approach focused on modeling software based on the **business domain** it serves. It was introduced by **Eric Evans** in his book *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003).

### Core Goals

- Align software design with business goals and domain knowledge.
- Manage complexity by focusing on core domain logic.
- Encourage collaboration between domain experts and developers.

---

## 🗂️ Key Concepts

### 📦 Domain
The sphere of knowledge and activity around which the application logic revolves.

### 📘 Ubiquitous Language
A common language used by developers and domain experts within a **Bounded Context**, ensuring consistent communication and naming.

### 📏 Bounded Context
A boundary around a specific domain model, where terms, logic, and rules are consistent. Bounded contexts communicate via defined interfaces.

### 📦 Entities
- Objects with a unique identity and lifecycle.
- Example: `User`, `Order`, `Invoice`

### 📦 Value Objects
- Immutable objects with no identity.
- Represent descriptive aspects.
- Example: `Money`, `DateRange`, `Address`

### 📦 Aggregates
- A cluster of domain objects treated as a single unit.
- An **Aggregate Root** is the entry point to this cluster.
- Enforces invariants and transactional consistency.

### 🧩 Domain Events
- Describe something that happened in the domain.
- Help model side effects and enable eventual consistency.

### 🔧 Repositories
- Abstract storage for aggregates.
- Provide methods like `save()`, `findById()`.

### 🧠 Services
- Contain domain logic that doesn’t naturally fit into an entity or value object.
- Should be stateless.

---

## 🧱 Strategic Design

### Bounded Context Mapping

- Identify boundaries in the business and design independently evolving subsystems.
- Define **relationships** between contexts (e.g., Customer-Supplier, Conformist, Anti-Corruption Layer).

### Context Map Example:

| Context A        | Context B         | Relationship Type      |
|------------------|------------------|------------------------|
| Customer Portal  | Billing Service  | Customer-Supplier      |
| Inventory System | Fulfillment      | Conformist             |
| Legacy CRM       | New CRM Adapter  | Anti-Corruption Layer  |

---

## ⚙️ Applying DDD in Practice

### 1. Collaborate with domain experts
Use **Event Storming** or **Domain Storytelling** to explore the business domain.

### 2. Define a Ubiquitous Language
Ensure everyone—developers and non-technical stakeholders—uses consistent terms.

### 3. Design aggregates around transactional boundaries
Keep aggregates small and cohesive to reduce contention and complexity.

### 4. Implement bounded contexts in code
Use clear module/package boundaries, separate databases or microservices when appropriate.

---

## 🧠 Benefits

- Improves alignment between code and business goals
- Helps manage complex domains
- Promotes modular architecture and microservices

---

## 📚 Resources

- *Domain-Driven Design* by Eric Evans
- *Implementing Domain-Driven Design* by Vaughn Vernon
- [DDD Community Portal](https://dddcommunity.org/)
- [Domain Language](https://domainlanguage.com/)

