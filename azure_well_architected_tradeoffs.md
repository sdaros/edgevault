# Azure Well-Architected Framework: Pillar Tradeoffs

A comprehensive collection of tradeoff considerations across all five pillars of the Azure Well-Architected Framework.

## Table of Contents

1. [Reliability Tradeoffs](#reliability-tradeoffs)
2. [Security Tradeoffs](#security-tradeoffs)
3. [Cost Optimization Tradeoffs](#cost-optimization-tradeoffs)
4. [Operational Excellence Tradeoffs](#operational-excellence-tradeoffs)
5. [Performance Efficiency Tradeoffs](#performance-efficiency-tradeoffs)

---


## Reliability Tradeoffs

# Reliability tradeoffs - Microsoft Azure Well-Architected Framework | Microsoft Learn

**Source:** https://learn.microsoft.com/en-us/azure/well-architected/reliability/tradeoffs

**Documentation:** Azure Well-Architected Framework

---

Table of contents 

Exit editor mode

Ask Learn

Ask Learn

Focus mode

Table of contents
[Read in English](#)

Add

Add to plan
[Edit](https://github.com/MicrosoftDocs/well-architected/blob/main/well-architected/reliability/tradeoffs.md)

---

#### Share via

[Facebook](#)
[x.com](#)
[LinkedIn](#)
[Email](#)

---

Print

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Reliability tradeoffs

Feedback

Summarize this article for me

A reliable workload consistently meets its defined reliability objectives. It should reach established resiliency targets, ideally by circumventing events that affect reliability. Realistically, however, a workload must tolerate and control the impact of such events and maintain operations at a predetermined level during active malfunction. Even during a disaster, a reliable workload must recover to a specific state within a given period of time, both of which are agreed upon among the stakeholders. An incident response plan that enables you to achieve rapid detection and recovery is vital.

During the design phase of a workload, you need to consider how decisions based on the [Reliability design principles](principles) and the recommendations in the [Design review checklist for Reliability](checklist) might influence the goals and optimizations of other pillars. Certain decisions might benefit some pillars but constitute a tradeoff for others. This article describes example tradeoffs that a workload team might encounter when designing workload architecture and operations for reliability.

## Reliability tradeoffs with Security

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased workload surface area.** The Security pillar prioritizes a reduced and contained surface area to minimize attack vectors and reduce the management of security controls.

* Reliability is often obtained through replication. Replication can occur at the component level, at the data level, or even at a geographic level. Replicas, by design, increase the surface area of a workload. From a security perspective, a reduced and contained surface area is preferred to minimize potential attack vectors and streamline the management of security controls.
* Similarly, disaster recovery solutions, like backups, increase a workload's surface area. However, they're often isolated from the workload's runtime. These solutions require the implementation of additional security controls, which might be specific to the disaster recovery approach.
* For the sake of reliability goals, additional components might be needed for the architecture, which increases the surface area. For example, a message bus might be added to make requests resilient through decoupling. This increased complexity increases the surface area of the workload by adding new components that need to be secured, possibly in ways that aren't already used in the system. Typically, these components are accompanied by additional code and libraries to support their use or general reliability patterns, which also increases application surface area.

> ![](../_images/trade-off.svg)
> **Tradeoff: Security control bypass.** The Security pillar recommends that all controls remain active in both normal and stressed systems.

* When a workload is experiencing a reliability event that's being addressed under active incident response, urgency might create pressure for workload teams to bypass security controls that are optimized for routine access.
* Troubleshooting activities can cause the team to temporary disable security protocols, leaving an already stressed system potentially exposed to additional security risks. There's also a risk that the security protocols won't be reestablished promptly.
* Granular implementations of security controls, like custom role-based access control assignments or narrow firewall rules, introduce configuration complexity and sensitivity, increasing the chance for misconfiguration. Mitigating this potential reliability impact by using broad rules erodes all three Zero Trust architecture principles.

> ![](../_images/trade-off.svg)
> **Tradeoff: Old software versions.** The Security pillar encourages a "get current, stay current" approach to vendor security patches.

* Applying security patches or software updates can potentially disrupt the target component, causing unavailability during the software change. Delaying or avoiding patching might avoid the potential reliability risks, but it leaves the system unprotected against evolving threats.
* The preceding consideration also applies to the workload's code. For example, it applies to application code that uses old libraries and containers that use old base images. If updating and deploying application code is viewed as an unmitigated reliability risk, the application is exposed to additional security risks over time.

## Reliability tradeoffs with Cost Optimization

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased implementation redundancy or waste.** A cost-optimized workload minimizes underutilized resources and avoids over-provisioning resources.

* Replication is a key strategy for reliability. Specifically, the strategy is to have enough replication to handle a given number of concurrent node failures. The tolerance for more concurrent node failures requires a higher replica count, which leads to increased costs.
* Over-provisioning is another technique for absorbing unexpected load on a system, such as during a failover event, that could otherwise lead to a reliability issue. Any excess capacity that's not utilized is considered wasteful.
* If a workload uses a disaster recovery solution that excessively satisfies the workload's recovery point and time objectives, the excess leads to higher costs because of waste.
* Workload deployments themselves are a potential source for reliability impact, and that impact is often mitigated by redundancy at deployment time via a deployment strategy like blue/green. This transient duplication of resources during safe deployment typically increases the overall cost of the workload during those periods. Costs increase with frequency of deployments.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased investment in operations that aren't aligned with functional requirements.** One approach to cost optimization is evaluating the value that's provided by any deployed solution.

* To achieve reliability, a system requires observability. Monitoring systems require observability data transfer and collection. As monitoring capabilities increase, the frequency and volume of data increase, leading to additional costs.
* Reliability affordances in workloads necessitate testing and drills. Designing and running tests takes time and potentially specialized tooling, which incurs costs.
* Workloads with high reliability targets often have a rapid response process that requires technical team members to be part of a formal on-call rotation. This process incurs additional personnel costs and lost opportunity costs because of attention that could be directed elsewhere. It also incurs potential tooling costs for management of the process.
* Support contracts with technology providers are a key component of a reliable workload. Support contracts that aren't utilized because the level of support is over-provisioned incur waste.

## Reliability tradeoffs with Operational Excellence

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased operational complexity.** Operational Excellence, like Reliability itself, prioritizes simplicity.

* Reliability usually increases the complexity of a workload. As the complexity of a workload increases, the operational elements of the workload can also increase to support the added components and processes in terms of deployment coordination and configuration surface area.
* Having a comprehensive monitoring strategy for a workload is a key part of operational excellence. Introducing additional components into an architecture to implement reliability design patterns results in more data sources to manage, increasing the complexity of implementing distributed tracing and observability.
* Using multiple regions to overcome single region resource capacity constraints and/or implement an active/active architecture increases the complexity of the workload's operational management. This complexity is introduced by the need to manage multiple regions and the need to manage the data replication between them.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased effort to generate team knowledge and awareness.** The Operational Excellence pillar recommends keeping and maintaining a documentation repository for procedures and topologies.

* As a workload becomes more robust through the addition of reliability components and patterns, it takes more time to maintain operational procedures and artifact documentation.
* Training becomes more complex as the number of components in the workload increases. This complexity affects the time required for onboarding. The complexity also increases the knowledge that's needed to track product roadmaps and the latest service-level guidance.

## Reliability tradeoffs with Performance Efficiency

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased latency.** Performance Efficiency requires a system to achieve performance targets for user and data flows.

* Reliability patterns often incorporate data replication to survive replica malfunction. Replication introduces additional latency for reliable data-write operations, which consumes a part of the performance budget for a specific user or data flow.
* Reliability sometimes employs various forms of resource balancing to distribute or redistribute load to healthy replicas. A dedicated component that's used for balancing usually affects the performance of the request or process that's being balanced.
* Distributing components across geographical boundaries or availability zones to survive a scoped impact introduces network latency in the communication between components that span those availability boundaries.
* Extensive processes are used to observe the health of a workload. Although monitoring is critical for reliability, instrumentation can affect system performance. As observability increases, performance might decrease.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased over-provisioning.** The Performance Efficiency pillar discourages over-provisioning, instead recommending the use of just enough resources to satisfy demand.

* Automatic scaling operations aren't instantaneous and therefore can't reliably handle a sudden and dramatic spike in demand that can't be shaped or smoothed. Therefore, over-provisioning via either larger instances or more instances is a critical reliability tactic to account for the lag between demand signal and supply creation to help absorb bursts. Unused capacity counters the goals of performance efficiency.
* Sometimes a component can't be scaled in reaction to demand, and that demand isn't fully predictable. Using large instances to cover the worst case leads to over-provisioning waste in situations that are outside that use case.

## Related links

Explore the tradeoffs for the other pillars:

* [Security tradeoffs](../security/tradeoffs)
* [Cost Optimization tradeoffs](../cost-optimization/tradeoffs)
* [Operational Excellence tradeoffs](../operational-excellence/tradeoffs)
* [Performance Efficiency tradeoffs](../performance-efficiency/tradeoffs)

---

## Feedback

Was this page helpful?

Yes

No

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Ask Learn

Ask Learn

 Suggest a fix?

---

## Additional resources

---

* Last updated on 
  2024-10-10
---

## Security Tradeoffs

# Security tradeoffs - Microsoft Azure Well-Architected Framework | Microsoft Learn

**Source:** https://learn.microsoft.com/en-us/azure/well-architected/security/tradeoffs

**Documentation:** Azure Well-Architected Framework

---

Table of contents 

Exit editor mode

Ask Learn

Ask Learn

Focus mode

Table of contents
[Read in English](#)

Add

Add to plan
[Edit](https://github.com/MicrosoftDocs/well-architected/blob/main/well-architected/security/tradeoffs.md)

---

#### Share via

[Facebook](#)
[x.com](#)
[LinkedIn](#)
[Email](#)

---

Print

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Security tradeoffs

Feedback

Summarize this article for me

Security provides confidentiality, integrity, and availability assurances of a workload's system and its users' data. Security controls are required for the workload and for the software development and operational components of the system. When teams design and operate a workload, they can almost never compromise on security controls.

During the design phase of a workload, it's important to consider how decisions based on the [Security design principles](principles) and the recommendations in the [Design review checklist for Security](checklist) might influence the goals and optimizations of other pillars. Certain security decisions might benefit some pillars but constitute tradeoffs for others. This article describes example tradeoffs that a workload team might encounter when establishing security assurances.

## Security tradeoffs with Reliability

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased complexity.** The Reliability pillar prioritizes simplicity and recommends that points of failure are minimized.

* Some security controls can increase the risk of misconfiguration, which can lead to service disruption. Examples of security controls that can introduce misconfiguration include network traffic rules, identity providers, virus scanning exclusions, and role-based or attribute-based access control assignments.
* Increased segmentation usually results in a more complex environment in terms of resource and network topology and operator access. This complexity can lead to more points of failure in processes and in workload execution.
* Workload security tooling is often incorporated into many layers of a workload's architecture, operations, and runtime requirements. These tools might affect resiliency, availability, and capacity planning. Failure to account for limitations in the tooling can lead to a reliability event, like SNAT port exhaustion on an egress firewall.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased critical dependencies.** The Reliability pillar recommends minimizing critical dependencies. A workload that minimizes critical dependencies, especially external ones, has more control over its points of failure.

The Security pillar requires a workload to explicitly verify identities and actions. Verification occurs via critical dependencies on key security components. If those components aren't available or if they malfunction, verification might not complete. This failure puts the workload in a degraded state. Some examples of these critical single-point-of-failure dependencies are:

* Ingress and egress firewalls.
* Certificate revocation lists.
* Accurate system time provided by a Network Time Protocol (NTP) server.
* Identity providers, like Microsoft Entra ID.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased complexity of disaster recovery.** A workload must reliably recover from all forms of disaster.

* Security controls might affect recovery time objectives. This effect can be caused by the additional steps that are needed to decrypt backed up data or by operational access delays created by site reliability triage.
* Security controls themselves, for example secret vaults and their contents or edge DDoS protection, need to be part of the disaster recovery plan of the workload and must be validated via recovery drills.
* Security or compliance requirements might limit data residency options or access control restrictions for backups, potentially further complicating recovery by segmenting even offline replicas.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased rate of change.** A workload that experiences runtime change is exposed to more risk of reliability impact due to that change.

* Stricter patching and update policies lead to more changes in a workload's production environment. This change comes from sources like these:

  + Application code being released more frequently because of updates to libraries or updates to base container images
  + Increased routine patching of operating systems
  + Staying current with versioned applications or data platforms
  + Applying vendor patches to software in the environment
* Rotation activities for keys, service principal credentials, and certificates increase the risk of transient issues due to the timing of the rotation and clients using the new value.

## Security tradeoffs with Cost Optimization

> ![](../_images/trade-off.svg)
> **Tradeoff: Additional infrastructure.** One approach to cost optimizing a workload is to look for ways to reduce the diversity and number of components and increase density.

Some workload components or design decisions exist only to protect the security (confidentiality, integrity, and availability) of systems and data. These components, although they enhance the security of the environment, also increase costs. They must also be subject to cost optimization themselves. Some example sources for these security-centric additional resources or licensing costs are:

* Compute, network, and data segmentation for isolation, which sometimes involves running separate instances, preventing co-location and reducing density.
* Specialized observability tooling, like a SIEM that can perform aggregation and threat intelligence.
* Specialized networking appliances or capabilities, like firewalls or distributed denial-of-service prevention.
* Data classification tools that are required for capturing sensitivity and information-type labels.
* Specialized storage or compute capabilities to support encryption at rest and in transit, like an HSM or confidential-compute functionality.
* Dedicated testing environments and testing tools to validate that security controls are functioning and to uncover previously undiscovered gaps in coverage.

The preceding items often also exist outside of production environments, in preproduction and disaster recovery resources.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased demand on infrastructure.** The Cost Optimization pillar prioritizes driving down demand on resources to enable the use of cheaper SKUs, fewer instances, or reduced consumption.

* *Premium SKUs*: Some security measures in cloud and vendor services that can benefit the security posture of a workload might only be found in more expensive SKUs or tiers.
* *Log storage*: High fidelity security monitoring and audit data that provide broad coverage increase storage costs. Security observability data is also often stored for longer periods of time than would typically be needed for operational insights.
* *Increased resource consumption*: In-process and on-host security controls can introduce additional demand for resources. Encryption for data at rest and in transit can also increase demand. Both scenarios can require higher instance counts or larger SKUs.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased process and operational costs.** Personnel process costs are part of the overall total cost of ownership and are factored into a workload's return on investment. Optimizing these costs is a recommendation of the Cost Optimization pillar.

* A more comprehensive and strict patch management regime leads to an increase in time and money spent on these routine tasks. This increase is often coupled with the expectation of investing in preparedness for ad hoc patching for zero-day exploits.
* Stricter access controls to reduce the risk of unauthorized access can lead to more complex user management and operational access.
* Training and awareness for security tools and processes take up employee time and also incur costs for materials, instructors, and possibly training environments.
* Complying with regulations might necessitate additional investments for audits and generating compliance reporting.
* Planning for and conducting drills for security-incident response preparedness takes time.
* Time needs to be allocated for designing and performing routine and ad hoc processes that are associated with security, like key or certificate rotation.
* The security validation of the SDLC usually requires specialized tools. Your organization might need to pay for these tools. Prioritizing and remediating issues found during testing also takes time.
* Hiring third-party security practitioners to perform white-box testing or testing that's performed without the knowledge of a system's internal workings (sometimes known as *black-box testing*), including penetration testing, incurs costs.

## Security tradeoffs with Operational Excellence

> ![](../_images/trade-off.svg)
> **Tradeoff: Complications in observability and serviceability.** Operational Excellence requires architectures to be serviceable and observable. The most serviceable architectures are those that are the most transparent to everyone involved.

* Security benefits from extensive logging that provides high fidelity insight into the workload for alerting on deviations from baselines and for incident response. This logging can generate a significant volume of logs, which can make it harder to provide insights that are targeted at reliability or performance.
* When compliance guidelines for data masking are followed, specific segments of logs or even large amounts of tabular data are redacted to protect confidentiality. The team needs to evaluate how this observability gap might affect alerting or hinder incident response.
* Strong resource segmentation increases the complexity of observability by requiring additional cross-service distributed tracing and correlation for capturing flow traces. The segmentation also increases the surface area of compute and data to service.
* Some security controls impede access by design. During incident response, these controls can slow down workload operators' emergency access. Therefore, incident response plans need to include more emphasis on planning and drills in order to reach acceptable efficacy.

> ![](../_images/trade-off.svg)
> **Tradeoff: Decreased agility and increased complexity.** Workload teams measure their velocity so that they can improve the quality, frequency, and efficiency of delivery activities over time. Workload complexity factors into the effort and risk involved in operations.

* Stricter change control and approval policies to reduce the risk of introducing security vulnerabilities can slow down the development and safe deployment of new features. However, the expectation of addressing security updates and patching can increase demand for more frequent deployments. Additionally, human-gated approval policies in operational processes can make it more difficult to automate those processes.
* Security testing results in findings that need to be prioritized, potentially blocking planned work.
* Routine, ad hoc, and emergency processes might require audit logging to meet compliance requirements. This logging increases the rigidity of running the processes.
* Workload teams might increase the complexity of identity management activities as the granularity of role definitions and assignments is increased.
* An increased number of routine operational tasks that are associated with security, like certificate management, increases the number of processes to automate.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased coordination efforts.** A team that minimizes external points of contact and review can control their operations and timeline more effectively.

* As external compliance requirements from the larger organization or from external entities increase, the complexity of achieving and proving compliance with auditors also increases.
* Security requires specialized skills that workload teams don't typically have. Those proficiencies are often sourced from the larger organization or from third parties. In both cases, coordination of effort, access, and responsibility needs to be established.
* Compliance or organizational requirements often require maintained communication plans for responsible disclosure of breaches. These plans must be factored into security coordination efforts.

## Security tradeoffs with Performance Efficiency

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased latency and overhead.** A performant workload reduces latency and overhead.

* Inspection security controls, like firewalls and content safety filters, are located in the flows that they secure. Those flows are therefore subject to additional verification, which adds latency to requests. In highly decoupled architecture the distributed nature can lead to these inspections happening multiple times for a single user or data flow transaction.
* Identity controls require each invocation of a controlled component to be verified explicitly. This verification consumes compute cycles and might require network traversal for authorization.
* Encryption and decryption require dedicated compute cycles. These cycles increase the time and resources consumed by those flows. This increase is usually correlated with the complexity of the algorithm and the generation of high-entropy and diverse initialization vectors (IVs).
* As the extensiveness of logging increases, the impact on system resources and network bandwidth for streaming those logs can also increase.
* Resource segmentation frequently introduces network hops in a workload's architecture.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased chance of misconfiguration.** Reliably meeting performance targets depends on predictable implementations of the design.

A misconfiguration or overextension of security controls can impact performance because of inefficient configuration. Examples of security control configurations that can affect performance include:

* Firewall rule ordering, complexity, and quantity (granularity).
* Failing to exclude key files from file integrity monitors or virus scanners. Neglecting this step can lead to lock contention.
* Web application firewalls performing deep packet inspection for languages or platforms that are irrelevant for the components that are being protected.

## Related links

Explore the tradeoffs for the other pillars:

* [Reliability tradeoffs](../reliability/tradeoffs)
* [Cost Optimization tradeoffs](../cost-optimization/tradeoffs)
* [Operational Excellence tradeoffs](../operational-excellence/tradeoffs)
* [Performance Efficiency tradeoffs](../performance-efficiency/tradeoffs)

---

## Feedback

Was this page helpful?

Yes

No

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Ask Learn

Ask Learn

 Suggest a fix?

---

## Additional resources

---

* Last updated on 
  2024-10-10
---

## Cost Optimization Tradeoffs

# Cost Optimization tradeoffs - Microsoft Azure Well-Architected Framework | Microsoft Learn

**Source:** https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/tradeoffs

**Documentation:** Azure Well-Architected Framework

---

Table of contents 

Exit editor mode

Ask Learn

Ask Learn

Focus mode

Table of contents
[Read in English](#)

Add

Add to plan
[Edit](https://github.com/MicrosoftDocs/well-architected/blob/main/well-architected/cost-optimization/tradeoffs.md)

---

#### Share via

[Facebook](#)
[x.com](#)
[LinkedIn](#)
[Email](#)

---

Print

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Cost Optimization tradeoffs

Feedback

Summarize this article for me

When you design a workload to maximize return on investment (ROI) under financial constraints, you first need clearly defined functional and nonfunctional requirements. A work and effort prioritization strategy is essential. The foundation is a team that has a strong sense of financial responsibility. The team should have a strong understanding of available technologies and their billing models.

After you understand the ROI of a workload, you can start improving it. To improve the ROI, consider how decisions based on the [Cost Optimization design principles](principles) and the recommendations in the [design review checklist for Cost Optimization](checklist) might influence the goals and optimizations of other Azure Well-Architected Framework pillars. For cost optimization, it's important to avoid focusing on a cheaper solution. Choices that focus only on minimizing spending can increase the risk of undermining your workload's business goals and reputation. This article describes example tradeoffs that a workload team might encounter when considering the target setting, design, and operations for cost optimization.

## Cost Optimization tradeoffs with Reliability

The cost of a service disruption must be measured against the cost of preventing or recovering from one. If the cost of disruptions exceeds the cost of reliability design, you should invest more to prevent or mitigate disruptions. Conversely, the cost of the reliability efforts might be more than the cost of a disruption, including factors like compliance requirements and reputation. You should consider strategic divestment in reliability design only in this scenario.

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduced resiliency.** A workload incorporates resiliency measures to attempt to avoid and withstand specific types and quantities of malfunction.

* To save money, the workload team might underprovision a component or overconstrain its scaling, making the component more likely to fail during sudden spikes in demand.
* Consolidating workload resources (*increasing density*) for cost optimization makes individual components more likely to fail during spikes in demand and during maintenance operations like updates.
* Removing components that support resiliency design patterns, like a message bus, and creating a direct dependency reduces self-preservation capabilities.
* Saving money by reducing redundancy can limit a workload's ability to handle concurrent malfunctions.
* Using budget SKUs might limit the maximum service-level objective (SLO) that the workload can reach.
* Setting hard spending limits can prevent a workload from scaling to meet legitimate demand.
* Without reliability testing tools or tests, the reliability of a workload is unknown, and it's less likely to meet reliability targets.

> ![](../_images/trade-off.svg)
> **Tradeoff: Limited recovery strategy.** A workload that's reliable has a tested incident response and recovery plan for disaster scenarios.

* Reduced testing or drilling of a workload's disaster recovery plan might affect the speed and effectiveness of recovery operations.
* Creating or retaining fewer backups decreases possible recovery points and increases the chance of losing data.
* Choosing a less expensive support contract with technology partners might increase workload recovery time due to potential delays in technical assistance.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased complexity.** A workload that uses straightforward approaches and avoids unnecessary or overengineered complexity is generally easier to manage in terms of reliability.

* Using cost-optimization cloud patterns can add new components, like a content delivery network (CDN), or shift duties to edge and client devices that a workload must provide reliability targets for.
* Event-based scaling can be more complicated to tune and validate than resource-based scaling.
* Reducing data volume and tiering data through data lifecycle actions, possibly in conjunction with implementing aggregated data points before a lifecycle event, introduces reliability factors to consider in the workload.
* Using different regions to optimize cost can make management, networking, and monitoring more difficult.

## Cost Optimization tradeoffs with Security

The cost of a compromise to confidentiality, integrity, and availability in a workload must always be balanced against the cost of the effort to prevent that compromise. A security incident can have a wide range of financial and legal impacts and harm a company's reputation. Investing in security is a risk mitigation activity. The cost of experiencing the risks must be balanced against the investment. As a rule, don't compromise on security to gain cost optimizations that are below the point of responsible and agreed upon risk mitigation. Optimizing security costs by rightsizing solutions is an important optimization practice, but be aware of tradeoffs like the following when doing so.

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduced security controls.** Security controls are established across multiple layers, sometimes redundantly, to provide defense in depth.

One cost optimization tactic is to look for ways to remove components or processes that accrue unit or operational costs. Removing security components like the following examples for the sake of saving money impacts security. You need to carefully perform a risk analysis on this impact.

* Reducing or simplifying authentication and authorization techniques compromises the *verify explicitly* principle of zero-trust architecture. Examples of these simplifications include using a basic authentication scheme like preshared keys rather than investing time to learn industry OAuth approaches, or using simplified role-based access control assignments to reduce management overhead.
* Removing encryption in transit or at rest to reduce costs on certificates and their operational processes exposes data to potential integrity or confidentiality breaches.
* Removing or reducing security scanning or inspection tooling or security testing because of the associated cost and time investment can directly impact the confidentiality, integrity, or availability that the tooling and testing is intended to protect.
* Reducing the frequency of security patching because of the operational time invested in cataloging and performing the patching affects a workload's ability to address evolving threats.
* Removing network controls like firewalls might lead to a failure to block malicious inbound and outbound traffic.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased workload surface area.** The Security pillar prioritizes a reduced and contained surface area to minimize attack vectors and the management of security controls.

Cloud design patterns that optimize costs sometimes necessitate the introduction of additional components. These additional components increase the surface area of the workload. The components and the data within them must be secured, possibly in ways that aren't already used in the system. These components and data are often subject to compliance. Examples of patterns that can introduce components include:

* Using the Static Content Hosting pattern to offload data to a new CDN component.
* Using the Valet Key pattern to offload processing and secure resource access to client compute.
* Using the Queue-Based Load Leveling pattern to smooth costs by introducing a message bus.

> ![](../_images/trade-off.svg)
> **Tradeoff: Removed segmentation.** The Security pillar prioritizes strong segmentation to support the application of targeted security controls and to control the blast radius.

Sharing resources, for example in multitenancy situations or co-locating multiple applications on a shared application platform, is an approach for reducing costs by increasing density and reducing the management surface. This increased density can lead to security concerns like these:

* Lateral movement between components that share resources is easier. A security event that compromises the availability of the application platform host or an individual application also has a larger blast radius.
* Co-located resources might share a workload identity and have less meaningful audit trails in access logs.
* Network security controls must be broad enough to cover all co-located resources. This configuration potentially violates the principle of least privilege for some resources.
* Co-locating disparate applications or data on a shared host can lead to extending compliance requirements and security controls to applications or data that would otherwise be out of scope. This broadening of scope necessitates additional security scrutiny and auditing effort on the co-located components.

## Cost Optimization tradeoffs with Operational Excellence

> ![](../_images/trade-off.svg)
> **Tradeoff: Compromised software development lifecycle (SDLC) capacities.** A workload's SDLC process provides rigor, consistency, specificity, and prioritization to change management in a workload.

* Reducing testing efforts to save time and the cost associated with test personnel, resources, and tooling can result in more bugs in production.
* Delaying paying back technical debt to focus personnel efforts on new features can lead to slower development cycles and overall reduced agility.
* Deprioritizing documentation to focus personnel efforts on product development can lead to longer onboarding time for new employees, impact the effectiveness of incident response, and compromise compliance requirements.
* A lack of investment in training leads to stagnated skills, reducing the team's ability to adopt newer technologies and practices.
* Removing automation tooling to save money can result in personnel spending more time on the tasks that are no longer automated. It also increases the risk of errors and inconsistencies.
* Reducing planning efforts, like scoping and activity prioritization, to cut expenses can increase the likelihood of rework due to vague specifications and poor implementation.
* Avoiding or reducing continuous improvement activities, like retrospectives and after-incident reports, to keep the workload team focused on delivery can create missed opportunities to optimize routine, unplanned, and emergency processes.

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduced observability.** Observability is necessary to help ensure that a workload has meaningful alerting and successful incident response.

* Decreasing log and metric volume to save on storage and transfer costs reduces system observability and can lead to:

  + Fewer data points for creating alerts related to reliability, security, and performance.
  + Coverage gaps in incident response activities.
  + Limited observability into interactions or boundaries related to security or compliance.
* Cost optimization design patterns can add components to a workload, increasing its complexity. The workload monitoring strategy must include those new components. For example, some patterns might introduce flows that span multiple components or shift processes from the server to the client. These changes can increase the complexity of correlating and tracking information.
* Reduced investment in observability tooling and the maintenance of effective dashboards can decrease the ability to learn from production, validate design choices, and inform product design. This reduction can also hamper incident response activities and make it harder to meet the recovery time objective and SLO.

> ![](../_images/trade-off.svg)
> **Tradeoff: Deferred maintenance.** Workload teams are expected to keep code, tooling, software packages, and operating systems patched and up to date in a timely and orderly way.

* Letting maintenance contracts with tooling vendors expire can result in missed optimization features, bug resolutions, and security updates.
* Increasing the time between system patches to save time can lead to missed bug fixes or a lack of protection against evolving security threats.

## Cost Optimization tradeoffs with Performance Efficiency

The Cost Optimization and Performance Efficiency pillars both prioritize maximizing a workload's value. Performance Efficiency emphasizes meeting performance targets without spending more than necessary. Cost Optimization emphasizes maximizing the value produced by a workload's resources without exceeding performance targets. As a result, Cost Optimization often improves Performance Efficiency. However, there are Performance Efficiency tradeoffs associated with Cost Optimization. These tradeoffs can make it harder to reach performance targets and hinder ongoing performance optimization.

> ![](../_images/trade-off.svg)
> **Tradeoff: Underprovisioned or underscaled resources.** A performance-efficient workload has enough resources to serve demand but doesn't have excessive unused overhead, even when usage patterns fluctuate.

* Reducing costs by downsizing resources can deprive applications of resources. The application might not be able to handle significant usage pattern fluctuations.
* Limiting or delaying scaling to cap or reduce costs might result in insufficient supply to meet demand.
* Autoscale settings that scale down aggressively to reduce costs might leave a service unprepared for sudden spikes in demand or cause frequent scaling fluctuations (flapping).

> ![](../_images/trade-off.svg)
> **Tradeoff: Lack of optimization over time.** Evaluating the effects of changes in functionality, changes in usage patterns, new technologies, and different approaches on the workload is one way to try to increase efficiency.

* Limiting the focus on developing expertise in performance optimization in order to prioritize delivery can cause missed opportunities for improving resource usage efficiency.
* Removing access performance testing or monitoring tools increases the risk of undetected performance issues. It also limits the ability for a workload team to execute on measure/improve cycles.
* Neglecting areas prone to performance degradation, like data stores, can gradually deteriorate query performance and elevate overall system usage.

## Related links

Explore the tradeoffs for the other pillars:

* [Reliability tradeoffs](../reliability/tradeoffs)
* [Security tradeoffs](../security/tradeoffs)
* [Operational Excellence tradeoffs](../operational-excellence/tradeoffs)
* [Performance Efficiency tradeoffs](../performance-efficiency/tradeoffs)

---

## Feedback

Was this page helpful?

Yes

No

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Ask Learn

Ask Learn

 Suggest a fix?

---

## Additional resources

---

* Last updated on 
  2024-10-10
---

## Operational Excellence Tradeoffs

# Operational Excellence tradeoffs - Microsoft Azure Well-Architected Framework | Microsoft Learn

**Source:** https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/tradeoffs

**Documentation:** Azure Well-Architected Framework

---

Table of contents 

Exit editor mode

Ask Learn

Ask Learn

Focus mode

Table of contents
[Read in English](#)

Add

Add to plan
[Edit](https://github.com/MicrosoftDocs/well-architected/blob/main/well-architected/operational-excellence/tradeoffs.md)

---

#### Share via

[Facebook](#)
[x.com](#)
[LinkedIn](#)
[Email](#)

---

Print

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Operational Excellence tradeoffs

Feedback

Summarize this article for me

Operational Excellence provides workload quality through the implementation of clear team standards, understood responsibility and accountability, attention to customer outcomes, and team cohesion. The implementation of these goals is rooted in DevOps, which recommends minimizing process variance, reducing human error, and ultimately increasing the return of value for the workload. That value isn't just measured against the functional requirements served by the components of the workload. It's also measured by the value that the team delivers in striving for improvement.

During the design phase of a workload and over its lifecycle, as continuous improvement steps are taken, it's important to consider how decisions based on the [Operational Excellence design principles](principles) and the recommendations in the [Design review checklist for Operational Excellence](checklist) might influence the goals and optimizations of other pillars. Certain decisions might benefit some pillars but constitute tradeoffs for others. This article describes example tradeoffs that a workload team might encounter when designing workload architecture and operations.

## Operational Excellence tradeoffs with Reliability

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased complexity.** Reliability prioritizes simplicity, because simple design minimizes misconfiguration and reduces unexpected interactions.

* Safe deployment strategies often require some amount of forward and backward compatibility between application logic and data in the workload. This added complexity increases the testing burden and can lead to complexities or integrity issues with the workload's data.
* Highly layered, modularized, or parameterized infrastructure as code can increase the chance of accidental misconfiguration because of the complexity of the interaction between the code components.
* Cloud design patterns that benefit operations sometimes necessitate the introduction of additional components, for example, the use of an external configuration store or the coordination of sidecar deployments in a containerized application platform. The additional components and added layers of indirection increase the points of interaction in the system, increasing the surface area for malfunction or misconfiguration.
* Workload components that are designed to independently evolve to support agile development and hosting introduce dependencies on service discovery as a layer of indirection. Service discovery might lack responsiveness to change, and malfunction can be hard to diagnose.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased potentially destabilizing activities.** The Reliability pillar encourages the avoidance of activities or design choices that can destabilize a system and lead to disruptions, outages, or malfunctions.

* Deploying small, incremental changes is a technique for mitigating risk, but those small changes are also expected to be delivered to production more frequently. Deployments can destabilize a system, so as the rate of deployment increases, so does this risk.
* A culture that measures itself with velocity metrics like deployments per week and uses automation that can facilitate introducing changes at a faster pace is also likely to perform more deployments in a shorter period.
* Increasing density to simplify operations by reducing the number of control and observability surfaces can also lead to an increased availability risk because malfunction or misconfiguration increases the impact radius of a destabilizing event.

## Operational Excellence tradeoffs with Security

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased surface area.** The Security pillar recommends a reduced workload surface area in terms of components and exposure to operations. This reduction minimizes attack vectors and produces a smaller scope for security control and testing.

* Components that surround the workload and support its operations, like automation or a custom control plane, must also be in scope for regular security hardening and testing.
* Routine, ad hoc, and emergency operations increase the points of contact with the workload. A zero trust approach requires that these processes are considered attack vectors and must be included in the security controls and validation for the workload.
* The observability platform of the system collects logs and metrics about the workload, which can be a valuable source of information disclosure. Therefore, the workload's security needs to extend to protect data sinks from internal and external threats.
* Build agents, externalized configuration and feature toggle stores, and side-by-side deployment approaches all increase the application surface area that requires security.
* A higher deployment frequency caused by small, incremental changes or by "get current, stay current" efforts results in more security testing in the software development lifecycle.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased desire for transparency.** A secure workload is based on designs that protect the confidentiality of data that flows through the components of the system.

Observability platforms ingest data of all types to gain insights into a workload's health and behavior. As teams try to attain higher fidelity in observability data, there's an increased risk that data classification controls, like data masking, of the source systems don't extend to the logs and log sinks of the observability platform.

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduced segmentation.** A key security approach for isolating access and function is to design a strong segmentation strategy. This design is implemented through resource isolation and identity controls.

* Co-locating disparate application components in shared compute, network, and data resources to make management easier reverses segmentation or makes role-based segmentation harder to achieve. Co-located components might also need to share a workload identity, which can lead to over-assignment of permissions or a lack of traceability.
* Collecting all logs from across the system in a unified log sink can make querying and building alerts easier. However, doing so can also make it harder or impossible to provide row-based security in order to treat sensitive data with the required audit controls.
* Simplifying the management of attribute-based or role-based security by reducing the granularity of roles and their assignments can lead to inappropriately broad permissions.

## Operational Excellence tradeoffs with Cost Optimization

The Operational Excellence pillar never recommends activities that reduce productivity or jeopardize a workload's return on investment. Recommendations that seem to shift focus from delivery activities take into account long-term best interests for the workload and team. If your workload is nearing its sunset date, it probably doesn't make sense to invest highly in recommendations that trigger these tradeoffs.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased resource spending.** A major cost driver for a workload is the cost of its resources. Deploying fewer resources, right-sizing resources, and reducing consumption generally helps keep costs low.

* Implementing safe deployment practices, even if the changes are relatively small, can lead to an increase in the number of resources that are concurrently deployed. These patterns require the deployment of multiple concurrent instances of the application or infrastructure component so that traffic can be shifted in a controlled way. This increase is more pronounced in a workload that uses an immutable infrastructure approach.
* The team might need to introduce additional workload components in order to implement operationally aligned cloud design patterns or workload automation. For example, to support deployment agility, they might add a gateway routing component. To support better configuration management, they might add an external configuration store. To support tenant lifecycle events, they might build a control plane. These resources also influence the costs of preproduction environments.
* Increasing the number of preproduction environments to improve the development and testing experience through isolation also increases the number of resources. These resources, which aren't used to deliver supply against production demand, increase the cost of the solution.
* Increasing the parity of preproduction environments with the production environment, in terms of resource count, SKUs, and data volumes, improves the quality assurance process. The cost increases as parity increases.
* Although telemetry data isn't directly a resource, to enable the effectiveness of observability platforms, this data needs to be persisted. Most operational data stores have pricing that's based on a combination of ingestion rates and volume. Generally, as the amount of low-latency, high-diversity telemetry increases, costs also increase. For multi-region deployments, these operational data sinks are expected to be deployed per region, so any per-resource costs become a factor.

> ![](../_images/trade-off.svg)
> **Tradeoff: Decreased focus on delivery activities.** Workload team members deliver increased workload value by efficiently performing tasks that are aligned to their capabilities.

* Workload teams that spend time creating and refining a healthy and responsible support structure and incident response are providing a valuable service to the workload's users. As the support effort increases (for example, formal on-call rotations), usually because of a change in business criticality, the costs of these activities increase. This cost increase can be the result of an increase in staff or can be incurred indirectly in the form of attention that's shifted from delivery activities to supporting functions.
* Training is a critical part of a workload team's personal continuous improvement process. This training can be formal or self-directed during personal enrichment time. As the amount of training time increases, the amount of time available for direct development of the workload decreases. Investment in training is diminished when the training isn't role-based or specifically relevant to the workload or its future.
* Standardized routine operational tasks for protecting the reliability, security, and performance efficiency of a workload take time to define, refine, and perform. This time isn't directly spent on delivery. Some examples of these tasks are comprehensive change impact analysis, change control processes, thorough testing, and increased patch management. As the frequency, comprehensiveness, or operational burden of these tasks increases, the time invested also increases.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased tooling demands and diversity.** The Cost Optimization pillar recommends the reduction of tooling sprawl, consolidation of vendors, and a right-sized approach to all tooling purchases.

A workload team purchases tools and hardware to support activities that are performed during the entire software development lifecycle (SDLC), including planning and design, development and testing, and monitoring. The marketplace for tooling in this space is growing. Tools are offered at various price points that usually correspond to the tools' features and capabilities. Except for free offerings, these tools incur initial licensing costs, which might be per-user, per-device, or site-wide. They often also require ongoing maintenance contracts. New vendor relationships might need to be established. Here are some examples of expected tooling or hardware spending that's associated with the principles of operational excellence:

* Requirements and backlog management
* Architecture design tools
* UI/UX design tools
* Code and asset hosting
* Code and low-code development environments
* Automation tools
* Development and quality assurance workstations
* Development and deployment pipelines
* Test execution and tracking
* Observability tools

## Operational Excellence tradeoffs with Performance Efficiency

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased resource utilization.** The Performance Efficiency pillar recommends the allocation of as much of the available compute and network as possible to the requirements of the workload.

* A workload's observability framework requires that the components in the architecture allocate time and resources to create, collect, and stream logs and metrics. These data points help ensure that effective alerting and monitoring is possible for reliability, security, and performance. As the level of instrumentation increases, the strain on system resources might also increase.
* Some deployment models, like blue/green deployment, which a workload might use for safe deployment, might introduce side-by-side deployments on the production application platform. These deployments require preemptive scaling to provide enough supply to meet future demand, or leave a mostly dormant deployment in place for a period of time to support rollback.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased latency.** To create performant workloads, teams look for ways to reduce the time and resources that workloads consume to perform their tasks.

* Many deployment models require the use of gateway routing access patterns, which can introduce latency. This latency draws against the performance target budget for the related flows.
* Some Architecture design patterns that support "independent change over time" approaches to support the ideals of incremental improvement can introduce latency due to the traversal of additional components. This latency can be introduced by gateways, messaging brokers, or anti-corruption layers.

## Related links

Explore the tradeoffs for the other pillars:

* [Reliability tradeoffs](../reliability/tradeoffs)
* [Security tradeoffs](../security/tradeoffs)
* [Cost Optimization tradeoffs](../cost-optimization/tradeoffs)
* [Performance Efficiency tradeoffs](../performance-efficiency/tradeoffs)

---

## Feedback

Was this page helpful?

Yes

No

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Ask Learn

Ask Learn

 Suggest a fix?

---

## Additional resources

---

* Last updated on 
  2024-10-10
---

## Performance Efficiency Tradeoffs

# Performance Efficiency tradeoffs - Microsoft Azure Well-Architected Framework | Microsoft Learn

**Source:** https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/tradeoffs

**Documentation:** Azure Well-Architected Framework

---

Table of contents 

Exit editor mode

Ask Learn

Ask Learn

Focus mode

Table of contents
[Read in English](#)

Add

Add to plan
[Edit](https://github.com/MicrosoftDocs/well-architected/blob/main/well-architected/performance-efficiency/tradeoffs.md)

---

#### Share via

[Facebook](#)
[x.com](#)
[LinkedIn](#)
[Email](#)

---

Print

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Performance Efficiency tradeoffs

Feedback

Summarize this article for me

A workload that meets its performance targets without overprovisioning is efficient. The goal of performance efficiency is to have just enough supply to handle demand at all times. Key strategies for performance efficiency include proper use of code optimizations, design patterns, capacity planning, and scaling. Clear performance targets and testing underpin this pillar.

During the process of negotiating a workload's performance targets and designing a workload for performance efficiency, it's important to be aware of how the [Performance Efficiency design principles](principles) and the recommendations in the [Design review checklist for Performance Efficiency](checklist) might affect the optimization goals of other pillars. Certain performance efficiency decisions might benefit some pillars but constitute tradeoffs for others. This article lists example tradeoffs that a workload team might encounter when designing workload architecture and operations for performance efficiency.

## Performance Efficiency tradeoffs with Reliability

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduced replication and increased density.** A cornerstone of reliability is ensuring resilience by using replication and limiting the blast radius of malfunctions.

* A workload that achieves efficiency by delaying scaling until the last responsible moment closely meets demand but is vulnerable to unforeseen node failures and scaling delays.
* Consolidating workload resources can use excess capacity and improve efficiency. However, it increases the blast radius of a malfunction in the co-located component or application platform.
* Scaling in or scaling down to minimize surplus capacity can leave a workload underprovisioned during usage spikes, which leads to service disruptions due to insufficient supply.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased complexity.** Reliability prioritizes simplicity.

* Using autoscaling to balance workload supply against demand introduces variability in the workload's topology and adds a component that must work correctly for the system to be reliable. Autoscaling leads to triggering more application lifecycle events, like starting and stopping.
* Data partitioning and sharding help avoid performance issues in large or frequently accessed datasets. However, the implementation of these patterns increases complexity because (eventual) consistency needs to be maintained across additional resources.
* Denormalizing data for optimized access patterns can improve performance, but it introduces complexity because multiple representations of data need to be kept synchronized.
* Performance-centric cloud design patterns sometimes necessitate the introduction of additional components. The use of these components increases the surface area of the workload. The components then must themselves be made reliable to keep the whole workload reliable. Examples include:

  + A message bus for load leveling, which introduces a critical, stateful component.
  + A load balancer for autoscaled replicas, which requires reliable operation and the enlistment of replicas.
  + Offloading data to caches, which requires reliable cache invalidation approaches.

> ![](../_images/trade-off.svg)
> **Tradeoff: Testing and observation on active environments.** Avoiding the unnecessary use of production systems is a self-preservation and risk avoidance approach for reliability.

* Performance testing in active environments, like the use of synthetic transactions, carries the risk of causing malfunctions due to the test actions or configurations.
* Workloads should be instrumented with an application performance monitoring (APM) system that enables teams to learn from active environments. The APM tooling is installed and configured in application code or in the hosting environment. Improper use, exceeding limitations, or misconfiguration of the tool can compromise its functionality and maintenance, potentially undermining reliability.

## Performance Efficiency tradeoffs with Security

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduction of security controls.** Security controls are established across multiple layers, sometimes redundantly, to provide defense in depth.

One performance optimization strategy is to remove or bypass components or processes that contribute to delays in a flow, especially when their processing time isn't justified. However, this strategy can compromise security and should be accompanied by a thorough risk analysis. Consider the following examples:

* Removing encryption in transit or at rest to improve transfer speeds exposes the data to potential integrity or confidentiality breaches.
* Removing or reducing security scanning or inspecting tools to reduce processing times can compromise the confidentiality, integrity, or availability that those tools protect.
* Decreasing the frequency of security patching to limit the performance impact can leave a workload more vulnerable to emerging threats.
* Removing firewall rules from network flows to improve network latency can allow undesirable communication.
* Minimizing data validation or content safety checks for quicker data processing might compromise data integrity, especially if inputs are malicious.
* Using less entropy in encryption or hashing algorithms, for example, on the initialization vector (IV), is more efficient but makes the encryption easier to crack.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased workload surface area.** Security prioritizes a reduced and contained surface area to minimize attack vectors and reduce the management of security controls.

Performance-centric cloud design patterns sometimes necessitate the introduction of additional components. These components increase the surface area of the workload. The new components must be secured, possibly in ways that aren't already used in the system, and they often increase the compliance scope. Consider these commonly added components:

* A message bus for load leveling
* A load balancer for autoscaled replicas
* Offloading data to caches, application delivery networks, or content delivery networks
* Offloading processing to background jobs or even client compute

> ![](../_images/trade-off.svg)
> **Tradeoff: Removing segmentation.** The Security pillar prioritizes strong segmentation to enable fine-grained security controls and reduce blast radius.

Sharing resources through increased density is an approach for improving efficiency. Examples include multitenancy scenarios or combining disparate applications in an architecture on a common application platform. The increased density can lead to the following security concerns:

* Increased risk of unauthorized lateral movement from one tenant to another.
* A shared workload identity that violates the principle of least privilege and obscures individual audit trails in access logs.
* Perimeter security controls, for example network rules, that are reduced to cover all co-located components, giving individual components more access than necessary.
* A compromise of the application platform host or an individual component due to a larger blast radius. This increase is caused by easier access to co-located components.
* Co-locating disparate components leading to more components in scope for compliance because of their shared host.

## Performance Efficiency tradeoffs with Cost Optimization

> ![](../_images/trade-off.svg)
> **Tradeoff: Too much supply for demand.** Both Cost Optimization and Performance Efficiency prioritize having just enough supply to serve demand.

* Overprovisioning is a risk when teams try to mitigate performance issues in a workload. Some common causes of overprovisioning include:

  + Initial capacity planning was misjudged because the team focused only on peak load estimates, neglecting strategies for peak smoothing in the workload design.
  + Scaling a resource up or out during a troubleshooting step of an incident response.
* Autoscaling can be misconfigured. Some examples of misconfigured autoscaling include:

  + Scaling up with minimal changes in demand or an extended cooldown period can incur more cost than demand requires.
  + Using autoscaling without a set upper limit can lead to uncontrolled growth due to system malfunctions or abuse and exceed the expected workload requirements.
* Expanding into multiple regions can enhance performance by bringing workloads closer to the user and can avoid temporary resource capacity constraints. However, that topology also adds complexity and resource duplication.

> ![](../_images/trade-off.svg)
> **Tradeoff: More components.** One cost optimization technique is to consolidate with a smaller number of resources by increasing density, removing duplication, and co-locating functionality.

* Performance-centric cloud design patterns sometimes necessitate the introduction of extra components. These extra components usually lead to an overall cost increase for the workload. For example, you might include a message bus for load leveling or offload tasks to an application or content delivery network for improved response times.
* Resource segmentation allows different parts of a workload to have distinct performance characteristics, enabling independent tuning for each segment. However, it can increase the total ownership costs because it requires multiple optimized segments rather than a single, generalized component.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased investment on items that aren't aligned with functional requirements.** One approach to cost optimization is evaluating the value provided by any solution that's deployed.

* Premium services and SKUs can help a workload meet performance targets. These services usually cost more and can provide extra features. They might be underutilized if many of the premium features aren't used specifically for meeting performance targets.
* A performant workload requires telemetry data for observability that must be transferred and stored. An increase in the performance telemetry being collected can increase the cost of telemetry data transfer and storage.
* Performance testing activities add costs that aren't associated with the value of the production system. Examples of performance testing costs include:

  + Instantiating environments that are dedicated to performance-centric tests.
  + Using specialized performance tooling.
  + Spending time to run the tests.
* Training team members for specialized performance optimization tasks or paying for performance tuning services adds to the cost of a workload.

## Performance Efficiency tradeoffs with Operational Excellence

> ![](../_images/trade-off.svg)
> **Tradeoff: Reduced observability.** Observability is necessary to provide a workload with meaningful alerting and help ensure successful incident response.

* Reducing log and metric volume to reduce the processing time spent on collecting telemetry instead of other tasks reduces the overall observability of the system. Some examples of the resulting reduced observability include:

  + It limits the data points that are used to build meaningful alerts.
  + It leads to gaps in coverage for incident response activities.
  + It limits observability in security-sensitive or compliance-sensitive interactions and boundaries.
* When performance design patterns are implemented, the complexity of the workload often increases. Components are added to critical flows. The workload monitoring strategy and performance monitoring must include those components. When a flow spans multiple components or application boundaries, the complexity of monitoring the performance of that flow increases. Flow performance needs to be correlated across all the interconnected components.

> ![](../_images/trade-off.svg)
> **Tradeoff: Increased complexity in operations.** A complex environment has more complex interactions and a higher likelihood of a negative impact from routine, ad hoc, and emergency operations.

* Improving performance efficiency by increasing density elevates the risk in operational tasks. An error in a single process can have a large blast radius.
* As performance design patterns are implemented, they influence operational procedures like backups, key rotations, and recovery strategies. For example, data partitioning and sharding can complicate routine tasks when teams try to ensure that those tasks don't affect data consistency.

> ![](../_images/trade-off.svg)
> **Tradeoff: Culture stress.** Operational Excellence is rooted in a culture of blamelessness, respect, and continuous improvement.

* Conducting root cause analysis of performance issues identifies deficiencies in processes or implementations that require correction. The team should consider the exercise a learning opportunity. If team members are blamed for issues, morale can be affected.
* Routine and ad hoc processes can affect workload performance. It's often considered preferable to perform these activities during off-peak hours. However, off-peak hours can be inconvenient or outside of regular hours for the team members who are responsible for or skilled in these tasks.

## Related links

Explore the tradeoffs for the other pillars:

* [Reliability tradeoffs](../reliability/tradeoffs)
* [Security tradeoffs](../security/tradeoffs)
* [Cost Optimization tradeoffs](../cost-optimization/tradeoffs)
* [Operational Excellence tradeoffs](../operational-excellence/tradeoffs)

---

## Feedback

Was this page helpful?

Yes

No

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Ask Learn

Ask Learn

 Suggest a fix?

---

## Additional resources

---

* Last updated on 
  2024-10-10