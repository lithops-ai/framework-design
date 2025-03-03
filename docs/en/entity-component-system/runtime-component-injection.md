# Runtime Component Injection Architecture

This document discusses the high-level architecture
of runtime component injection,
an approach employed by Lithops to implement
large scale, distributed and decentralized entity-component systems.

## Architecture Overview

In runtime component injection:

- Each actor with all its components runs as a container;
- Each component runs as a self-contained, sandboxed package inside the actor container.
- When an actor is spawned, the actor container is created,
then the component packages are pulled and run.

## Host Image API

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
- Calling exposed APIs from other components.

In Lithops, we organize such APIs in an object-oriented manner
similar to game engines.
Specifically:

- Component code can get handles to actors or components.
- These handles expose APIs such as
sending events, binding event dispatchers
and calling APIs
(similar to calling public functions
on other actors/components in game engines).
- These handles automatically handle the cases where
actor/components fail and restart.
