Adding tenants to a system built without them taught me where tenant identity has to reach: not just the tables,
but every cache key, every graph query and every nightly job.

IAM AI missed each of them once:

→ A new required tenant column made the ingestion worker fail every write, quietly, inside a broad except.
→ Redis baselines and Neo4j queries were keyed by user alone, so one tenant’s habits could shape another’s scores.
→ Twelve days after that fix, a nightly job turned up with its own copy of the old key format.

The rules that came out of it: the tenant comes from the caller’s key, never the request body. Ownership is
checked, not assumed. Every duplicated fact needs a test that fails when the copies disagree.

The last part of the series also lists what is still open, twelve items in all, and where IAM AI meets Agent
Sentinel: the trust score of the person behind an agent, feeding the policy that governs the agent.

Part 5 is in the first comment.

#IdentitySecurity #MultiTenancy #SoftwareArchitecture #AIAgents #RegTech
