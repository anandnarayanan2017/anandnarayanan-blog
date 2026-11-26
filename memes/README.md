# Memes

LinkedIn memes on one recurring picture: the "AI-native SDLC factory" from
[AI-assisted SDLC Part 1](../ai-assisted-sdlc/docs/blog/images/01-from-arm-assembly-to-ai-1.png),
with the architect, the monkey agents and the "Still in control... right?" mug. Each post gets its
own version: the people and the scene stay the same, and the words change to fit the post.

## Make one

1. Copy a labels file, for example [`identity-01.json`](identity-01.json), and change the words.
2. Render it next to the post's LinkedIn draft:

   ```bash
   node memes/render.mjs memes/identity-01.json agent-identity/docs/blog/linkedin/01-an-agent-cant-answer-an-mfa-prompt-meme.jpg
   ```

3. Open the image and check every label fits its panel. Shorten any that spill over.

`render.mjs` needs Playwright with Chromium. It isn't a site dependency, so it isn't in
`package.json`.

## Labels

Every key is optional. Leave one out and that part of the picture keeps its original words.

| Key | Where it goes | Fits |
|---|---|---|
| `title`, `subtitle` | The banner at the top | About 26 and 45 characters |
| `board.heading`, `board.items[].text` / `.done` | The whiteboard on the left | Up to 6 items of about 24 characters |
| `shirts` | The three front monkeys' T-shirts, left to right; `\n` breaks a line | Two short words each |
| `boxes` | The four boxes on the conveyor belt, left to right | About 10 characters each |
| `dashboard.heading`, `dashboard.rows[].text` / `.status` | The left dashboard; status is `ok` ✓, `unknown` ? or `fail` ✗ | Up to 6 rows of about 20 characters |
| `output.lines`, `output.note` | The words beside the chart | 3 lines of about 10 characters |
| `anomalies` | The red "Anomalies detected" panel | Up to 5 lines of about 32 characters |
| `sticky` | The yellow note by the kill switch | About 35 characters |
| `killSwitch.title`, `.subtitle` | The kill switch label | About 14 and 28 characters |
| `plan` | The notebook, bottom right | 3 lines of about 24 characters |
| `base` | A different picture of the same size, relative to the repo root | 1222 × 1287 pixels |

Labels are inserted as plain text, never HTML.

## Rendered so far

| Post | Labels | Image |
|---|---|---|
| Identity for AI Agents Part 1 | [`identity-01.json`](identity-01.json) | [`01-an-agent-cant-answer-an-mfa-prompt-meme.jpg`](../agent-identity/docs/blog/linkedin/01-an-agent-cant-answer-an-mfa-prompt-meme.jpg) |
