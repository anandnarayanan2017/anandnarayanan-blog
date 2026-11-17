The Docker images built. The type checker was clean. CI was green.

Nobody had ever started the whole system.

When I finally ran it, my identity risk-scoring project failed in two ways no check had seen:

1. It did not start. The four services share code, and each image was built from its own folder, so the shared
code was not in any of them. Building an image never imports the code, so the build passed. Every container died
on its first import.

2. It did not keep its evidence. Every BLOCK and STEP_UP decision was made and enforced, and then its alert record
failed on a foreign key. A broad except logged the error, and the logger dropped the reason. I found it by
querying the database.

The run also exposed a test that had passed only because of a bug, and a type check that was green because the
package it was checking was never installed.

What I took from it:

→ A build proves the files are there. Only a run proves they work together.
→ In a repository of services that share code, the build context is an architecture decision.
→ The record of a decision is part of the decision. Write it all at once, and decide out loud what happens when
you can’t.
→ A check that cannot fail is not a check. Break it once on purpose.
→ Test what the design guarantees, not what one run happened to return.

Part 4 of the IAM AI series, with the code and tests behind each point, is in the first comment.

#SoftwareArchitecture #DevOps #Testing #Azure #RegTech
