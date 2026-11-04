# Requirements and design report

Use this for the design you propose to the client: the requirements, the options you weighed, the one you chose and why.

## 1. Business context
Who the client is, what they do, who uses the systems, and the problem to solve (in the client's words).

## 2. Requirements
| ID | Requirement (client's words) | Functional / non-functional | Source (consultation no.) |
| --- | --- | --- | --- |

## 3. Specifications
| Req ID | Measurable specification | How it will be tested |
| --- | --- | --- |

Performance: sizing from measured numbers, with headroom stated.
Data migration: what moves, from where, in what order, the cutover and the fallback.

## 4. Network design
Zones, address ranges, and the controls between zones. Add a diagram with every device, range and link labelled. Link each part to a requirement.

## 5. Server design
For each server: role, size, operating system, location, dependencies. Include at least one server with complex user and network service requirements.

## 6. Service configuration
For each service (DNS, DHCP, time, web, proxy, file transfer, mail, directory, file and print, backup, monitoring): purpose, key settings, dependencies, who manages it, how it starts and is restarted.

## 7. Decisions and alternatives
Choices made, options rejected, and why.

## 8. Changes after the prototype
| Date | What the prototype taught me | What I changed |
| --- | --- | --- |

## 9. Version history
| Version | Date | Change |
| --- | --- | --- |
