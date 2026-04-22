# Individual Report: Cloud Execution Models - Container and Serverless Hybrid Architecture

## Student ID: [REDACTED]

## Group ID: [REDACTED]

---

## 1. Introduction

This report documents my analysis and reflection on the design and implementation of a cloud-native application that combines container-based services with serverless functions. The project, titled "Creator Cloud Studio," implements an event poster submission system that demonstrates the hybrid execution model approach taught in the Comp3006J Cloud Computing course.

The primary objective of this mini-project was to understand how different cloud execution models can be strategically combined to build efficient, scalable, and cost-effective applications. Rather than applying a one-size-fits-all approach, the project required careful consideration of which components benefit most from containers versus serverless architectures.

---

## 2. System Architecture Overview

The implemented system follows a six-component architecture as specified in the project requirements. Each component was designed with specific responsibilities and deployed using the most appropriate execution model.

### 2.1 Container-Based Components

Three services were implemented as container-based applications using Docker:

**Presentation Service** serves as the user-facing interface. It accepts form submissions containing event title, description, and poster filename, then displays the final processing results. This service was chosen for containers because it requires persistent network connections, needs to serve web content with low latency, and benefits from maintaining session state during user interactions.

**Workflow Service** orchestrates the submission processing pipeline. It creates initial records, triggers background processing, and coordinates between other services. Containers are ideal here because this service maintains complex state during the workflow, needs to manage multiple API calls sequentially, and requires persistent connections to other services.

**Data Service** handles storage and retrieval of submission records. As a stateless service that simply stores and retrieves data, it could theoretically use either execution model. However, containers were chosen to provide consistent low-latency database operations and easier integration with the other services.

### 2.2 Serverless Components

Three functions were implemented using serverless architecture:

**Submission Event Function** is triggered when new submissions are created. It converts submission events into standardized processing requests. Serverless is ideal for this component because it is event-driven, has variable and unpredictable load patterns, and requires minimal compute resources.

**Processing Function** applies validation rules and computes submission results. This function is invoked frequently but executes quickly. Serverless architecture provides automatic scaling during peak submission periods while minimizing costs during quiet times.

**Result Update Function** updates stored records with computed results. Similar to the event function, this is an event-driven component with sporadic execution patterns that benefits from serverless scaling.

---

## 3. Execution Model Justification

The choice between containers and serverless functions was based on several key factors:

### 3.1 Container Selection Criteria

Containers were selected for components that exhibit the following characteristics:

- **Long-running processes**: Services that need to maintain persistent connections or run continuously benefit from containers' ability to run indefinitely without cold-start delays.

- **Stateful operations**: Components requiring session management or complex state transitions are easier to implement in containers with persistent memory.

- **Consistent resource patterns**: When resource usage is relatively predictable and steady, containers provide better cost efficiency than serverless functions.

- **Network dependencies**: Services that need to maintain persistent connections to other services or databases perform better as containers.

### 3.2 Serverless Selection Criteria

Serverless functions were selected for components that exhibit the following characteristics:

- **Event-driven triggers**: Functions that respond to specific events rather than continuous polling are natural fits for serverless architecture.

- **Variable and unpredictable load**: Components experiencing significant traffic variations benefit from serverless auto-scaling without pre-provisioning.

- **Short execution duration**: Functions that complete quickly (typically under a few seconds) maximize the cost efficiency of serverless billing models.

- **Infrequent invocation**: Components that may remain idle for extended periods avoid the resource waste of idle containers.

### 3.3 Design Trade-offs

The hybrid approach introduces some complexity compared to a pure-container or pure-serverless solution. Service orchestration becomes more complex when managing both execution models. Monitoring and debugging require different tools and approaches for containers versus functions. However, these challenges are offset by the optimization benefits of choosing the right tool for each component.

---

## 4. Processing Rules Implementation

The system implements three-tier validation logic as specified:

1. **INCOMPLETE Status**: Returned when any required field (title, description, or poster filename) is missing. This rule has highest priority and cannot be overridden by other conditions.

2. **NEEDS_REVISION Status**: Returned when all required fields are present but either the description contains fewer than 30 characters or the poster filename does not end with .jpg, .jpeg, or .png.

3. **READY Status**: Returned only when all validations pass—required fields present, description meets minimum length, and poster has valid image extension.

The Processing Function implements these rules with clear separation of concerns, ensuring each validation rule is applied independently and in the correct order.

---

## 5. Technical Implementation Details

### 5.1 Service Communication

The system uses RESTful API communication between containers. The Presentation Service accepts user input and forwards it to the Workflow Service, which orchestrates the processing pipeline. The Workflow Service triggers the serverless functions and updates the Data Service with results.

### 5.2 Serverless Function Simulation

For local development and testing, the serverless functions are simulated within the Workflow Service. In production, these would be deployed to cloud function services (AWS Lambda, Azure Functions, or Alibaba Cloud Function Compute) and triggered via event buses or direct invocations.

### 5.3 Data Storage

The Data Service uses in-memory storage for this implementation. Production deployments would typically use cloud databases such as PostgreSQL, MongoDB, or cloud-native storage services.

---

## 6. Learning Outcomes

Through this project, I gained deeper understanding of several cloud computing concepts:

**Architectural Decision Making**: Selecting between execution models requires analyzing each component's specific requirements rather than applying a uniform approach. The trade-offs between containers and serverless functions are nuanced and depend heavily on workload characteristics.

**Event-Driven Architecture**: Implementing the serverless components reinforced my understanding of event-driven patterns. The separation between event producers, processors, and result handlers demonstrates loose coupling benefits.

**Microservices Design**: The six-component architecture requires careful API design and clear component boundaries. Each service has well-defined responsibilities, making the system easier to understand, test, and maintain.

**Cloud Cost Optimization**: Understanding when serverless scaling benefits outweigh container cost efficiency helps in designing economically sustainable cloud applications.

---

## 7. Challenges and Solutions

One challenge was simulating serverless functions locally while maintaining architectural correctness. The solution was to implement the function logic in separate modules that can run both within the container workflow and as standalone serverless deployments.

Another challenge was ensuring all six components participated in the same workflow as required. This was addressed by explicit orchestration in the Workflow Service, which coordinates all function invocations.

---

## 8. Conclusion

This mini-project successfully demonstrated a hybrid cloud architecture combining containers and serverless functions. The Creator Cloud Studio application processes event poster submissions through a well-defined workflow, with each component deployed using the most appropriate execution model.

The key takeaway is that cloud architecture decisions should be driven by component-specific requirements rather than preference for a particular technology. Containers excel for persistent, stateful services with predictable resource needs, while serverless functions are optimal for event-driven, variable-load components. The hybrid approach enables optimization across multiple dimensions including cost, scalability, and development complexity.

---

## References

- Project Specification: Comp3006J Mini-Project 1 Guidelines
- Docker Documentation: https://docs.docker.com/
- AWS Lambda Documentation: https://docs.aws.amazon.com/lambda/
- Cloud Native Architecture Patterns

---

*Report generated for Comp3006J Cloud Computing course assessment.*
