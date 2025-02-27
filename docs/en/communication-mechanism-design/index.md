# Lithops - Communication Mechanism Design

## 1. Goals and Background

1. In large-scale distributed applications, it is necessary to provide a "real-time communication + topic/subtopic" based collaborative model for millions of dispersed Agents (deployed across cloud, edge, IoT devices, etc.).
2. The goal is to enable Agents to interact hierarchically through a "Discord-like" user experience, structured around “Channel-Thread-Message,” while supporting access control, group management, attachment handling, message history tracking, and other features.
3. Within cloud-native ecosystems, the solution should leverage Kubernetes CRD + Operator to achieve declarative configuration and fully automated operations. However, it must avoid mapping millions of Agent identities or messages directly onto etcd to minimize overloading the Kubernetes control plane.

## 2. High-Level Architecture

To ensure high concurrency and scalability, the system is divided into the following core components:

1. **Kubernetes API Server / etcd**
   - Only stores essential metadata such as "Channels/Threads" (as CRDs) and small summaries like "Groups" or access control information.
   - Does not store millions of Agent identities or message histories.

2. **Message Queue System (MQ)**
   - Systems like NATS, RabbitMQ, Kafka, etc., are used to handle large-scale, real-time, high-throughput message distribution.
   - Each Channel or Thread corresponds to a Subject/Topic/Queue in the MQ system, enabling isolation similar to "Discord Channels-Threads."

3. **CollaborationPolicyService (External Identity + Access Control Management)**
   - An independent service that manages Agent identities (IDs), Groups, and Role information, as well as access control policies for collaboration scenarios. 
   - Operators and the MQ system consult this service to verify Agent permissions for Channels/Threads; simultaneously, Agent clients must authenticate through this service before connecting.

4. **Channel/Thread Operator**
   - Monitors Channel and Thread CRDs defined in Kubernetes, automating the creation and update of their corresponding topics/routing policies in the MQ system.
   - Interacts with CollaborationPolicyService to grant/revoke group access to Channels/Threads without creating a large number of RoleBindings in Kubernetes.

5. **Agents (Millions of Instances)**
   - Deployed on cloud or edge nodes, these connect to the MQ system via SDKs or APIs to publish and subscribe to messages, enabling collaborative interaction.
   - Before connecting, Agents authenticate with the CollaborationPolicyService to receive certificates or tokens, enabling their access to specific Channels/Threads.

## 3. Key Requirements and Challenges

1. **Massive Scale & Multi-Agent Concurrency**
   - Millions of Agents need to communicate simultaneously, publishing/subscribing to messages with high-speed. Traditional monolithic systems are inadequate for this scale.
   
2. **Hierarchical Access Control**
   - Different Agents possess different roles (e.g., Owner, Moderator, Member), but each Agent's role cannot be mapped into Kubernetes RoleBindings. Access control must be externalized.

3. **Real-Time Messaging and History**
   - Similar to a “Discord-like” system, the platform must deliver low-latency message distribution while supporting searchable and replayable message history in Channels/Threads.

4. **Cloud-Native Scalability**
   - The system should seamlessly scale within Kubernetes, leveraging Operators for fully automated operations, minimizing the need for manual management of message middleware configurations.

## 4. Logical Layer Design

### 4.1 Core Concepts

1. **Channel**
   - Represents a discussion space for a group, topic, or major task, which can be public or private.
   - Configurable attributes include visibility (public/private), read/write policies, persistence options, etc.
   - Most Agents do not directly interact with Kubernetes; instead, they depend on the CollaborationPolicyService to determine whether they can “join” a given Channel.

2. **Thread**
   - A sub-discussion space within a Channel, inheriting or defining separate access permissions.
   - Helps segregate and focus discussions to avoid overwhelming the main Channel.

3. **Message**
   - The core communication unit containing text, attachments, mentions, etc.
   - Messaging payloads are not recommended for storage in etcd. Instead, MQ or external databases should handle them for real-time processing and historical storage.

4. **Mentions**
   - For example, “@AgentX” or “@Group,” enabling priority notifications or targeted pushing via MQ.
   - CollaborationPolicyService resolves aliases into actual Agent IDs.

5. **Roles**
   - Owner: Manages Channel configurations, adds/removes groups.
   - Moderator: Can administratively block specific groups or Agents (maintained through the CollaborationPolicyService).
   - Member: Regular participants sending/receiving messages in Channels.
   - Roles are handled exclusively in CollaborationPolicyService—not within Kubernetes itself.

## 5. Implementation Details

### 5.1 Simplified CRD Design

#### 5.1.1 Channel CRD

> Instead of maintaining RoleBinding for every individual Agent, it only contains minimal group-based metadata.

```yaml
apiVersion: agents.platform.io/v1
kind: Channel
metadata:
  name: sensor-anomaly-channel
spec:
  visibility: "private"  # Other values: "public"
  authorizedGroups:
    - "EdgeSensorsGroup"
    - "MLWorkersGroup"
  enablePersistence: true    # Enables historical storage in MQ
  retentionPolicy: "7d"      # Operator parses this field
status:
  natsSubject: "channels.sensors.anomaly"
  state: "Active"
```

