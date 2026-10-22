---
name: access-requests
description: Review pending Hugging Face access requests on the gated Hebrish models and datasets, show them with their form answers, and accept or reject the ones the maintainer decides on, following the Hebrish terms (non-commercial free, commercial needs a licence). Optionally adds accepted users who opted in to the Hebrish newsletter. Use when asked who has requested access, to check, approve or reject access requests, or after a release.
---

# Hebrish gated access requests

## Access

- **Maintainer access only:** people with the write or admin role in the
  [Hebrish organisation on Hugging Face](https://huggingface.co/Hebrish), using a token with that
  access in `HF_TOKEN` (or `hf auth login`). Deciding requests needs it (a read token or a non-member gets
  HTTP 403, per the huggingface_hub docs); listing them was tested with such a token only.
- **Anyone else:** there is nothing to review without that access. If your own request has been
  waiting, or you want to report a problem with the gate (a broken form, a wrong address), open an
  issue on [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues), for example
  `Hugging Face: access request to Hebrish/Sabich pending`, or e-mail access@hebrish.app (the
  project's one access-request address since 2026-10-22). Do not put anyone else's details in the issue.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *access-requests*, for the maintainer setup.

Hebrish is Daniel Rosehill's one-person project (<https://hebrish.app>). Written
2026-10-22; the dry run was tested against the live org that day.

## Requesters' data stays out of files

Usernames, full names, e-mail addresses and form answers are personal data. Show them in the chat
only; **never write them to any file in a repository** (no logs, notes, planning entries, commit
messages or issues). The script never prints e-mail addresses at all; do not redirect its output into a
repo. When you report, count requests and name repos; the maintainer sees the people in the chat.

## Policy

From the [Hebrish terms of use](https://hebrish.app/terms) and the maintainer's decisions (2026-10-21):

1. Every gated Hebrish repo uses **manual** review: the maintainer decides each request. Accept or
   reject **only the users the maintainer names**, never on your own judgement, never in bulk because
   the requests "look fine".
2. **Non-commercial use is free:** personal dictation, research, teaching, non-profits, open-source
   projects that are not sold. A request with a plausible non-commercial intended use and the terms
   checkbox ticked is normally accepted, but it is still the maintainer's call.
3. **Commercial use needs a commercial licence:** telephony, call centres, voice agents, any product or
   hosted service sold to others, and internal use for a business's commercial operations. Flag such a
   request clearly and let the maintainer decide; the requester is pointed to access@hebrish.app (the
   standard access-request address since 2026-10-22; older cards and pages may still name
   access-requests@hebrish.app, which the `hf-audit` and `model-cards` audits flag).
4. **Empty or thin answers:** gated datasets have no request form (as of 2026-10-22), so their requests
   arrive with no answers. Offer the requester's public profile (`--profiles`) and let the maintainer
   decide or ask the requester by e-mail.
5. **Newsletter:** only users who ticked the newsletter checkbox on the gate form are ever added to the
   Hebrish newsletter. As of 2026-10-22 no gate form has that checkbox yet, so `--subscribe` finds
   nobody; it is there for when the form gains it.

## Steps

Script: `${CLAUDE_PLUGIN_ROOT}/skills/access-requests/scripts/access_requests.py`. If
`CLAUDE_PLUGIN_ROOT` is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/access-requests/scripts/access_requests.py` inside it.

```bash
R="uv run --no-project --with huggingface_hub python3 ${CLAUDE_PLUGIN_ROOT}/skills/access-requests/scripts/access_requests.py"
$R --profiles                                   # dry run: every gated model and dataset, pending requests
```

1. **List.** Run the dry run (about 30 seconds; it walks every model and dataset in the org). Output:
   `repos` (each gated repo, its mode, pending count) and `pending` (repo, user, full name, requested
   at, form answers, whether the form was filled in, newsletter tick, and with `--profiles` the public
   profile counts and URL).
2. **Show the list** to the maintainer as a table: repo, user, full name, requested, organisation,
   intended use, terms ticked, and your reading against the policy (non-commercial / commercial: flag /
   no answers). No e-mail addresses.
3. **Wait for the decision.** Then, for exactly the users named:
   ```bash
   $R --accept alice,bob --apply                                   # every repo each asked for
   $R --accept alice --repo Hebrish/Yiddish-Sentences --apply      # one repo
   $R --reject carol --reason "Commercial use: see hebrish.app/terms" --apply
   ```
   Run without `--apply` first if the list changed since step 1; `not_pending` lists names that matched
   no pending request (typo, or already decided).
4. **Newsletter (optional, maintainer with the newsletter's key):** `$R --subscribe` lists accepted
   users who ticked the box; `$R --subscribe --apply` with `BUTTONDOWN_API_KEY` (the Hebrish
   newsletter's key, never another newsletter's) adds them with tag `gated-access`. Buttondown sends
   its own double opt-in mail. Status 201 = created; 400 usually means already subscribed.
5. **Verify the thing:** run the dry run again; the decided users are gone from `pending`. Spot-check
   one repo's list at `https://huggingface.co/<repo>/settings/gated-user-access` (models) or
   `https://huggingface.co/datasets/<repo>/settings/gated-user-access` (datasets).

If the API fails, the same lists and buttons are on those settings pages in a browser logged in as an
org member.

## API facts (huggingface_hub 2.2.0)

| Call | Detail | Verified |
| --- | --- | --- |
| `list_pending_access_requests(repo, repo_type=...)` | `GET /api/{models,datasets}/{repo}/user-access-request/pending`; also `/accepted`, `/rejected`. Returns a **generator** in 2.x: wrap in `list()` before `len()` or `+` | 2026-10-22 |
| `AccessRequest` fields | `username`, `fullname`, `email`, `timestamp`, `status`, `fields` (form answers, keyed by the field label in the card's `extra_gated_fields`; `{}` when the gate has no form). `email` is filled in for org members' tokens | 2026-10-22 (one real dataset request) |
| `accept_access_request(repo, user, repo_type=...)` | `POST .../user-access-request/handle` with `{"user", "status": "accepted"}`; 403 with a read token or without write/admin role; 400 if the repo is not gated | docs; not yet run |
| `reject_access_request(repo, user, repo_type=..., rejection_reason=...)` | same endpoint, `status: "rejected"`, `rejectionReason`; `rejection_reason` is a **required keyword** in 2.x (pass `None` for none) | signature 2026-10-22; not yet run |
| `model_info(id).gated` / `dataset_info(id).gated` | `"manual"`, `"auto"` or `False` | 2026-10-22 |
| Gate form | the card's `extra_gated_prompt` and `extra_gated_fields` front matter | 2026-10-21 |

As of 2026-10-22 the gated repos are: every Hebrish ASR model and build except the token classifier,
`Hebrish/TTS-V1` (Meorav) and Boxty; `Hebrish/Parakeet-TDT-0.6B-v2-Tech-And-Accent` is gated
**automatic** (requests are accepted without review); and six datasets
(`English-Hebrew-Mixed-Sentences`, `English-Hebrew-Codeswitching-ASR-Benchmark`, `Yiddish-Sentences`,
`Jewish-Religious-Terminology-Sentences`, `Parakeet-V2-Blend-All`, `Parakeet-V2-Blend-No-Hebrew`).
The script reads this live each run, so the list here is only orientation.
