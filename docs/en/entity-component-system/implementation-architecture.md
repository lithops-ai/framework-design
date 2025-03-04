# Lithops Distributed ECS Implementation Architecture

This document discusses the high-level architecture
that Lithops employs to implement
large scale, distributed and decentralized entity-component systems.

## Architecture Overview

Lithops employs the runtime component injection architecture
for implementing distributed ECS
and adds an abstraction named "service"
for implementing API services that need load-balancing,
such as image generation.

There are four core concepts in the ECS architecture.

### Actor

Each actor with all its components runs as a container.
An actor is assumed to be relatively lightweight
and can fit on a single machine.

### Component

Each component runs as a self-contained, sandboxed package inside the actor container.
When an actor is spawned, the actor container is created,
then the component packages are pulled and run.

### Service

A service is a load-balanced API service endpoint
providing stateless, potentially heavily-depended API services,
such as text and image generation.

### Core Functionality Service

This is a core functionality service endpoint
(deployed and load-balanced automatically)
that all actors/components use
to access Lithops ECS core functionalities.

All communications, event passing and API calls
are proxied through this service.

## Actor API

The host image refers to the base image of the actor container.
This does not include any components but must provide syscall-like APIs
that the components use to implement their functionalities.

For the MVP, we provide a minimal set of APIs
that are used the most frequently in a well-structured game project:

- Get component by class (gets the first component of the given type);
- Find component by class and tag.

For reference, a tag is a semantic string
associated with either a component or an actor.
Each component or actor can have multiple tags.
In game development,
a component use tags to find
other components it depends on.

## Component SDK API

Component SDK API refers to the APIs that
component code uses to access
the syscall-like entity-component system core functionalities.

This includes:

- Sending and receiving events to/from other components,
either on the same or different actors.
- Calling exposed APIs on other components/services.

In Lithops, we organize such APIs in an object-oriented manner
similar to game engines.
Specifically:

- Component code can get handles to actors,
components or services.
- These handles expose APIs such as
sending events, binding event dispatchers
and calling APIs
(similar to calling public functions
on other actors/components in game engines).
- These handles automatically handle the cases where
actor/components fail and restart.

## Messaging & API Calls

Actors and components may use the core service to get handles,
but once that handle is acquired,
it accesses the handle directly if possible
and API calls are not proxied through the core service.

Such a calling mechanism have different semantic implications in different scenarios:

- In case of calling a service: Operation guaranteed to success,
since the service is inherently load-balanced and distributed.
- In case of calling a function on a component: Operation may fail or timeout,
since the component may be invalid (e.g., null reference or pending kill).
- In case of broadcasting an event:
Some of the listeners may be invalid and may not receive the event,
but the semantics of event broadcast is the same with that in game engines,
i.e., the event broadcaster does not care about who received the event or not.
