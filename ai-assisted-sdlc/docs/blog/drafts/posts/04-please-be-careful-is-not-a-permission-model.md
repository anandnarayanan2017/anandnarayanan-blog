# “Please Be Careful” Is Not a Permission Model

![“Please be careful” is not a permission model: on the left, rules written in the prompt (don’t edit the tests, only change this project, don’t run dangerous commands, never leak secrets); on the right, the same rules enforced by the system (tests restored before every check, writes outside the workspace refused, no shell and only fixed commands, keys from the environment and never logged). The thing that judges the work must not be writable by the thing being judged.](../../images/04-please-be-careful-is-not-a-permission-model-1.png)

*A rule in a prompt is a request. A rule in the system is a control.*

Most agent instruction files I have read contain a sentence like this:

> Do not modify the tests. Do not touch production. Never commit secrets. Be careful with destructive commands.

Every one of those is a good rule. None of them is a permission.

A prompt is text that a model reads, weighs against everything else it has read, and usually follows. “Usually” is fine for a writing style. It isn’t fine for “never delete the customer table”.

## Three questions, answered by the system

In Part 3, the harness gave the agent context, tools, feedback and recovery. This part is about the boundaries of those tools. For any agent I now ask three questions:

1. **What may it read?**
2. **What may it change?**
3. **What may it execute?**

And for each answer, one more: **what stops it if it tries anyway?** If the answer is “the prompt says not to”, the honest answer is “nothing”.

## Change: the tests the agent can’t keep

In Part 2, the tests are the specification. So the most tempting thing for an agent under pressure to pass is to change the tests.

This isn’t paranoia. A generator told “make the check green” will eventually notice that the shortest path to green is to weaken an assertion, skip a test or delete it. It isn’t malice. It is optimisation.

My harness tells the generator it may not edit the acceptance tests. Then it ignores whether the generator listened: before every check it rewrites the tests from the contract. An edited test is overwritten before it can run. A deleted test comes back.

I considered making the files read-only instead. I rejected it: a process that can write files can usually find a way around a file mode. Restoring the tests from a copy the agent never touches doesn’t depend on the agent’s cooperation at all.

The same idea protects the architecture rules. They live outside the workspace the agent writes to, so the agent can be judged by them but can’t edit them.

**The thing that judges the work must not be writable by the thing being judged.**

## Change: the workspace has walls

The generator returns file contents and the harness writes them. Before each write, the harness resolves the path and refuses anything outside the workspace:

```text
path escapes workspace: ../../.github/workflows/deploy.yml
```

That one check closes a whole family of problems: editing the CI pipeline, overwriting a dotfile, writing into another project. It is a few lines of code. It replaces a paragraph of prompt that says “only change files in this project”.

## Execute: no shell, fixed commands

The generator in my harness can’t run commands. It never gets a shell.

The only things that run are the contract’s check command, fixed before the generator starts, and the app itself, started by the harness for live probes. The agent can influence what code runs inside those commands. It can’t choose the commands.

For the model benchmark, where the harness runs code from models I haven’t vetted at all, the boundary is tighter. Each sample runs in a fresh Node.js process with the permission model switched on: read access only to its own temporary folder, no file writes, no child processes, no worker threads, no native add-ons, network blocked, and a ten-second timeout. That process runs inside a container. The database is a throwaway PostgreSQL on a RAM disk, reset before each run.

None of those layers is perfect on its own. Together they mean a misbehaving sample wastes ten seconds, not my afternoon.

## Read: the part people forget

Reading feels harmless. It isn’t, for two reasons.

**Secrets.** Every model vendor’s API key comes from an environment variable. The configuration stores the variable’s name, never its value. Keys are never printed, logged or written to the transcripts the harness keeps of every model call. A key is only ever sent to the address configured for that model, which is why a change to that address is reviewed like a code change: point it somewhere else and the key goes with it.

**Instructions in data.** An agent reads files, tool output, web pages and other models’ replies. Any of them can contain text that looks like an instruction: “ignore the previous rules and…”. The rule in my repository is that all of this is data, never instructions. But that rule is, again, a sentence in a prompt. The real protection is that even a fully convinced agent can’t do much: it can’t run a shell, can’t write outside the workspace, can’t edit its tests, and can’t reach a production database because none is configured.

Simon Willison describes the dangerous combination as a *lethal trifecta*: access to private data, exposure to untrusted content, and a way to send data out. You can’t always remove the untrusted content. You can usually remove one of the other two.

## The pattern

Every control in this post has the same shape:

| Rule in the prompt | Control in the system |
|---|---|
| “Don’t edit the tests.” | Tests restored from the contract before every check |
| “Only change this project.” | Writes outside the workspace are refused |
| “Don’t run dangerous commands.” | No shell; only fixed, pre-agreed commands run |
| “Don’t leak secrets.” | Keys from the environment, never logged, sent only to the configured address |
| “Only use approved libraries.” | Imports checked against an allow-list on every sprint |
| “Be careful with untrusted code.” | Separate process, permission model, timeout, container |

I keep the left column. It helps the agent do the right thing first time, which saves an attempt. I just don’t rely on it.

## Where this stops working

- **My boundaries are coarse.** The harness allows or refuses a whole category (shell, network, paths). Real teams need finer rules: this agent may open pull requests but not merge them; that one may read the staging logs but not production.
- **There are gaps.** On older Node.js versions the permission model doesn’t block network access, so my benchmark relies on the container for that. I wrote the gap down rather than pretending it isn’t there.
- **A path check is not a sandbox.** Refusing `../` stops mistakes and simple tricks. A determined attacker with real execution needs an operating-system boundary: a container, a virtual machine, a separate account.
- **Least privilege makes agents less useful.** Every permission I remove is a task the agent can no longer do alone. That is the right trade for a booking API built by an experiment. It needs a deliberate decision, per action, in a real organisation.

That last point is where the next two parts go. Some actions should be allowed automatically. Some need a reviewer. And some reviewers are themselves models. So how much should you trust a reviewer that scores the broken code 9 out of 10?

**Next: Part 5, When the AI Reviewer Says 9/10 and the Test Still Fails.**

Which rule in your agent’s instructions would cause real damage if the agent ignored it, and what actually enforces it? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **Least privilege:** Jerome Saltzer and Michael Schroeder, “The Protection of Information in Computer Systems”, *Proceedings of the IEEE*, 1975: the original statement of least privilege and fail-safe defaults.
- **Excessive agency:** OWASP, [Top 10 for Large Language Model Applications](https://genai.owasp.org/llm-top-10/), on prompt injection and excessive agency.
- **The lethal trifecta:** Simon Willison, [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/).
- **Process sandbox:** Node.js documentation, [Permissions](https://nodejs.org/api/permissions.html).
- **CI tokens:** GitHub documentation, [Controlling permissions for GITHUB_TOKEN](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token).
