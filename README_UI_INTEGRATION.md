# MemoryAI UI — Integration Notes

This UI was built strictly against your existing `src/` backend.
Nothing under `src/`, `requirements.txt`, or `README.md` was
modified. These are the only new files:

```
app.py
ui/
├── __init__.py
├── styles.py
├── state.py
├── components.py
├── chat.py
├── memory_view.py
├── profile_view.py
├── learning_view.py
└── system_view.py
.streamlit/
└── config.toml
```

## How the UI talks to your backend

`ui/state.py` imports `src.agent` exactly once per process (cached
with `st.cache_resource`, so Mem0/Qdrant/the embedding model aren't
re-initialised on every Streamlit rerun). Every page calls existing
functions on that module — `run_agent`, `search_memory`,
`get_all_memories`, `delete_memory`, `get_user_profile`,
`get_learning_summary`, `get_learning_history`, `feedback_system`,
`save_new_memory`, `update_user_profile`, `save_learning_log` — no
new memory, feedback, evaluation, or planning logic was written.

## Two things the current backend doesn't expose (by design, not a bug)

I didn't fake these — flagging them so you can decide if/when to add them:

1. **Per-memory categories aren't persisted.** `save_new_memory()` in
   `src/agent.py` classifies a memory (`fact`, `preference`, `goal`, ...)
   but only stores the plain text via `memory.add()` — the category is
   never saved as metadata. So the Memory page can't show a real
   category tag per stored memory. If you want this, the smallest
   change would be adding `metadata={"category": category}` to the
   `memory.add()` call in `save_new_memory()`, then reading
   `item.get("metadata", {}).get("category")` in `get_all_memories()`
   results.

2. **Tool usage (calculator / web search) isn't returned.**
   `run_agent()` decides and executes tool calls internally but
   only returns the final answer string. There's no reliable way to
   show a "🔧 Calculator used" badge without either (a) having
   `run_agent()` also return the tool name(s) it used, or (b) some
   other signal. I left this out of the chat UI rather than guessing
   from the answer text. Everything else in the spec (memories used,
   new memory saved, evaluation score, feedback → learning) is backed
   by real data returned by the backend.

## Additional UI package required

```powershell
pip install streamlit
```

Nothing else — `requirements.txt` already covers `mem0ai`, `ollama`,
`qdrant-client`, `sentence-transformers`, `ddgs`, `python-dotenv`, etc.

## Run it

```powershell
cd C:\memory-ai-agent
.\.venv\Scripts\Activate.ps1
pip install streamlit
streamlit run app.py
```

Copy `app.py`, the `ui/` folder, and the `.streamlit/` folder into
your project root (next to `src/`) first.

## Testing checklist

```
[ ] Streamlit starts (streamlit run app.py)
[ ] Chat page loads, sidebar shows Ollama / Memory backend status
[ ] User can send a message and the existing agent responds
[ ] Conversation persists during the session
[ ] "N relevant memories used" indicator appears when memories exist
[ ] New-memory indicator appears when the backend extracts one
[ ] Memory page displays real memories from Mem0
[ ] Memory deletion works (single + delete-all with confirmation)
[ ] Profile page shows real profile data, "Regenerate" re-runs it
[ ] 👍 / 👎 feedback buttons save feedback and show the learned statement
[ ] Learning dashboard shows real totals, charts, and recent learning
[ ] System page shows live Ollama / model / memory-backend status
[ ] No secrets (.env) are displayed anywhere
[ ] src/ files are byte-for-byte unchanged
```
