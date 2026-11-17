# IAM AI

A five-part series on IAM AI, a continuous identity trust scoring platform for Microsoft Entra ID on Azure, built
between June and September 2026.

The series asks **can we trust who signed in?**, the question that comes before Agent Sentinel’s *can we trust what
the agent did?*

| Part | Title | What it covers |
|---|---|---|
| 1 | Who Signed In, and Do We Still Trust Them? | What the platform does, the four rules it rests on, and the ten weeks from first commit to evidence |
| 2 | Rules Decide, Models Advise | Fifteen signals, eleven rules, three anomaly models, the hard floor, and an inverted sign |
| 3 | One Place Decides | OPA as the single policy point, the fallback when it is down, and the model that only explains |
| 4 | The Build Was Green. The System Had Never Run. | What starting the whole stack found that no check had |
| 5 | Tenants, Evidence and What Is Still Open | Adding tenants, the leak that survived its fix, the open list, and where Agent Sentinel joins in |

The code lives in a separate repository, `iam-ai-tf`, which is private for now. Every claim in the posts links to a
file at commit `100c0d2`. See [docs/blog/drafts/REVIEW.md](docs/blog/drafts/REVIEW.md) for what has to happen
before the first part goes out.