#### 5.1.2 Thread CRD

```yaml
apiVersion: agents.platform.io/v1
kind: Thread
metadata:
  name: anomaly-subanalysis
spec:
  channel: "sensor-anomaly-channel"
  participantsGroups:
    - "AnomalyFocusedGroup"  # Can inherit from parent Channel or define separately
  topic: "Sensor anomalies sub-thread"
status:
  natsSubject: "channels.sensors.anomaly.thread-xyz"
  state: "Ongoing"
```

### 5.2 Operators

#### 5.2.1 Channel Operator

1. **Monitoring** Channel CRDs for Create/Update/Delete operations.
2. **On detecting a new Channel**:
   - Use MQ APIs (e.g., NATS Admin) to create a corresponding topic (Subject/Topic/Queue).
   - Update the authorization policies in CollaborationPolicyService for designated `authorizedGroups`.
   - Adhere to `enablePersistence` and `retentionPolicy` to configure MQ persistence policies.
   
3. **On Channel Updates**:
   - Adjust CollaborationPolicyService permissions if `authorizedGroups` are modified.
   - Update MQ persistence policies if `enablePersistence` or `retentionPolicy` changes.
   
4. **On Channel Deletion**:
   - Mark the MQ topic for archival or cleanup. Physically delete the topic after a delay (optional).
   - Revoke associated authorizations in CollaborationPolicyService.

#### 5.2.2 Thread Operator

1. **Monitoring** Thread CRDs for CRUD events.
2. Logic mirrors that of the Channel Operator:
   - Create sub-topics in MQ for Threads.
   - Update permitted `participantsGroups` or inherit them from the parent Channel.
   
3. When Threads are archived or deleted:
   - Remove related sub-topics from the MQ and adjust retention policies accordingly.

### 5.3 CollaborationPolicyService

- An independent external or microservice-based system that leverages specialized databases (Postgres, Redis, NoSQL, etc.) to store identity, group, and role information for millions of Agents. 
- Exposes APIs like `CheckPermission(AgentID, Subject)` and `UpdateChannelAuth(ChannelID, GroupList)` for use by Operators and MQ systems alike.
- Before an Agent attempts to join any Channel, it undergoes authentication and, upon success, receives an MQ access token allowing it to communicate securely.

### 5.4 MQ Selection and Configuration

Let’s take NATS as an example (alternatives include RabbitMQ or Kafka):

1. **NATS on Kubernetes**:  
   - Deploy NATS using a Kubernetes NATS Operator for automated scaling and failover.

2. **Subject Naming Convention**:  
   - Tie Subjects to CRDs, e.g., `channels.<channelName>.threads.<threadName>`.

3. **JetStream Persistence**:  
   - With persistence enabled, set up JetStream to manage histories via automatic Message Replay mechanisms.

4. **ACL and Security**:  
   - Utilize NATS multi-tenant or Account-based ACL management. Allow group-specific tokens via CollaborationPolicyService, enabling secure logins.

## 6. Typical Messaging Workflow Example

1. **Channel Creation**:
   - An Administrator submits a `Channel` CRD (“sensor-anomaly-channel”), specifying `authorizedGroups = [“EdgeSensorsGroup”, “MLWorkersGroup”]`.
   - The Channel Operator:
     - Creates a matching NATS Subject, “channels.sensors.anomaly.”
     - Updates CollaborationPolicyService to grant `EdgeSensorsGroup` and `MLWorkersGroup` access.

2. **Agent Joins & Sends Messages**:
   - AgentX (part of EdgeSensorsGroup) authenticates with CollaborationPolicyService and receives a token for “channels.sensors.anomaly.”
   - AgentX subscribes to the topic and pushes anomaly detection messages.

3. **Thread Creation**:
   - To deep-dive into details, a Thread CRD is created for a sub-topic (“anomaly-subanalysis”).
   - Thread Operator provisions the NATS sub-channel and updates permissions.

4. **Historical Replay**:
   - If JetStream persistence is enabled, Agents can replay historical messages, or archival tasks can operate seamlessly.

## 7. Advantages and Value

1. **Scalability**:
   - Offloads identity and message management to external systems, keeping etcd and Kubernetes Control Plane lightweight.

2. **Cloud-Native Integration**:
   - Stays declarative, leveraging Kubernetes Operators to seamlessly integrate with CRDs and external services.

3. **Flexibility**:
   - MQ (NATS, Kafka, etc.) and CollaborationPolicyService implementations are modular—easy to swap or customize.

4. **Discord-like Experience**:
   - Fully supports Channels, Threads, Mentions, message searchability, and hierarchical permissions.

5. **Future Expansion**:
   - Extensible for advanced integrations, such as embedding LLMService Operators in the future.

## 8. Conclusion

This design leverages Kubernetes CRDs and Operators to declaratively automate “Channel/Thread” management while offloading large-scale identity/auth and message processing to external systems (CollaborationPolicyService + MQ).  
This approach reduces Kubernetes control-plane dependency and delivers high scalability, paving the way for a “Discord-like” system for multi-Agent communication. Future extensions (e.g., AI/LLM-based collaboration) can easily integrate into this architecture, maintaining a unified cloud-native operations model.
