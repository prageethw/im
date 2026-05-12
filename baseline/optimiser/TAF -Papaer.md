
# Why TM Forum Needs Both specCharacteristic and specExpression

**Document Type:** Technical Architecture Framework (TAF) Position Paper  
**Domain:** TM Forum Open APIs — Catalogue and Intent Models  
**Audience:** Solution Architects and API Designers  
**Language:** Australian English  

---

## Overview

Within TM Forum's Open API framework, two constructs are commonly encountered when 
modelling the properties and behaviours of a specification: `specCharacteristic` and 
`specExpression`. At first glance, they may appear redundant — both are ways of describing 
something about a specification. In practice, however, they serve fundamentally different 
purposes and neither can substitute for the other.

This paper explains what each construct does, why both are necessary, and what breaks if 
either is removed.

---

## Understanding the Two Constructs

### specCharacteristic — The Data Definition

`specCharacteristic` is the structural building block of any TM Forum specification. It 
defines the *named attributes* that a product, service, or resource specification exposes 
to consuming systems and end users.

Each `specCharacteristic` entry formally describes:

- The **name** of the attribute (e.g., `bandwidth`, `accessType`, `latencyClass`)
- The **data type** (e.g., string, integer, boolean, object)
- The **allowed values**, value ranges, or regex constraints
- Whether the attribute is **configurable**, **derived**, or **read-only**
- The **cardinality** (mandatory, optional, multi-valued)

This information acts as the *schema* or *vocabulary* of the specification. It tells 
downstream systems — ordering engines, inventory stores, UI renderers, and validation 
services — what data fields exist and what form they must take.

### specExpression — The Behavioural Logic

`specExpression` is the construct used when a specification needs to express formal, 
executable logic that goes beyond simply naming an attribute. This includes:

- **Derived value formulas** (e.g., total cost = unit price × quantity)
- **Cross-attribute constraints** (e.g., "If `bandwidth` > 500 Mbps, then `accessType` 
  must equal Fibre")
- **Intent statements** in the TM Forum intent model (TMF921 / TR290), where an expression 
  holds the machine-readable intent that the Intent Management API must evaluate and enforce
- **Dynamic validation rules** that cannot be captured by a simple allowed-values list

`specExpression` requires an expression language (such as OCL, FEEL, or a custom DSL) and 
carries an `expressionValue` that the expression engine evaluates at runtime.

---

## Why Both Are Needed

The relationship between the two constructs is one of **dependency, not duplication**. 
`specExpression` does not define data — it operates on data. And that data must first be 
formally declared via `specCharacteristic`.

### The Noun–Verb Analogy

A useful way to think about the relationship:

- `specCharacteristic` is the **noun** — it defines *what exists*.
- `specExpression` is the **verb** — it defines *what to do with what exists*.

You cannot write a functional sentence using only verbs. An expression that references 
`bandwidth` or `latencyClass` can only be evaluated if those attributes have been formally 
declared with a type, cardinality, and value domain. Without the characteristic definition, 
the expression engine has no schema to bind the logic to.

### The Vocabulary Problem

If `specCharacteristic` is removed, an expression such as:

> "If `bandwidth` > 500 and `serviceClass` == 'Premium', enforce SLA tier A"

…becomes unexecutable. The system no longer knows:

- Whether `bandwidth` is a number or a string
- What the allowed values of `serviceClass` are
- Whether either attribute is even part of the specification payload

The expression engine would be attempting to evaluate logic against a completely undefined 
data model.

---

## Consequences of Dropping specCharacteristic

| Domain | Impact if specCharacteristic is Removed |
|---|---|
| **Product / Service / Resource Catalogue** (TMF620, TMF633, TMF634) | Catalogue APIs cannot advertise what attributes a specification has. Consumers have no way to know what data to submit. |
| **UI and CPQ Systems** | Frontends read `specCharacteristic` to dynamically generate input fields, drop-downs, and validation messages. Without it, every UI must be hardcoded per product. |
| **Order Management** (TMF622) | Ordering systems cannot validate whether the submitted characteristic payload conforms to the specification. Invalid or missing data passes unchecked into fulfilment. |
| **Inventory** (TMF638, TMF639, TMF634) | Inventory instances carry `characteristic` values derived from `specCharacteristic`. Without the spec-level definition, instance data has no schema to validate against. |
| **Intent Management** (TMF921, TR290) | `specExpression` entries lose their variable vocabulary. Expressions that reference spec attributes cannot be bound or evaluated. |
| **EAV Extensibility Pattern** | The entire Entity-Attribute-Value extensibility pattern that allows organisations to add custom fields without changing core API schemas collapses. |

---

## Consequences of Dropping specExpression

For completeness, it is worth noting what is lost if `specExpression` is dropped while 
retaining `specCharacteristic`:

- **Static catalogues only:** The model can define what attributes exist and what values 
  they may take, but it cannot express any dependencies, derivations, or conditional 
  constraints between them.
- **Intent models break entirely:** TMF's intent model (TR290 / TMF921) is built around 
  the concept that an Intent carries a formal, evaluable `expression`. Without 
  `specExpression`, there is no way to represent intent semantics in a machine-processable 
  form.
- **Complex validation is lost:** Rules such as "bandwidth and SLA tier must be consistent 
  with each other" cannot be enforced at the specification layer. These constraints must be 
  pushed into custom backend code outside the standard model.

---

## The Complementary Architecture

The two constructs form a layered architecture:

