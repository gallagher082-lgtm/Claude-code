# Errand Runner

A to-do list agent that lives in your Claude account.

- Live page: https://claude.ai/artifact/2u5CK2Eb8cb6h4Aoj9EzSP
- Source: `index.html` (republish with Claude's Artifact tool to update the same link)

## How it works
1. Paste your whole list, one task per line, and tap **Add tasks**.
2. Tap **Work through my list**. Each task gets its own Claude helper (up to 3 run at once; the rest queue).
3. Helpers can search Gmail, read threads, check Google Calendar, find free time, and search Google Drive.
4. Helpers **cannot send anything**. Emails and calendar invites come back as editable proposals.
   You tap **Send…**, then confirm, before anything goes out. You can also save emails as Gmail drafts.
5. If a helper needs info, it asks a question; answer it and the task re-runs.

Your list is stored privately per user (`data/users/<you>`), so it follows you to your phone.
Helpers run while the page is open (phone or desktop); your computer can be off.
