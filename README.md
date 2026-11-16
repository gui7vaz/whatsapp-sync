# WhatsApp Sync

A small app for your Mac that keeps the WhatsApp conversations **you choose**
as Markdown (`.md`) files in folders you choose, so Claude can use them as
context. It can also ask Claude Code on your Mac to draft replies.

**What it does not do:** it never sends WhatsApp messages and never changes
WhatsApp. It reads the WhatsApp for Mac database (read-only) and runs only on
your computer, at http://whatsapp-sync.localhost:8765. The only time chat text
leaves your Mac is when **you** click *Generate drafts*: then that
conversation's recent history goes to Claude through your own Claude Code
account (see *Privacy*).

---

## Install (about 10 minutes)

> **Using an AI assistant (Claude Code, etc.)?** Open a terminal session in
> any folder and say: *"Install WhatsApp Sync by following the README at
> https://github.com/gui7vaz/whatsapp-sync"*. The section
> [For AI assistants](#for-ai-assistants) tells it exactly what to do and
> when to hand over to you.

### What you need

- A Mac with **macOS 13 or newer**.
- **WhatsApp for Mac** installed and signed in (App Store or whatsapp.com).
  Open it at least once so your chats are on the Mac.
- **Command Line Tools** (they include `git`, `python3` and the C compiler).
  Check in Terminal:
  ```bash
  xcode-select -p
  ```
  If it prints an error, install them (a window opens; click Install):
  ```bash
  xcode-select --install
  ```
- Optional, for reply drafts: **Claude Code** installed and signed in
  (`claude --version` works in Terminal).

### Steps

1. **Download the app** into `~/Applications` (keep it out of Google Drive,
   iCloud or Dropbox folders — the app gets Full Disk Access, so its code
   should live in a normal local folder):
   ```bash
   mkdir -p ~/Applications && cd ~/Applications && git clone https://github.com/gui7vaz/whatsapp-sync.git "WhatsApp Sync"
   ```

2. **Install the background service** (builds a tiny launcher app and starts
   it at every login):
   ```bash
   cd ~/Applications/"WhatsApp Sync" && zsh servico/instalar.sh
   ```
   It ends with `Service installed`.

3. **Give it Full Disk Access** — this is what lets it read the WhatsApp
   database. Only you can do this step:
   1. Open **System Settings → Privacy & Security → Full Disk Access**.
   2. Find **WhatsApp Sync** and turn it on. If it is not in the list, click
      **+**, press **⌘⇧G**, paste
      `~/Applications/WhatsApp Sync/WhatsApp Sync.app`, and click **Open**.
   3. Restart the service so it picks up the permission:
      ```bash
      launchctl kickstart -k gui/$(id -u)/com.whatsapp-sync
      ```

4. **Open the app:** http://whatsapp-sync.localhost:8765

5. **First setup in the app:**
   - **Settings** → set *Your name in conversations*, then **Save settings**.
   - **Following** → **New topic** (e.g. a customer or partner), then the
     new-folder icon to pick where its `.md` files go, and add keywords under
     *Suggestions*.
   - **Conversations** → search and **Follow** the chats you want. New ones
     appear at the top of **Following** in red until they have a topic or their
     own folder.

### Check that it works

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://whatsapp-sync.localhost:8765/
```
`200` means the app is running. In the app, **Settings → WhatsApp
installations** should list your WhatsApp with a number of conversations.

---

## Everyday use

| Tab | What it is for |
|---|---|
| **Dashboard** | Totals, who is waiting for your reply, activity charts. **Customize** reorders or hides widgets. |
| **Conversations** | Search all of WhatsApp (names and message text) and follow chats. |
| **Following** | Your topics, their folders and keywords, and where each conversation is written. Red = nothing is written. |
| **Messages** | Read followed conversations WhatsApp-style and search them. |
| **Settings** | Defaults, Claude model for drafts, keywords, WhatsApp installations. |

The pencil next to a conversation opens its menu: topics, history start date,
own folder, external references, and **Reply** (Claude drafts — copy and
paste them into WhatsApp yourself).

## Updating

```bash
cd ~/Applications/"WhatsApp Sync" && git pull && launchctl kickstart -k gui/$(id -u)/com.whatsapp-sync
```
Your settings are not touched by updates.

## Uninstall

```bash
cd ~/Applications/"WhatsApp Sync" && zsh servico/instalar.sh remove
```
Then delete the folder `~/Applications/WhatsApp Sync`, and, if you also want
to erase your settings, `~/Library/Application Support/WhatsApp Sync`. The
`.md` files already written in your folders stay until you delete them.

## Troubleshooting

| Symptom | Fix |
|---|---|
| The page does not open | Run the *Check that it works* command. If it is not `200`, see the log: `tail -50 ~/Library/Application\ Support/WhatsApp\ Sync/logs/servico.log` |
| Red banner about Full Disk Access | Do step 3 again, then click **Done, try again**. |
| `xcrun: error` or `cc: command not found` | Install the Command Line Tools (see *What you need*). |
| No conversations in Settings → WhatsApp installations | Open WhatsApp for Mac once, sign in, wait for chats to load. |
| "Claude Code was not found" in Reply | Install Claude Code and sign in; drafts are optional. |
| Address `whatsapp-sync.localhost` does not resolve | Use http://127.0.0.1:8765 instead. |
| Port 8765 is used by something else | Set `"porta"` in `~/Library/Application Support/WhatsApp Sync/config.json` to another number (1024–65535) and restart the service. |

## Privacy and where data lives

- **Your settings** (followed chats, topics, folders, keywords, screen
  preferences) live only in
  `~/Library/Application Support/WhatsApp Sync/config.json`, with a daily
  backup in `backups/`. They are never inside the app folder, so they can
  never be committed to git.
- The repository ships only **`config.example.json`**, the default settings a
  new install starts from. `.gitignore` blocks any other `config*.json`.
- The server listens only on this Mac (`127.0.0.1`); other computers cannot
  reach it. It has no password, so on a Mac shared by several user accounts,
  other accounts could reach it — install it only on your own Mac.
- `.md` files are written only into folders you chose, and the app only
  overwrites or deletes files it wrote itself (they start with
  `# WhatsApp — `).
- If a destination folder syncs to the cloud (Drive, iCloud…), a cloud icon
  shows next to it: those conversations will be uploaded by that service.
- Reply drafts are made by Claude Code on your Mac with your own Claude
  account: the conversation's recent history, your writing-style files and
  any reference files are sent to Claude for that request. Claude gets no
  tools (no files, no shell, no web). External connectors, if you enable them
  for a conversation, are limited to read tools — and if that filter cannot
  run, every connector tool is refused. Drafts may quote what Claude read in
  a connector, so read them before pasting.
- The app accepts API calls only from its own page: other websites you visit
  cannot read your chats or change settings, and the page cannot be embedded
  in another site.
- Writing-style and reference files must be `.md` or `.txt`; files inside
  `~/Library` (mail, messages, app data) are refused.
- Keep the app folder on your own Mac and only update it with `git pull`
  from the official repository: the code runs with Full Disk Access.

**Why a port number (8765)?** The app is a small web server on your Mac and
your browser talks to it; every local server needs a port number. You never
have to change it — it is fixed and no longer shown in Settings. Only if
another program already uses 8765, change it as described in
*Troubleshooting*.

## Contributing: no personal data, ever

This repository is public. **Rule number one: no personal data may ever be
committed** — no phone numbers, e-mail addresses, contact or group names,
WhatsApp ids, group invite links, personal folder paths or real settings, not
even in an old commit. Use fictional examples (`+55 11 91234-5678`).

- Turn on the checks once after cloning:
  ```bash
  git config core.hooksPath .githooks
  ```
  Before every commit and push, `scripts/privacy_check.py` scans the changes
  and the commit message, including every name, keyword and folder from your
  own `config.json`, and blocks the commit if it finds any of them. It prints
  matches masked, so the check itself never shows the data.
- Run it by hand any time: `python3 scripts/privacy_check.py --all` (current
  files) or `--history` (every version ever committed).
- The same check runs on GitHub for every push and pull request.

## Command line

- `python3 whatsapp_export.py` — run the app without the service (Terminal
  needs Full Disk Access).
- `python3 whatsapp_export.py --sync` — sync once and exit.
- `python3 whatsapp_export.py --novidades` / `--marcar-lido` — list messages
  Claude has not processed yet / mark them as processed.
- `zsh servico/instalar.sh rebuild` — rebuild the launcher (macOS will ask for
  Full Disk Access again).

---

## For AI assistants

You are helping a person install WhatsApp Sync on **their own Mac**. Follow
these steps in order, run the commands yourself when you can, and check each
result before moving on. Explain each step in one plain sentence; the person
may not be technical.

**Rules**
- Never read, print, copy or upload WhatsApp messages, contact names or phone
  numbers while installing. Do not open the WhatsApp database yourself.
- Never commit or push anything from `~/Library/Application Support/WhatsApp
  Sync/`. Never edit `config.example.json` with personal data.
- Do not use `sudo`. Nothing here needs it.
- Steps marked **HUMAN** can only be done by the person (macOS privacy
  settings and Apple dialogs). Tell them exactly what to click, then wait for
  them to confirm.

**Steps**
1. Check the Mac: `sw_vers -productVersion` (needs 13 or newer) and
   `xcode-select -p`. If the second fails, run `xcode-select --install` —
   **HUMAN** clicks *Install* in the dialog and waits for it to finish. Then
   re-check.
2. Check WhatsApp: `ls ~/Library/Group\ Containers | grep -i whatsapp`. If
   nothing prints, **HUMAN** must install WhatsApp for Mac, sign in and let
   the chats load.
3. Clone: run the command in *Steps → 1*. If `~/Applications/WhatsApp Sync`
   already exists, run `git -C ~/Applications/"WhatsApp Sync" pull` instead.
4. Install the service: run the command in *Steps → 2*. Expect
   `Service installed`. If `cc` fails, go back to step 1.
5. **HUMAN:** grant Full Disk Access exactly as in *Steps → 3* (items 1–2).
   Wait until they confirm the switch is on, then run the `launchctl
   kickstart` command from item 3.
6. Verify: run the `curl` command from *Check that it works* and expect
   `200`. Then run
   `curl -s http://127.0.0.1:8765/api/chats | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if not d.get('erro') and d.get('fontes', 0) >= 1 else 'NO ACCESS: ' + str(d.get('erro')))"`
   — it prints only `OK` or the error, never chat data. Anything other than
   `OK` means Full Disk Access is not active yet: repeat step 5.
7. Optional: `claude --version` — if it fails, tell the person reply drafts
   need Claude Code, and that everything else works without it.
8. Open http://whatsapp-sync.localhost:8765 for the person and walk them
   through *First setup in the app*. Let them choose topics, folders and
   conversations themselves.

If anything fails, read the last lines of
`~/Library/Application Support/WhatsApp Sync/logs/servico.log` and use the
*Troubleshooting* table.

## License

MIT — see [LICENSE](LICENSE).
