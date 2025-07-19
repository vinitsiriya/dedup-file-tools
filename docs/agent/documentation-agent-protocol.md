## Step-by-Step Documentation Update Protocol (Generic)

1. **Identify the Feature or Change:**
   - Determine the new feature, bugfix, or change that requires documentation updates in the <project>.

2. **Locate All Relevant Documentation Files:**
   - Refer to the documentation directory structure for <project>.
   - Most documentation is under `docs/`, organized by module/component, feature, and perspective.
   - The main `README.md` is in the project root.
   - Example structure:
     - `docs/agent/` — agent protocols, bootstrap, and meta docs
     - `docs/commons/` — shared/manual test docs
     - `docs/<module>_commons/` — shared module docs
     - `docs/<module>/` — module/component docs, organized as below
         - `developer_reference/feature/`, `developer_reference/implementation/`, `developer_reference/requirements/` — feature, implementation, and requirements docs
         - `developer_reference/planning/`, `developer_reference/standalone/`, `developer_reference/user_prepective/` — planning, standalone, and CLI/user docs
   - See the <project> for the full up-to-date structure.

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



## Main Documentation Files & Locations (Pattern)
**Location:**
- All documentation is under `docs/` unless otherwise noted.
- Key locations (replace <module> with your module/component name):
  - `docs/agent/` — agent protocols, bootstrap, meta
  - `docs/commons/` — shared/manual test docs
  - `docs/<module>_commons/` — shared module docs
  - `docs/<module>/` — module/component docs:
    - `developer_reference/feature/` — feature docs
    - `developer_reference/implementation/` — implementation docs
    - `developer_reference/requirements/` — requirements docs
    - `developer_reference/planning/` — planning docs
    - `developer_reference/standalone/` — standalone/external tool docs
    - `developer_reference/user_prepective/` — CLI/user docs
  - `README.md` — project root

---



## Protocol for Updating Documentation When Adding or Updating a Feature

**1. Update the following in order for the new or changed feature (all in the appropriate subdirectory under `docs/<module>/developer_reference/`):**
   - `docs/<module>/developer_reference/requirements/features/<feature>.md` (define or update requirements for the feature)
   - `docs/<module>/developer_reference/implementation/<feature>.md` (describe or update the implementation details)
   - `docs/<module>/developer_reference/feature/<feature>.md` (document the feature for users and agents)

**2. Update global requirements and test documentation for the module:**
   - `docs/<module>/developer_reference/requirements/requirements.md` (overall requirements summary)
   - `docs/<module>/developer_reference/requirements/requirements-test.md` (test requirements and coverage)

**3. Update CLI and external tool documentation for the module:**
   - `docs/<module>/developer_reference/user_prepective/cli.md` (CLI usage, options, and examples)
   - `docs/<module>/developer_reference/standalone/external_ai_tool_doc.md` (external AI tool integration, if relevant)

**4. Update the main project README:**
   - `README.md` (root directory; update quick start, features, and any relevant sections)

**General Pattern:**
For each module/component in <project>, documentation is organized as:

```
docs/<module>/
  developer_reference/
    feature/
    implementation/
    requirements/
      features/
  planning/
  standalone/
  user_prepective/
```
Where `<module>` is the tool or component name, and `<feature>` is the feature being documented. Always follow this pattern for new features or changes in any project.

---


## Rules
- Always follow the order above. Do not skip or reorder steps.
- Each file (in `<doc-dir>` or root as specified) must be updated to reflect the new or changed feature before moving to the next file in the protocol.
- If a file does not require changes for the feature, explicitly note this in your commit or documentation update.
- All documentation must be clear, complete, and up to date before the feature is considered finished.
- Agents must read and follow this protocol for all documentation updates related to features.

---

_This protocol supersedes any previous instructions for documentation updates. For questions, consult the project owner._
