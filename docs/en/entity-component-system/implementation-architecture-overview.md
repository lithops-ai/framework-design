# Implementation Architecture Overview

!!! note
    This is just a tentative design.

This document discusses a number of approaches
for implementing large-scale,
distributed and decentralized entity-component systems.

Currently, we take the third approach,
i.e., runtime component injection.

## Special Challenges with Distributed ECS

Since Lithops implements distributed, large scale entity-component system,
there are some unique challenges that do not arise in general game development.

### Error Handling

Lithops ECS is designed to be high-available and fault-tolerant.
bugs or null reference errors on an actor/component must not crash the entire system.

### Concurrency

Concurrency is an issue rarely encountered in game development,
because mainstream game engines are generally single-threaded
(known as the game thread).
Despite the performance issues,
this is a deliberate design choice
that eliminates concurrency-specific concerns
for artists and game developers,
a population with generally no strong background
in software development and system programming.

However, large-scale distributed ECS systems are
inherently concurrent and asynchronous,
and it is unrealistic to employ a single-threaded approach
because the performance degradation would be unacceptable.

## Architecture Choices

There are several schemes to implement the Entity-Component-System (ECS) architecture.

### One Container Per Actor

This is the easiest scheme to think of.
In this scheme,
each actor is associated with a single container,
and all components in that actor are isolated in that container.

**Pros:**

- Each actor with its components is isolated,
and failure within one actor does not affect the others.
- There is minimal communication cost between multiple components on a single actor.

**Cons:**

- Even though the number of components is limited,
the number of possible combinations,
and hence the number of actor types,
can be potentially large.
If we were to create an image for each actor with a different set of components,
the number of docker images would blow up.
- Does not allow adding or removing components at runtime.
- Cannot handle very large actors because each actor must fit on one node.

### One Service Per Component

In this scheme,
each type of component is implemented as a service
which automatically load-balances across multiple nodes
as the number of actors using this component grows.
All actors using the same type of component
connects to the same service endpoint.

#### General Architecture

Physically, each type of component is exposed as a service
which may be deployed over one or multiple nodes.
The idea is, component services are guaranteed to be always available,
and scales automatically with the number of actors using them.

For example, consider a multi-agent system:

```mermaid
graph TD
    A1(Actor 1) --> C11(Component 1)
    A1 --> C12(Component 2)
    A2(Actor 2) --> C21(Component 1)
```

The implementation might look like:

```mermaid
graph TD
    A1(Actor 1) --> C1
    A2(Actor 2) --> C1
    A1 --> C2
    C1(Component 1 Service)
    C2(Component 2 Service)
    C1 --> N1(Node 1)
    C1 --> N2(Node 2)
    C2 --> N2
```

#### Component Service Implementation

To ensure isolation across different component instances,
each instance of a component is encapsulated in its own process.

**Pros:**

- Scales to large number of actors with different combinations of components.
- Allows dynamically adding and removing components
  after an actor is spawned (like in game engines).
- Scales well in situations where
there is a single actor so large it cannot fit on one machine,
as components in an actor are distributed
across multiple services and nodes in nature.

**Cons:**

- It can be hard to ensure isolation between
  different instances of the same component type
  attached to different actors,
  especially when those instances are deployed on the same node.
- Each inter-component event requires a round-trip over the cluster network,
  even for the components on the same actor.

### Runtime Component Injection

This scheme is similar to "One Container Per Actor",
in that each actor gets its own container.
The difference is that instead of creating an image
for each different combination of components,
there is only one image providing the basic functionalities
like event passing.
When an actor is spawn,
a container is created,
then the components are injected into the container.

The critical design choice with this architecture is
how to package the runtime code for each component.
Apparently, we want something more lightweight than a container
since the components are already running in a container.
May look into existing sandboxing solutions like snap and AppImage.

In general, the means of component packaging/virtualization should:

1. Be lightweight;
2. Ensure isolation between different components on the same actor.

**Pros:**

- Ensures isolation between different actors.
- Keeps the number of packages at a minimum
even when there are a large number of actors
with different combinations of components.
- Allows dynamically adding and removing components
after an actor is spawned (like in game engines).

**Cons:**

- The process of component injection can introduce unexpected bugs.
For example, if two components use the same temporary directory in the host container,
they may interfere with each other and cause unwanted behavior even if they have no bugs on their own.
- Cannot handle very large actors because each actor must fit on one node.

## Runtime Component Injection

Currently, we employ the runtime component injection approach
for implementing the ECS architecture.

The design ideas are:

- Components may be buggy so there needs to be
some sandboxing for each component.
- Component sandboxing should incur minimal overhead
since we're already inside a container.
- Components should be self-contained to
avoid dependency and environment configuration issues.

Specifically:

- Use AppImage to package each component into a self-contained binary.
- Use BubbleWrap to sandbox each component AppImage
and provide a safe, ephemeral mount point for it to write to,
similar to a Docker volume (expect that it does not persist).
Restrict AppImages from accessing the host filesystem
to avoid multiple components sharing the same file system and interfering with each other.
