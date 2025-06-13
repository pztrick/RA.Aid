# Planning Workflow

## Overview: Plan First, Execute Later

RA.Aid's planning workflow allows you to generate detailed implementation plans without executing any code. This powerful feature enables you to review, approve, and understand the AI's proposed approach before committing time and resources to execution.

### Why Use the Planning Workflow?

- **Review & Approve**: Examine the AI's proposed plan before any code changes are made
- **Cost & Safety**: Prevent unexpected behavior or costs by ensuring the plan is sound
- **Manual Guidance**: Generate high-quality plans that you can execute manually
- **Iterative Planning**: Refine and improve plans through multiple iterations
- **Documentation**: Create detailed implementation guides for your team

## How-To Guide: Generating and Extracting Plans

### Step 1: Generate the Plan

Use the `--research-and-plan-only` (or `-rap`) flag to enable planning mode. The agent will:

1. Perform research on your task
2. Generate research notes
3. Create a detailed implementation plan
4. Exit automatically without executing any code

```bash
# Generate a plan for building a snake game
ra-aid -m "Create a simple snake game using Pygame" --research-and-plan-only

# Using the short form
ra-aid -m "Add user authentication to my Flask app" -rap
```

### Step 2: Extract the Plan

After generating a plan, you can extract it using one of two commands:

#### Extract the Most Recent Plan

```bash
# Get the plan from the latest session
ra-aid extract-last-plan
```

This is the most common use case and will output the plan as clean markdown to your terminal.

#### Extract a Specific Plan

```bash
# Get the plan from a specific session ID
ra-aid extract-plan 123
```

If you don't specify a session ID, it defaults to the latest session:

```bash
# These commands are equivalent
ra-aid extract-plan
ra-aid extract-last-plan
```

### Step 3: Save and Review

You can save the plan to a file for easier review:

```bash
# Save the plan to a markdown file
ra-aid extract-last-plan > implementation-plan.md

# Or view it with your preferred pager
ra-aid extract-last-plan | less
```

## Common Workflows and Examples

### Example 1: The "Review and Approve" Workflow

This is the most common use case for the planning workflow:

```bash
# 1. Generate the plan
ra-aid -m "Refactor my_script.py to be more modular" --research-and-plan-only

# 2. Extract and review the plan
ra-aid extract-last-plan > refactor-plan.md
# (Review the plan in your editor)

# 3. If satisfied, execute the same task without the flag
ra-aid -m "Refactor my_script.py to be more modular"
```

### Example 2: Iterative Planning

Refine your plans through multiple iterations:

```bash
# 1. Generate initial plan
ra-aid -m "Build a weather CLI tool" --research-and-plan-only

# 2. Extract and review
ra-aid extract-last-plan
# (Decide the plan needs more features)

# 3. Generate improved plan
ra-aid -m "Build a weather CLI tool with current weather and 3-day forecast" --research-and-plan-only

# 4. Extract final plan
ra-aid extract-last-plan > weather-cli-plan.md
```

### Example 3: Manual Implementation Guide

Use RA.Aid to create detailed guides for manual implementation:

```bash
# 1. Generate comprehensive plan
ra-aid -m "Set up a new React project with TypeScript, ESLint, and testing" --research-and-plan-only

# 2. Extract as implementation guide
ra-aid extract-last-plan > react-setup-guide.md

# 3. Follow the guide manually, step by step
```

### Example 4: Team Planning and Documentation

Create plans for team review and collaboration:

```bash
# Generate plan for team review
ra-aid -m "Migrate our authentication system from JWT to OAuth2" --research-and-plan-only

# Extract and share with team
ra-aid extract-last-plan > migration-proposal.md
# (Share migration-proposal.md with your team for review)
```

## Related Commands

### Extract Research Notes

The planning workflow also generates detailed research notes that you can extract:

```bash
# Get research notes from the latest session
ra-aid extract-last-research-notes

# Save research notes to file
ra-aid extract-last-research-notes > research-findings.md
```

Research notes contain the AI's analysis and findings that inform the implementation plan.

### Custom Project State Directory

All commands support custom project state directories:

```bash
# Generate plan with custom directory
ra-aid -m "Build API" --research-and-plan-only --project-state-dir ~/my-project-state

# Extract plan from custom directory
ra-aid extract-last-plan --project-state-dir ~/my-project-state
```

## Technical Details

### Database Storage

Plans are stored in RA.Aid's SQLite database as markdown text:

- **Location**: `.ra-aid/pk.db` (or custom location with `--project-state-dir`)
- **Storage**: Plans are saved in the `plan` field of the `session` table
- **Format**: Markdown text for easy reading and formatting

