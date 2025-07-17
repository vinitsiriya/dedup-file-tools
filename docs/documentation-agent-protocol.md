## Step-by-Step Agentic Algorithm for Documentation Updates

1. **Identify the Feature or Change:**
   - Determine the new feature, bugfix, or change that requires documentation updates.

2. **Locate All Relevant Documentation Files:**
   - Refer to the list of main documentation files above.
   - Remember: all files are in `<doc-dir>` except `README.md` (root directory).

3. **Review Existing Documentation:**
   - Read the current contents of each relevant file before making changes.
   - Pay special attention to section structure and existing conventions.


4. **Update Files in Protocol Order:**
   - Follow the strict update order defined above (requirements, implementation, feature, global requirements, CLI, etc.).
   - For each file:
     - Update only the sections that are relevant to the change.
     - Avoid unnecessary edits or restructuring.
     - If a section is already up to date, leave it unchanged.
     - When updating CLI usage examples or automation/integration details (such as YAML config support), ensure these are reflected in all relevant documentation files (e.g., CLI docs, external tool integration docs, README), but only where contextually appropriate. Do not add information or headings where they are not relevant to the document's purpose or flow.
     - Always maintain the natural flow and structure of each document—do not insert abrupt or intrusive headings or information blocks. Blend updates with care and precision.
     - For complex or multi-faceted features, use multiple focused iterations to update different sections or document types, ensuring no section loses focus or clarity due to a single broad update.

5. **Integrate Carefully:**
   - Ensure new information fits naturally into the document.
   - Do not add new sections unless truly needed for clarity or protocol compliance.
   - Use minimal, precise language.

6. **Verify Consistency Across Docs:**
   - Check that all related documentation files are consistent and reference each other as needed.
   - Ensure no contradictions or outdated information remain.

7. **Document What Was Not Changed:**
   - If a file or section did not require changes, note this in your commit or update log.

8. **Final Review:**
   - Re-read all updated files to ensure clarity, accuracy, and protocol compliance.
   - Confirm that the documentation is ready for review or release.
# Documentation Agent Protocol

This protocol defines the strict order and rules for updating documentation when adding or updating a feature in the project.

---



## Main Documentation Files
**Location:**
- All documentation files listed below are located in `<doc-dir>` (the documentation directory),
  **except** for `README.md`, which is located in the root directory of the project.

- `<doc-dir>/feature/<feature>.md`
- `<doc-dir>/requirements/<feature>.md`
- `<doc-dir>/implementation/<feature>.md`
- `<doc-dir>/cli.md`
- `<doc-dir>/requirements.md`
- `<doc-dir>/requirements-test.md`
- `<doc-dir>/external_ai_tool_doc.md`
- `README.md` (root directory)

---


## Protocol for Updating Documentation When Adding or Updating a Feature

**1. Update the following in order for the new or changed feature (all in `<doc-dir>` except `README.md`):**
   - `<doc-dir>/requirements/<feature>.md` (define or update requirements for the feature)
   - `<doc-dir>/implementation/<feature>.md` (describe or update the implementation details)
   - `<doc-dir>/feature/<feature>.md` (document the feature for users and agents)

**2. Update global requirements and test documentation (in `<doc-dir>`):**
   - `<doc-dir>/requirements.md` (update overall requirements summary)
   - `<doc-dir>/requirements-test.md` (update test requirements and coverage)

**3. Update CLI and external tool documentation (in `<doc-dir>`):**
   - `<doc-dir>/cli.md` (update CLI usage, options, and examples)
   - `<doc-dir>/external_ai_tool_doc.md` (update if the feature involves or impacts external AI tools)

**4. Update the main project README:**
   - `README.md` (root directory; update quick start, features, and any relevant sections)

---


## Rules
- Always follow the order above. Do not skip or reorder steps.
- Each file (in `<doc-dir>` or root as specified) must be updated to reflect the new or changed feature before moving to the next file in the protocol.
- If a file does not require changes for the feature, explicitly note this in your commit or documentation update.
- All documentation must be clear, complete, and up to date before the feature is considered finished.
- Agents must read and follow this protocol for all documentation updates related to features.

---

_This protocol supersedes any previous instructions for documentation updates. For questions, consult the project owner._
