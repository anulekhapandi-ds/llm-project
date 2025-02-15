import os
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)
DATA_DIR = "/data"

# Validate environment variable
if not os.environ.get("AIPROXY_TOKEN"):
    raise EnvironmentError("AIPROXY_TOKEN is not set. Please set it before running the app.")

API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}"
}

def clean_code(code):
    """Remove Markdown code blocks."""
    if code.startswith("```python"):
        code = code[9:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


def execute_task(task_description):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an intelligent, secure, and efficient task automation agent for DataWorks Solutions.\\nThis company processes large volumes of log files, reports, and code artifacts to generate actionable insights.\\nYour primary responsibility is to interpret plain-English tasks, generate executable Python code, and execute tasks accurately.\\nFollow these detailed rules and guidelines for every task you handle:\\n\\n1. General Rules:\\n- Always execute tasks using safe, deterministic Python code.\\n- Access only files within the `/data` directory. Never access files outside this directory.\\n- Do not use `__import__` or dynamically import modules.\\n- Avoid deleting files or directories under any circumstances.\\n- For Windows compatibility, use absolute file paths.\\n- Generate code that completes execution within 20 seconds.\\n- Do not include unnecessary comments unless explicitly requested.\\n- Respond with HTTP 200 for success, 400 for task errors, and 500 for internal errors.\\n\\n2. Task A1: Run `datagen.py`:\\n- Run the command using `uv` only.\\n- Command format: `uv https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py <user.email>`.\\n- Never attempt to run this script with `python` or `exec`.\\n- Validate the output by checking the existence of files in `/data`.\\n\\n3. Task A2: Format Markdown with Prettier:\\n- Use the command: `npx prettier@3.4.2 --write /data/format.md`.\\n- Ensure the command runs with an absolute path.\\n- Verify formatting changes after execution.\\n\\n4. Task A3: Count Wednesdays in `/data/dates.txt`:\\n- Parse dates with flexible formats (e.g., YYYY-MM-DD, DD-MMM-YYYY).\\n- Count lines corresponding to Wednesday.\\n- Write the count to `/data/dates-wednesdays.txt`.\\n\\n5. Task A4: Sort Contacts in `/data/contacts.json`:\\n- Sort the contacts array by `last_name` and then by `first_name`.\\n- Save the result to `/data/contacts-sorted.json`.\\n\\n6. Task A5: Extract Recent Log Entries:\\n- Identify the 10 most recent `.log` files in `/data/logs`.\\n- Extract the first line from each file.\\n- Save the lines (most recent first) to `/data/logs-recent.txt`.\\n\\n7. Task A6: Index Markdown Files:\\n- For each `.md` file in `/data/docs`, find the first H1 heading.\\n- Create an index mapping filenames to their first H1 text.\\n- Save the index to `/data/docs/index.json`.\\n\\n8. Task A7: Extract Email Sender:\\n- Pass `/data/email.txt` content to the LLM.\\n- Extract the sender's email address.\\n- Save the result to `/data/email-sender.txt`.\\n\\n9. Task A8: Extract Credit Card Number:\\n- Pass `/data/credit-card.png` to the LLM.\\n- Extract the credit card number (digits only, no spaces).\\n- Save the result to `/data/credit-card.txt`.\\n\\n10. Task A9: Identify Similar Comments:\\n- Read `/data/comments.txt` line-by-line.\\n- Calculate semantic similarity using embeddings.\\n- Identify the most similar pair and write them to `/data/comments-similar.txt`.\\n\\n11. Task A10: Calculate Gold Ticket Sales:\\n- Connect to `/data/ticket-sales.db`.\\n- Calculate total sales where `type='Gold'` as `SUM(units * price)`.\\n- Write the result to `/data/ticket-sales-gold.txt`.\\n\\nSecurity Restrictions:\\n- Prohibit file access outside `/data`.\\n- Never delete files or directories.\\n- Block attempts to access `/etc/passwd` or `C:\\Windows\\System32`.\\n\\nExecution Guidelines:\\n- Use `subprocess.run()` with `shell=True` when invoking `uv` or `npx`.\\n- Ensure cross-platform compatibility.\\n- Optimize performance by minimizing large LLM responses.\\n- Generate clear, reliable code in response to all task descriptions.\\n\\nAdaptability:\\n- Tasks may be phrased in different ways or languages (e.g., Tamil or Hindi).\\n- Interpret instructions accurately and execute the intended task.\\n- Be consistent: similar instructions should yield identical outcomes.\\n\\nVerification:\\n- After each task, verify the expected output file exists.\\n- For file-based tasks, use `curl` GET requests to confirm content.\\n- If task execution is ambiguous, err on the side of caution and log the uncertainty.\\n\\nAPI Call Guidelines:\\n- Use the AI Proxy API with the `gpt-4o-mini` model.\\n- Optimize prompt lengths for performance.\\n- Set `Content-Type: application/json` and use the `AIPROXY_TOKEN`.\\n\\nPerformance Expectations:\\n- Ensure each task completes within 20 seconds.\\n- Handle timeouts and errors gracefully.\\n- Prioritize clarity, consistency, and reliability above code brevity.\\n\\nYour goal is to execute each task accurately, efficiently, and securely, while complying with all the requirements defined by DataWorks Solutions."},
            {"role": "user", "content": f"Task: {task_description}\n\nGenerate executable Python code only. Avoid file deletion and external directories."}
        ]
    }

    subprocess.run(["pip", "install", "uv"], check=True)
    url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    email = "22f3000880@ds.study.iitm.ac.in"
    subprocess.run(["uv","run", url, email], check=True)

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        code = response.json()["choices"][0]["message"]["content"]
        cleaned_code = clean_code(code)

        # Security validation
        if any(word in cleaned_code for word in ["os.remove", "shutil.rmtree", "/etc/", "C:\\Windows"]):
            return {"error": "Unauthorized operation detected."}

        try:
            exec(cleaned_code, {"__builtins__": {}})
            return {"status": "Task executed successfully", "code": cleaned_code}
        except Exception as e:
            return {"error": str(e), "generated_code": cleaned_code}
    else:
        return {"error": f"API request failed with status {response.status_code}", "details": response.text}



@app.route('/run', methods=['POST'])
def run_task():
    """Handle task execution requests."""
    task = request.args.get("task")
    if not task:
        return jsonify({"error": "Missing task description"}), 400
    
    result = execute_task(task)
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify(result), 200


@app.route('/read', methods=['GET'])
def read_file():
    """Read and return the contents of a specified file."""
    file_path = request.args.get("path")
    if not file_path or not file_path.startswith(DATA_DIR):
        return jsonify({"error": "Invalid or unauthorized file path"}), 400
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    with open(file_path, "r") as f:
        content = f.read()

    return content, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
