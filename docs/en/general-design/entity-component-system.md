# Entity Component System

## Entity Component System Overview

Lithops employs an entity-component-system (ECS) style architecture.

In this architecture, everything in a multi-agent system
is abstracted as an **actor**.
This includes agents capable of critical thinking,
frontend that interacts with the user,
and even API services.

An actor on its own does not do anything useful;
its behavior is defined by the **components** attached to it.

A component is a reusable piece of logic
that adds a certain behavior to an actor.

## Communication

Actors and components communicate through events.
Components may expose event dispatchers
for other components from either the same or another actor to bind to.
Of course, API calls are also supported;
a component can call an exposed API from other components
to process data or to invoke certain behavior.

## Persistent Actors



## Examples

For a better understanding of the ECS architecture,
let's look at some examples.
Consider a simple multi-agent system that develops software
from specification provided by the user.
This system consists of the following actors:

- A frontend for interacting with the user.
  Components:
  - A "UserSoftwareSpecInput" component
- A software developer agent for building software.
  Components:
  - An "LLMGoalFinisher" component representing the agent's brain.
    This component takes a goal, produces a plan and executes it.
    During goal execution, it may call other tools.
  - A "ForwardGoal" component that periodically checks the user input
    via API service
- A compiler service that takes the source code and outputs the compiled binary.