### The Planning Process

When you use `--research-and-plan-only`:

1. **Research Phase**: The agent researches your task and gathers information
2. **Research Notes**: Calls `emit_research_notes` to store findings
3. **Plan Generation**: Creates a detailed implementation plan
4. **Plan Storage**: Calls `emit_plan` to save the plan to the database
5. **Automatic Exit**: The agent exits without proceeding to implementation

### Session Management

Each RA.Aid run creates a new session with a unique ID:

- Session IDs are displayed when RA.Aid starts
- Plans are associated with their session for easy retrieval
- Multiple sessions can exist simultaneously in the database

## Integration with Other Workflows

### Memory Management

The planning workflow integrates with RA.Aid's memory system:

- Plans can reference stored key facts and code snippets
- Research notes become part of the project's knowledge base
- Use `--wipe-project-memory` to reset if needed

### Project State Directory

Plans work seamlessly with custom project state directories:

```bash
# Generate plan in shared project directory
ra-aid -m "Add feature X" --research-and-plan-only --project-state-dir /team/shared/project-state

# Team members can extract the same plan
ra-aid extract-last-plan --project-state-dir /team/shared/project-state
```

### Normal Execution Workflow

After reviewing a plan, you can execute it by running the same command without `--research-and-plan-only`:

```bash
# Plan phase
ra-aid -m "Add error handling to database module" --research-and-plan-only

# Review phase
ra-aid extract-last-plan

# Execution phase (if plan looks good)
ra-aid -m "Add error handling to database module"
```

## Troubleshooting

### No Plan Found

**Problem**: `ra-aid extract-last-plan` returns "No plan found for the latest session."

**Solutions**:
- Ensure you used the `--research-and-plan-only` flag when generating the plan
- Check if the agent completed successfully (look for error messages in the output)
- Verify you're using the correct `--project-state-dir` if you specified one during planning

### Empty or Incomplete Plans

**Problem**: The extracted plan is empty or seems incomplete.

**Solutions**:
- The agent may have encountered an error before completing the plan
- Check the session logs in `.ra-aid/logs/` for error details
- Try running the planning command again with a more specific task description

### Finding Session IDs

**Problem**: You need to find a specific session ID.

**Solutions**:
- Session IDs are printed when RA.Aid starts: `"Initialized SessionRepository"`
- Use `ra-aid extract-plan` without an ID to get the latest session
- Inspect the database directly if needed (advanced users)

### Database Access Issues

**Problem**: Cannot access the plan database.

**Solutions**:
- Ensure the `.ra-aid` directory exists and is writable
- Check file permissions on the database file
- Verify the correct `--project-state-dir` if using a custom location
- Try `--wipe-project-memory` if the database is corrupted

### Research Notes Missing

**Problem**: `ra-aid extract-last-research-notes` finds no notes.

**Solutions**:
- Research notes are only generated in `--research-and-plan-only` mode
- Ensure the research phase completed successfully
- Check for error messages during the research phase

## Best Practices

### When to Use Planning Mode

- **Large or Complex Tasks**: Use planning for significant changes or new features
- **Unfamiliar Domains**: When working with technologies you're less familiar with
- **Team Collaboration**: Generate plans for team review before implementation
- **Cost-Sensitive Operations**: When you want to understand the scope before committing resources

### Plan Review Checklist

When reviewing extracted plans:

- ✅ Does the plan address all requirements?
- ✅ Are the proposed technologies appropriate?
- ✅ Is the implementation approach sound?
- ✅ Are there any missing steps or considerations?
- ✅ Does the plan fit your timeline and resource constraints?

### Combining with Other Features

- Use with `--project-state-dir` for organized project management
- Combine with memory management for context-aware planning
- Leverage custom tools for domain-specific planning capabilities

## Examples

### Planning a Database Migration

```bash
# Generate migration plan
ra-aid -m "Migrate user table to add email verification fields" --research-and-plan-only

# Extract and review
ra-aid extract-last-plan > db-migration-plan.md

# Extract research for additional context
ra-aid extract-last-research-notes > migration-research.md
```

### Planning a New Feature

```bash
# Plan a complex feature
ra-aid -m "Add real-time chat functionality to the web app" --research-and-plan-only

# Save comprehensive documentation
ra-aid extract-last-plan > chat-feature-plan.md
ra-aid extract-last-research-notes > chat-research.md

# Review both files before implementation
```

### Planning with Custom Tools

```bash
# Generate plan using custom tools
ra-aid -m "Optimize database queries" --research-and-plan-only --custom-tools ./tools/db_tools.py

# Extract plan that includes custom tool recommendations
ra-aid extract-last-plan > optimization-plan.md
```