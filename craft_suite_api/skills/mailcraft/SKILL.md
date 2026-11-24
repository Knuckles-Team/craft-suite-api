---
name: mailcraft
description: MailCraft mail client — mailboxes, folders, messages, contacts, calendar and tasks in a .mailcraft mailbox; read, write and send mail.
---

# Mailcraft

## When to use

MailCraft mail client — mailboxes, folders, messages, contacts, calendar and tasks in a .mailcraft mailbox; read, write and send mail.

## Activation

Call `registry_activate` with the namespace `mailcraft` before using any `mailcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `mailcraft_batch` | Run commands in order; stops at the first error unless keepGoing. |
| `mailcraft_click` | Click at window coordinates, or on something by kind and id as ui_inspect lists it (desktop app only). |
| `mailcraft_execute` | Run one command by id with params, e. |
| `mailcraft_import_file` | Bring a file into the mailbox: messages (. |
| `mailcraft_inspect_mailbox` | Accounts and how much of everything the mailbox holds. |
| `mailcraft_key` | Press a key with modifiers (desktop app only), e. |
| `mailcraft_list_commands` | Every MailCraft command: id, label, ribbon location, shortcut and params. |
| `mailcraft_list_contacts` | People of every account, unless `account` names one, optionally filtered by name, company or address. |
| `mailcraft_list_events` | What is on the calendar between two days (inclusive), recurring events expanded. |
| `mailcraft_list_folders` | Every account's folder tree with message and unread counts. |
| `mailcraft_list_messages` | The message list of a folder, newest first, optionally narrowed by a search (from:, subject:, has:attachment, is:unread, before:/after:YYYY-MM-DD…). |
| `mailcraft_list_tasks` | To-do items of every account, unless `account` names one. |
| `mailcraft_open_mailbox` | Open a . |
| `mailcraft_parity` | MailCraft's command coverage of the mail-client feature catalog. |
| `mailcraft_read_message` | One message in full: sender and recipients, body text, attachments, and `authentication` (spf, dkim, dkimDomain, dmarc: what the account's own mail server wrote in its topmost Authentication-Results; absent when it wrote none; dkimDomain is the signer's choice, so it comes framed). |
| `mailcraft_save_mailbox` | Save the mailbox to a . |
| `mailcraft_screenshot` | Screenshot of the whole MailCraft window (desktop app only). |
| `mailcraft_send_message` | Write and send a new message. |
| `mailcraft_status` | Whether the mailbox is open. |
| `mailcraft_ui_inspect` | UI state: module, tab, dialog, selection, and where the visible items are on screen (desktop app only). |

## Functionalities

- `mailcraft-open_mailbox` — Open a mailbox file or start from the sample mailbox, and inspect what it holds.
- `mailcraft-read_messages` — List a folder's messages and read one in full.
- `mailcraft-send_message` — Write and send a new message from an account.
- `mailcraft-save_mailbox` — Save the mailbox back to a .mailcraft file.
