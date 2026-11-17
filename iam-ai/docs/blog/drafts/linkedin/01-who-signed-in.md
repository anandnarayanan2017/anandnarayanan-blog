Before an AI agent acts, a person signs in. The agent usually acts with that person’s access.

So before “can we trust what the agent did?”, there is an earlier question: can we trust who signed in?

Most sign-ins are checked once, at the door. A stolen refresh token, a consent grant to a malicious app, or an
admin signing in at 03:00 from a new country with SMS as the only second factor can all pass that check.

IAM AI is my attempt at continuous trust for Microsoft Entra ID sign-ins. It rests on four rules:

→ Typed events at every boundary.
→ Rules decide, models advise. The anomaly models can never block on their own.
→ One place decides: an OPA policy has the final say.
→ The language model explains. It never decides.

The first commit was 8,300 lines with no tests. It looked finished. This new five-part series is about the ten
weeks it took to find out what it actually did.

Part 1 is in the first comment.

#IdentitySecurity #EntraID #SoftwareArchitecture #Azure #RegTech
