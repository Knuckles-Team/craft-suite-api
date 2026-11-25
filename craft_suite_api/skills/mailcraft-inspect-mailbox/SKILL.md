---
name: mailcraft-inspect-mailbox
description: Inspect a mailbox — open the sample mailbox, read its accounts, folders and messages, read a message in full, list the contacts, and round-trip the mailbox back as data.
---

# Inspect a mailbox

## When to use

A mailbox needs to be read and summarized — its accounts, folders, messages and contacts — without touching a live mail account. The built-in sample mailbox stands in for one; the same steps work on a real mailbox an owner has opened.

## Inputs

- `${message_id}`: the id of the message to read in full, taken from the message list.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open mailbox between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `mailcraft_open_mailbox` | `{"sample": true}` | Open the mailbox; the built-in sample mailbox needs no account. With a real mailbox the owner's account signs in first. |
| 2 | `mailcraft_status` | `{}` | The app's status: what is open and ready. |
| 3 | `mailcraft_inspect_mailbox` | `{}` | The mailbox's shape: accounts and their counts. |
| 4 | `mailcraft_list_folders` | `{}` | The folder tree with counts (inbox, drafts, sent, deleted, archive, junk, outbox, custom folders). |
| 5 | `mailcraft_list_messages` | `{}` | The messages, newest first; take the id of the one to read — it names `${message_id}`. |
| 6 | `mailcraft_read_message` | `{"id": "${message_id}"}` | Read that message in full: subject, from, to, date, body. |
| 7 | `mailcraft_list_contacts` | `{}` | The contacts in the mailbox. |
| 8 | `mailcraft_save_mailbox` | `{}` | Round-trip the mailbox back as data: no path argument (data mode) — the mailbox comes back as base64 in the result, decoded to a `.mailcraft` file. |

## Outputs

The round-tripped mailbox as data in the save result (`data` base64, `bytes` its size); decoded it is a `.mailcraft` mailbox file with the same accounts and folders. The open mailbox stays in the app's session; sending (`mailcraft_send_message`) needs a real account and the per-call `confirmed` flag and is not part of this workflow.

## Verify

The counts agree end to end: the accounts the inspect call names, the folder tree with its counts, and the message list all describe the same mailbox; the read message's fields match its list entry; the decoded mailbox round-trips the same accounts and folders (compare its base64 size to the save result's `bytes`).

## Notes

- Mailcraft runs headless in data mode: the agent passes and receives file content as base64 and never names files on the host, so `mailcraft_save_mailbox` takes no path — the file comes back in the result instead.
- Only the `mailbox` and `send` consent classes are granted to the connector; the other classes (delete, accounts, settings, input) stay refused, so permanent deletion and credential changes are not possible through it.
- `mailcraft_list_commands` lists the app's full command catalogue for calls beyond the typed tools this skill walks.

## Refusals

An app is in one lifecycle state: `warming` while its command registry loads, `Ready`, `Degraded` after a failed load, Backoff once its retries are used. A call to a `warming` app answers `APP_WARMING` (retryable, `retry_after_s`): wait that long and call again. A call to a `Degraded` or `Backoff` app answers `APP_REGISTRY_UNREADABLE` (retryable): retry after `retry_after_s`; a `Backoff` app has used its retries and needs an operator. Report any other refusal verbatim; never retry past it.
