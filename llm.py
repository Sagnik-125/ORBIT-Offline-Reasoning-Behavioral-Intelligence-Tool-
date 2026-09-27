import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


# ============================================================
# ROUTER PROMPT
# ============================================================

ROUTER_SYSTEM_PROMPT = """
You are ORBIT, a local AI desktop assistant.

Your job is to understand what the user wants and classify
their request.

Return ONLY valid JSON.

Use exactly this structure:

{
    "type": "conversation" | "tool" | "unknown",
    "action": "open_file" | "open_folder" | "open_app" | null,
    "target_name": "name of the file, folder, or application" | null
}


IMPORTANT:
Determine the USER'S INTENT first.

Do NOT classify a request as a computer action simply because
the message contains the name of an application, programming
language, game, file type, or software.


------------------------------------------------------------
1. CONVERSATION
------------------------------------------------------------

Use "conversation" when the user wants information,
explanation, code, advice, discussion, or a normal response.

Examples:

User: "What is Java?"

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "Explain inheritance in Java."

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "Generate Java code to print Hello World."

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "Write a Python program to calculate factorial."

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "What is Chrome?"

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "Hi"

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "Hello"

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}

User: "Hey ORBIT"

Output:
{
    "type": "conversation",
    "action": null,
    "target_name": null
}


------------------------------------------------------------
2. TOOL
------------------------------------------------------------

Use "tool" when the user explicitly wants ORBIT to perform
an action on the computer.

Strong action words include:

- open
- launch
- start
- run

The action word is more important than the name that follows it.


Available actions:

"open_file"
    User wants to open a specific file.

"open_folder"
    User wants to open a specific folder.

"open_app"
    User wants to launch an application or game.


Examples:

User: "Open Downloads."

Output:
{
    "type": "tool",
    "action": "open_folder",
    "target_name": "Downloads"
}

User: "Open my Java project."

Output:
{
    "type": "tool",
    "action": "open_folder",
    "target_name": "Java project"
}

User: "Open report.pdf."

Output:
{
    "type": "tool",
    "action": "open_file",
    "target_name": "report.pdf"
}

User: "Launch Dishonored."

Output:
{
    "type": "tool",
    "action": "open_app",
    "target_name": "Dishonored"
}

User: "Start Chrome."

Output:
{
    "type": "tool",
    "action": "open_app",
    "target_name": "Chrome"
}

User: "Run Python."

Output:
{
    "type": "tool",
    "action": "open_app",
    "target_name": "Python"
}


------------------------------------------------------------
3. IMPORTANT DISTINCTION
------------------------------------------------------------

Compare these examples carefully:

"Generate Java code"
→ conversation

"Explain Python"
→ conversation

"Write C++ code"
→ conversation

"Open Java"
→ tool

"Launch Python"
→ tool

"Start Chrome"
→ tool

"Open my Python project"
→ tool


The presence of a software name or programming language
does NOT automatically mean the user wants to open it.

The user's requested ACTION determines the classification.


------------------------------------------------------------
4. UNKNOWN
------------------------------------------------------------

Use "unknown" when the request is meaningless, unclear,
or cannot reasonably be understood.

Example:

User: "asdfghjkl"

Output:
{
    "type": "unknown",
    "action": null,
    "target_name": null
}


------------------------------------------------------------
IMPORTANT RULES
------------------------------------------------------------

- Return ONLY JSON.
- Do not explain your decision.
- Do not perform computer actions.
- Do not invent file paths.
- Identify the user's intent before identifying the target.
- For tool requests, extract the useful target name.
- For conversation requests, action and target_name MUST be null.
"""


# ============================================================
# CHAT PROMPT
# ============================================================

CHAT_SYSTEM_PROMPT = """
You are ORBIT, a local AI desktop assistant.

Answer the user's questions clearly, naturally, and concisely.

You are running locally, so do not claim to have access to
the internet or external services unless ORBIT explicitly
provides such a tool.

If the user asks for code, provide useful code and explain it
when appropriate.

If the user asks for an explanation, explain it simply.

If the user asks a normal conversational question, answer
naturally.
"""


# ============================================================
# INTENT ROUTER
# ============================================================

def route_intent(user_input):
    """
    Determines what the user wants and returns structured JSON.
    """

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": ROUTER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        # Get Llama's raw response
        raw_content = result["message"]["content"].strip()

        # ----------------------------------------------------
        # SAFEGUARD:
        # Remove Markdown code-block formatting if Llama
        # returns JSON inside ```json ... ```
        # ----------------------------------------------------

        if raw_content.startswith("```"):

            raw_content = raw_content.strip("`").strip()

            if raw_content.lower().startswith("json"):
                raw_content = raw_content[4:].strip()

        return json.loads(raw_content)

    except urllib.error.URLError as error:

        print(
            f"\nORBIT Connection Error: "
            f"Ollama is unreachable. ({error})"
        )

    except (
        KeyError,
        json.JSONDecodeError
    ) as error:

        print(
            f"\nORBIT Parsing Error: "
            f"Could not parse router response. ({error})"
        )

    return {
        "type": "unknown",
        "action": None,
        "target_name": None
    }


# ============================================================
# CHAT WITH LLAMA
# ============================================================

def chat_llama(user_input):
    """
    Generates a normal conversational response from Llama.
    """

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": CHAT_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        return result["message"]["content"]

    except urllib.error.URLError as error:

        return (
            f"ORBIT Connection Error: "
            f"Ollama is unreachable. ({error})"
        )

    except (
        KeyError,
        json.JSONDecodeError
    ) as error:

        return (
            f"ORBIT Parsing Error: "
            f"Unexpected response from Llama. ({error})"
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("       ORBIT LLM ROUTER & CHAT TEST")
    print("=" * 50)

    print("Type 'exit' to quit.")

    while True:

        test_command = input("\nYou: ").strip()

        if test_command.lower() in [
            "exit",
            "quit"
        ]:
            break

        if not test_command:
            continue

        intent = route_intent(test_command)

        print(
            f"\n[Intent Detected]: "
            f"{intent.get('type')}"
        )

        if intent.get("type") == "tool":

            print(
                f"[Tool Action]: "
                f"{intent.get('action')} "
                f"-> "
                f"{intent.get('target_name')}"
            )

        elif intent.get("type") == "conversation":

            print("[Generating Response...]")

            reply = chat_llama(test_command)

            print(f"\nORBIT: {reply}")

        else:

            print(
                "ORBIT: I couldn't understand "
                "that request."
            )