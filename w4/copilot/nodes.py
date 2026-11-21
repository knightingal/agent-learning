import json
import shlex
import subprocess
from pathlib import Path
from langgraph.types import interrupt

from .agents import StructuredAgent, build_agents
from .harness import Harness
from .retrieval import search_knowledge
from .state import CopilotState

ROOT = Path(__file__).resolve().parent.parent
HARNESS = Harness(ROOT)
PLANNER, RESEARCHER, CODER, REVIEWER = build_agents()
SAFE_COMMANDS = {"python", "python3", "pytest", "gradle", "./gradlew"}


# def _run(agent, prompt: str):
#   print("_run prompt:" + prompt)
#   result = Runner.run_sync(agent, prompt, max_turns=8)
#   output = result.final_output
#   print(output)
#   return output

def _run(agent: StructuredAgent, prompt: str):
  return agent.run(prompt)


def initialize_node(state: CopilotState) -> dict:
  HARNESS.trace("run_stated", {"request": state["request"]})
  return {"iteration": 0, "max_iterations": state.get("max_iterations", 4)}


def plan_node(state: CopilotState) -> dict:
  print("enter plan_node")

  output = _run(PLANNER, f"User request:\n{state['request']}")
  plan = output.model_dump()
  HARNESS.trace("plan_created", plan)
  return {"plan": plan}


def research_node(state: CopilotState) -> dict:
  plan_json = json.dumps(state["plan"], ensure_ascii=False, indent=2)
  evidence = search_knowledge(ROOT, state["request"] + " " + plan_json)
  snapshot = HARNESS.read_workspace_snapshot()
  prompt = (
    f"Request:\n{state["request"]}\n\nPlan\n{plan_json}\n\n"
    f"Knowledge excerpts:\n{json.dumps(evidence, ensure_ascii=False, indent=2)}\n\n"
    f"Workspace snapshot:\n{snapshot}"
  )
  output = _run(RESEARCHER, prompt)
  research = output.model_dump()
  HARNESS.trace("reseach_completed", research)
  return {"research": research}


def code_node(state: CopilotState) -> dict:
  prompt = (
    f"Request:\n{state['request']}\n\n"
    f"Plan\n{json.dumps(state['plan'], ensure_ascii=False, indent=2)}\n\n"
    f"Research:\n{json.dumps(state['research'], ensure_ascii=False, indent=2)}\n\n"
    f"Current workspace:\n{HARNESS.read_workspace_snapshot()}\n\n"
    f"Previous review, if any:\n{json.dumps(state.get('review', {}), ensure_ascii=False, indent=2)}"
  )
  output = _run(CODER, prompt)
  coding = output.model_dump()
  HARNESS.trace("code_proposed", {"summary": coding["summary"], "files": [x["path"] for x in coding["files"]]})
  return {"coding": coding}


def approval_node(state: CopilotState) -> dict:
  proposal = {
    "action": "write_files",
    "summary": state["coding"]["summary"],
    "files": [{"path": x["path"], "purpose": x["purpose"]} for x in state["coding"]["files"]],
    "allowed_decisions": ["approve", "reject"],
  }
  decision = interrupt(proposal)
  approved = isinstance(decision, dict) and decision.get("decision") == "approve"
  HARNESS.trace("approval_decision", {"approved": approved})
  return {"approval": {"approved": approved, "raw": decision} }


def apply_node(state: CopilotState) -> dict:
  files = HARNESS.apply_files(state["coding"]["files"])
  return {"applied_files": files}


def reject_node(_state: CopilotState) -> dict:
  return {"final_report": "Change rejected by human reviewer. No files were written."}


def verify_node(state: CopilotState) -> dict:
  results = []
  for command in state["coding"].get("verification_commands", [])[:5]:
    print("======")
    print(command)
    print("======")
    if command.startswith("./gradlew"):
      command = "chmod u+x ./gradlew; " + command
      print("======")
      print(command)
      print("======")

    
    argv = shlex.split(command)
    # if not argv or argv[0] not in SAFE_COMMANDS:
    #   results.append({"command": command, "status": "blocked", "output": "Command is not allow-listed."})
    #   continue
    try:
      completed = subprocess.run(
        argv,
        cwd=HARNESS.workspace,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
      )
      results.append({
        "command": command,
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "output": (completed.stdout + completed.stderr)[-5000:]
      })
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
      results.append({"command": command, "status": "error", "output": str(exc)})
  verification = {"results": results, "all_passed": bool(results) and all(x["status"] == "passed" for x in results)}
  HARNESS.trace("verification_completed", verification)
  return {"verification": verification}


def review_node(state: CopilotState) -> dict:
  prompt = (
    f"Request:\n{state['request']}\n\nPlan:\n{json.dumps(state['plan'], ensure_ascii=False)}\n\n"
    f"Research:\n{json.dumps(state['research'], ensure_ascii=False)}\n\n"
    f"Verification:\n{json.dumps(state['verification'], ensure_ascii=False)}\n\n"
    f"Workspace after change:\n{HARNESS.read_workspace_snapshot()}"
  )
  output = _run(REVIEWER, prompt)
  review = output.model_dump()
  HARNESS.trace("review_completed", review)
  return {"review": review}


def route_after_approval(state: CopilotState) -> str:
  return "apply" if state["approval"]["approved"] else "reject"


def route_after_review(state: CopilotState) -> str:
  if state["review"]["approved"]:
    return "finalize"
  if state.get("iteration", 0) < state.get("max_iterations", 4):
    return "revise"
  return "finalize"


def revise_node(state: CopilotState) -> dict:
  return {"iteration": state.get("iteration", 0) + 1}


def finalize_node(state: CopilotState) -> dict:
  if state.get("final_report"):
    report = state["final_report"]
  else:
    report = "\n".join([
      "# Mobile Enterprise Copilot Run",
      "",
      "# Request",
      state["request"],
      "",
      "## Plan",
      json.dumps(state.get("plan", {}), ensure_ascii=False, indent=2),
      "",
      "## Research",
      json.dumps(state.get("research", {}), ensure_ascii=False, indent=2),
      "",
      "## Applied files",
      *[f"- `{item}`" for item in state.get("applied_files", [])],
      "",
      "## Verification",
      json.dumps(state.get("verification", {}), ensure_ascii=False, indent=2),
      "",
      "## Review",
      json.dumps(state.get("review", {}), ensure_ascii=False, indent=2),
    ])
  path = HARNESS.reports / "final_report.md"
  path.write_text(report, encoding="utf-8")
  HARNESS.trace("run_finished", {"report_path": str(path)})
  return {"final_report": report, "report_path": str(path)}
