# Logical Abstraction

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

## Actor Discovery

Actor discovery refers to how an actor finds other actors it needs to reference.
For finding "global actors" such as API services and user interface component,
we provide a tagging mechanism similar to those find in Unity and Unreal, where:

- Each actor can have a bunch of tags.
- There is a system-wide service for finding actor/actors with a specific tag.

## Actor Virtualization

Actors are virtualized and automatically restarted/repaired
on any non-intentional failures such as network disconnection or machine failures.
From the user's perspective,
actors are always alive and available unless intentionally destroyed.

## Examples

For a better understanding of the ECS architecture,
let's look at some examples.
Consider a simple multi-agent system that develops software
from specification provided by the user.
This system consists of the following actors:

- A frontend for interacting with the user.
  Components:
    - A "UserSoftwareSpecInput" component that exposes an event dispatcher
      which fires whenever the user submits a new software development request.
    - A "ReportOnDevComplete" component
      that reports to the user when a
      software development goal completion event
      (exposed by the LLMGoalFinisher component)
      is fired.
- A software developer agent for building software.
  Components:
    - An "LLMGoalFinisher" component representing the agent's brain.
      This component takes a goal, produces a plan and executes it.
      During goal execution, it may call other tools.
      This component exposes an event dispatcher to be fired
      when the development of a software is complete.
    - A "ForwardGoal" component that sets the goal of LLMGoalFinisher component
      whenever the user inputs a software development request.
- A compiler service that takes the source code and outputs the compiled binary.
  Components:
    - A "CompilerService" component that exposes a software compilation API.


