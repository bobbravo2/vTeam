Break down a Jira feature into Epics and Stories for any project (unrelated to this repository).

## Process:

### Step 1: Create Structural Outline
1. **Fetch Feature**: Get feature details using Jira issue key
2. **Get Context**: Ask user for project's tech stack, architecture, and constraints
3. **Create Placeholder Epics**: Use stella agent for initial draft of 3-7 Epics with empty placeholder Jira issues, linked as children to the passed Jira issue
4. **Olivia Review**: Have olivia agent review epic structure and provide specific suggested changes
5. **Lee Review**: Have lee agent review epic structure and provide specific suggested changes
6. **Taylor Review**: Have taylor agent review epic structure and provide specific suggested changes
7. **Final Structure**: Have stella agent incorporate feedback and do final refinement of the epic structure

### Step 2: Write User Stories
1. **Initial Draft**: Use lee agent to create user stories for the placeholder issues created in Step 1
2. **Olivia Review**: Have olivia agent review user stories and provide specific suggested changes
3. **Stella Review**: Have stella agent review user stories and provide specific suggested changes
4. **Taylor Review**: Have taylor agent review user stories and provide specific suggested changes
5. **Final Stories**: Have lee agent incorporate feedback and do final refinement of the user stories

### Step 3: Define Acceptance Criteria
1. **Initial Criteria**: Use olivia agent to create acceptance criteria for all issues' descriptions
2. **Stella Review**: Have stella agent review acceptance criteria and provide specific suggested changes
3. **Lee Review**: Have lee agent review acceptance criteria and provide specific suggested changes
4. **Taylor Review**: Have taylor agent review acceptance criteria and provide specific suggested changes
5. **Final Criteria**: Have olivia agent incorporate feedback and do final refinement of the acceptance criteria

## Input:
- Jira issue key
- Project context

## Output:
- Feature summary
- Created Epics and Stories with Jira keys and proper parent linking
- Complete user stories with acceptance criteria
- Implementation recommendations