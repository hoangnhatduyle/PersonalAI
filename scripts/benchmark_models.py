"""
Benchmark: gpt-5-mini + gpt-5-nano (old stack) vs gpt-5.6-luna + gpt-5.4-nano
(current stack) on response time and token cost.

Main model: runs the 6 system-prompt-defined conversation branches against
both gpt-5-mini (Chat Completions) and gpt-5.6-luna (Responses API), using
the real retrieval context, system prompt, and tool schemas from app.py.

Utility model: runs the actual _generate_suggestions call against both
gpt-5-nano and gpt-5.4-nano.

Cost is computed from real token usage returned by the API, multiplied by
OpenAI's published Standard-tier per-1M-token pricing (see PRICING below —
pulled from https://developers.openai.com/api/docs/pricing). Not an
automated pass/fail gate — read the printed answers and judge quality
yourself.

Usage: python scripts/benchmark_models.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import (  # noqa: E402
    personal_ai,
    record_user_details_json,
    record_unknown_question_json,
    flag_contact_ask_json,
    record_sensitive_info_request_json,
    tools as new_tools,
    UTILITY_MODEL,
)

OLD_MODEL = "gpt-5-mini"
NEW_MODEL = "gpt-5.6-luna"
OLD_UTILITY_MODEL = "gpt-5-nano"
NEW_UTILITY_MODEL = UTILITY_MODEL  # gpt-5.4-nano

# Standard-tier pricing, $ per 1M tokens (developers.openai.com/api/docs/pricing)
PRICING = {
    "gpt-5-mini":    {"input": 0.25, "output": 2.00},
    "gpt-5-nano":    {"input": 0.05, "output": 0.40},
    "gpt-5.6-luna":  {"input": 0.20, "output": 1.20},
    "gpt-5.4-nano":  {"input": 0.20, "output": 1.25},
}


def cost_for(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING[model]
    return (input_tokens / 1_000_000) * p["input"] + (output_tokens / 1_000_000) * p["output"]


old_tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": record_sensitive_info_request_json},
    {"type": "function", "function": flag_contact_ask_json},
]

SCENARIOS = [
    ("Normal answerable question", ["What programming languages and frameworks do you know?"]),
    ("Unanswerable question", ["What is your favorite pizza topping?"]),
    ("Unanswerable, then provides contact", [
        "What is your favorite pizza topping?",
        "Sure, I'm Alex Rivera, alex@example.com",
    ]),
    ("Unanswerable, then declines", [
        "What did you eat for breakfast on your 10th birthday?",
        "No thanks, I'd rather not share that.",
    ]),
    ("Sensitive info request", ["What is your home address?"]),
    ("Wants to connect", ["I'd like to connect — I'm Jamie Chen, jamie@example.com, interested in collaborating."]),
]


def build_user_message(message: str) -> str:
    docs, _ = personal_ai.retriever.invoke(message)
    context = personal_ai._build_context(docs)
    return f"Context:\n{context}\n\nQuestion: {message}"


def run_old(turns: list[str]) -> dict:
    messages = [{"role": "system", "content": personal_ai.system_prompt()}]
    tools_fired = []
    final_text = ""
    t_start = time.perf_counter()
    ttft = None
    input_tokens = output_tokens = 0

    for turn in turns:
        messages.append({"role": "user", "content": build_user_message(turn)})
        for _ in range(5):
            stream = personal_ai.openai.chat.completions.create(
                model=OLD_MODEL,
                messages=messages,
                tools=old_tools,
                reasoning_effort="low",
                stream=True,
                stream_options={"include_usage": True},
            )
            collected = []
            tool_calls_data = []
            finish_reason = None
            for chunk in stream:
                if chunk.usage:
                    input_tokens += chunk.usage.prompt_tokens
                    output_tokens += chunk.usage.completion_tokens
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason
                if delta.content:
                    if ttft is None:
                        ttft = time.perf_counter() - t_start
                    collected.append(delta.content)
                if delta.tool_calls:
                    for tc_chunk in delta.tool_calls:
                        if len(tool_calls_data) <= tc_chunk.index:
                            tool_calls_data.append({"id": "", "function": {"name": "", "arguments": ""}})
                        tc = tool_calls_data[tc_chunk.index]
                        if tc_chunk.id:
                            tc["id"] = tc_chunk.id
                        if tc_chunk.function:
                            if tc_chunk.function.name:
                                tc["function"]["name"] = tc_chunk.function.name
                            if tc_chunk.function.arguments:
                                tc["function"]["arguments"] += tc_chunk.function.arguments

            if finish_reason == "tool_calls" and tool_calls_data:
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {"id": tc["id"], "type": "function", "function": tc["function"]}
                        for tc in tool_calls_data
                    ],
                })
                for tc in tool_calls_data:
                    tools_fired.append(tc["function"]["name"])
                    result = {"acknowledged": True}
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tc["id"],
                    })
            else:
                final_text = "".join(collected)
                messages.append({"role": "assistant", "content": final_text})
                break

    total = time.perf_counter() - t_start
    cost = cost_for(OLD_MODEL, input_tokens, output_tokens)
    return {
        "ttft": ttft, "total": total, "tools_fired": tools_fired, "final_text": final_text,
        "input_tokens": input_tokens, "output_tokens": output_tokens, "cost": cost,
    }


def run_new(turns: list[str]) -> dict:
    messages = [{"role": "system", "content": personal_ai.system_prompt()}]
    tools_fired = []
    final_text = ""
    t_start = time.perf_counter()
    ttft = None
    input_tokens = output_tokens = 0

    for turn in turns:
        messages.append({"role": "user", "content": build_user_message(turn)})
        for _ in range(5):
            stream = personal_ai.openai.responses.create(
                model=NEW_MODEL,
                input=messages,
                tools=new_tools,
                reasoning={"effort": "low"},
                stream=True,
            )
            collected = []
            completed_output = []
            for event in stream:
                if event.type == "response.output_text.delta":
                    if ttft is None:
                        ttft = time.perf_counter() - t_start
                    collected.append(event.delta)
                elif event.type == "response.completed":
                    completed_output = event.response.output
                    usage = event.response.usage
                    input_tokens += usage.input_tokens
                    output_tokens += usage.output_tokens

            function_calls = [item for item in completed_output if item.type == "function_call"]
            if function_calls:
                messages.extend([
                    {"type": "function_call", "call_id": tc.call_id, "name": tc.name, "arguments": tc.arguments}
                    for tc in function_calls
                ])
                for tc in function_calls:
                    tools_fired.append(tc.name)
                    result = {"acknowledged": True}
                    messages.append({
                        "type": "function_call_output",
                        "call_id": tc.call_id,
                        "output": json.dumps(result),
                    })
            else:
                final_text = "".join(collected)
                messages.append({"role": "assistant", "content": final_text})
                break

    total = time.perf_counter() - t_start
    cost = cost_for(NEW_MODEL, input_tokens, output_tokens)
    return {
        "ttft": ttft, "total": total, "tools_fired": tools_fired, "final_text": final_text,
        "input_tokens": input_tokens, "output_tokens": output_tokens, "cost": cost,
    }


def fmt(v):
    return f"{v:.2f}s" if v is not None else "n/a"


def run_utility(model: str, message: str, response: str) -> dict:
    """Replicates the real _generate_suggestions call shape from app.py."""
    t_start = time.perf_counter()
    try:
        resp = personal_ai.openai.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": (
                    f"Based on this Q&A about a software engineer named Hoang Nhat Duy Le, "
                    f"suggest 3 short natural follow-up questions a visitor might ask next.\n\n"
                    f"User asked: {message}\n"
                    f"Answer summary: {response[:300]}\n\n"
                    f"Return ONLY a JSON array of 3 questions (under 12 words each). No explanation.\n"
                    f'Example: ["What projects have you built?", "What\'s your tech stack?", "Are you open to work?"]'
                )
            }],
            max_completion_tokens=120,
        )
        total = time.perf_counter() - t_start
        raw = (resp.choices[0].message.content or "").strip()
        usage = resp.usage
        cost = cost_for(model, usage.prompt_tokens, usage.completion_tokens)
        return {
            "total": total, "raw": raw, "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens, "cost": cost, "error": None,
        }
    except Exception as e:
        return {"total": time.perf_counter() - t_start, "raw": None, "error": str(e),
                "input_tokens": 0, "output_tokens": 0, "cost": 0.0}


def main():
    print("### MAIN MODEL: gpt-5-mini vs gpt-5.6-luna ###\n")
    print(f"{'Scenario':<38} {'Model':<14} {'TTFT':>7} {'Total':>7} {'Tokens (in/out)':>16} {'Cost':>9}  Tools fired")
    print("-" * 130)
    old_totals = {"input": 0, "output": 0, "cost": 0.0, "latency": 0.0}
    new_totals = {"input": 0, "output": 0, "cost": 0.0, "latency": 0.0}

    for name, turns in SCENARIOS:
        old = run_old(turns)
        new = run_new(turns)

        for totals, r in ((old_totals, old), (new_totals, new)):
            totals["input"] += r["input_tokens"]
            totals["output"] += r["output_tokens"]
            totals["cost"] += r["cost"]
            totals["latency"] += r["total"]

        tok_old = f"{old['input_tokens']}/{old['output_tokens']}"
        tok_new = f"{new['input_tokens']}/{new['output_tokens']}"
        print(f"{name:<38} {OLD_MODEL:<14} {fmt(old['ttft']):>7} {fmt(old['total']):>7} {tok_old:>16} ${old['cost']*1000:>7.4f}m  {old['tools_fired']}")
        print(f"{'':<38} {NEW_MODEL:<14} {fmt(new['ttft']):>7} {fmt(new['total']):>7} {tok_new:>16} ${new['cost']*1000:>7.4f}m  {new['tools_fired']}")
        print(f"    old answer: {old['final_text'][:150]!r}")
        print(f"    new answer: {new['final_text'][:150]!r}")
        print()

    print("=" * 70)
    print(f"TOTAL over {len(SCENARIOS)} scenarios:")
    print(f"  {OLD_MODEL:<14} tokens={old_totals['input']}/{old_totals['output']}  "
          f"cost=${old_totals['cost']:.6f}  latency={old_totals['latency']:.2f}s")
    print(f"  {NEW_MODEL:<14} tokens={new_totals['input']}/{new_totals['output']}  "
          f"cost=${new_totals['cost']:.6f}  latency={new_totals['latency']:.2f}s")
    if old_totals["cost"] > 0:
        print(f"  Cost ratio (new/old): {new_totals['cost'] / old_totals['cost']:.2f}x")
    if old_totals["latency"] > 0:
        print(f"  Latency ratio (new/old): {new_totals['latency'] / old_totals['latency']:.2f}x")

    # ── Utility model comparison ──
    print("\n\n### UTILITY MODEL: gpt-5-nano vs gpt-5.4-nano (suggestion generation) ###\n")
    sample_qas = [
        ("What programming languages and frameworks do you know?",
         "I'm experienced with Java, C#, C++, Python, JavaScript, TypeScript, and various backend/web frameworks."),
        ("What is your favorite pizza topping?",
         "I don't have that detail available. If you'd like, you can leave your name and email so I can follow up."),
        ("I'd like to connect — I'm Jamie Chen, interested in collaborating.",
         "Thanks, Jamie! I've saved your details and will follow up soon about collaborating."),
    ]
    old_u_totals = {"input": 0, "output": 0, "cost": 0.0, "latency": 0.0, "errors": 0}
    new_u_totals = {"input": 0, "output": 0, "cost": 0.0, "latency": 0.0, "errors": 0}
    for q, a in sample_qas:
        old_u = run_utility(OLD_UTILITY_MODEL, q, a)
        new_u = run_utility(NEW_UTILITY_MODEL, q, a)
        for totals, r in ((old_u_totals, old_u), (new_u_totals, new_u)):
            totals["input"] += r["input_tokens"]
            totals["output"] += r["output_tokens"]
            totals["cost"] += r["cost"]
            totals["latency"] += r["total"]
            if r["error"]:
                totals["errors"] += 1
        print(f"Q: {q[:60]}")
        print(f"  {OLD_UTILITY_MODEL:<14} {fmt(old_u['total']):>7}  tokens={old_u['input_tokens']}/{old_u['output_tokens']}  "
              f"cost=${old_u['cost']:.6f}  -> {old_u['raw'] if not old_u['error'] else 'ERROR: ' + old_u['error']}")
        print(f"  {NEW_UTILITY_MODEL:<14} {fmt(new_u['total']):>7}  tokens={new_u['input_tokens']}/{new_u['output_tokens']}  "
              f"cost=${new_u['cost']:.6f}  -> {new_u['raw'] if not new_u['error'] else 'ERROR: ' + new_u['error']}")
        print()

    print("=" * 70)
    print(f"TOTAL over {len(sample_qas)} utility calls:")
    print(f"  {OLD_UTILITY_MODEL:<14} tokens={old_u_totals['input']}/{old_u_totals['output']}  "
          f"cost=${old_u_totals['cost']:.6f}  latency={old_u_totals['latency']:.2f}s  errors={old_u_totals['errors']}")
    print(f"  {NEW_UTILITY_MODEL:<14} tokens={new_u_totals['input']}/{new_u_totals['output']}  "
          f"cost=${new_u_totals['cost']:.6f}  latency={new_u_totals['latency']:.2f}s  errors={new_u_totals['errors']}")


if __name__ == "__main__":
    main()
