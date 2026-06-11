# Stack Selection

status: unselected
selected_profile: none
note: stack is selected in the first project chat

Production implementation must not begin until a stack profile is selected here or the user explicitly confirms a custom approach.

## Available Profiles

See `agents/harness/stack-options.md`.

## Selection Notes

- Use `python tools/llm_wiki.py stack list` to review profiles.
- Use `python tools/llm_wiki.py stack select <profile>` to record the selected profile.
- The command records the choice only. It does not install dependencies, scaffold a new stack, or modify `frontend/`.
