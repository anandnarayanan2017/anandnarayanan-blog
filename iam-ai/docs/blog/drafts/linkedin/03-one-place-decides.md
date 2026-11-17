A score of 64 is not a decision. Someone has to say what 64 means.

In IAM AI exactly one thing says it: an OPA policy, about 160 lines of Rego. No application code hard-codes ALLOW
or BLOCK anywhere else.

That gives a security owner one file to read, its own change control, and context the score cannot see: a
privileged sign-in outside business hours is blocked at a score of 50, not 70.

But one policy point is also one point of failure. When OPA is down, a Python fallback copies its blocking rules.
Two code reviews found that copy had drifted: first it ignored the unconditional blocks, then it missed one of five
and read a travel time of zero minutes as 999.

Now a unit test reads the Rego file and fails if the two disagree.

And the language model? It runs after the decision, its prompt forbids it to recommend anything, and if it fails a
fixed template takes over.

Part 3 of the IAM AI series is in the first comment.

#PolicyAsCode #OPA #IdentitySecurity #SoftwareArchitecture #RegTech
