# Design Philosophy

Lithops is designed around a set of ideas and goals:
robustness & decentralized control,
separation of logical/physical construct
and flexibility.

## Robustness & Decentralization

Lithops deploys a large number of self-autonomous agents over a cluster.
There is no centralized control and the failure of one agent has minimal impact over the others.

## Separation of Logical/Physical Construct

In Lithops, the logical abstraction of a multi-agent system
and how it functions physically are decoupled.

## Flexibility

At its core, Lithops tries to introduce minimal inductive bias over how agents should be designed and how they behave.

Rather than a monolithic framework,
Lithops is a set of building blocks that can be composed to create a wide range of multi-agent systems.
Some of these building blocks may have assumptions of a certain aspect of agents,
and they may have dependency on other building blocks.
These building blocks may be considered subsystems or micro-frameworks;
they interact with each other according to protocols,
a concept similar to trait in Rust.
