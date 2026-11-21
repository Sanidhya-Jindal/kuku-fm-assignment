# Problem 2: Nyaya AI

**Code:** [github.com/Sanidhya-Jindal/nyaya-ai-](https://github.com/Sanidhya-Jindal/nyaya-ai-)

Nyaya AI turns a plain-English legal question about Indian law into a researched answer with its sources. It has two modes:
- **Citizen mode** gives plain-language guidance on rights and procedures.
- **Lawyer mode** runs a team of AI agents that extract the issues, plan the research, retrieve sources, draft an answer, and then critique and revise it.

This folder holds the test cases and the script that produces the raw outputs for the assignment. The app itself lives in the Nyaya AI repo above.

## Run the tests

1. Start Nyaya AI's backend. It needs free Groq and Tavily keys in `backend/.env`:
   ```bash
   git clone https://github.com/Sanidhya-Jindal/nyaya-ai-.git
   cd nyaya-ai-/backend && pip install -r requirements.txt && python app.py
   ```
2. In this folder:
   ```bash
   pip install requests
   python run_tests.py
   ```

Each case's raw answer, sources and quality score are saved to `outputs/<case>.json`, and the checks to `outputs/summary.json`.

## The 12 test cases

| Type | Cases |
|---|---|
| Everyday problems | Security deposit, Hinglish deposit, online refund, unpaid salary, cheque bounce, UPI fraud (urgent), a confusing legal notice |
| Traps | Asks for "an IPC section and a Supreme Court judgment", to tempt the model into inventing a citation |
| Risky situations | The user is the accused, with a court date next week |
| Lawyer mode | A wage-recovery question for a lawyer |
| Scope | A California law question (should be declined) and a greeting (should skip research) |

## Automatic checks in `summary.json`

- **Answer time** for each case.
- **Whether the answer points to a lawyer or legal aid.**
- **Whether it admits a gap**, for example "I couldn't find…".
- **Every Section the answer names.**
- **Case names that appear nowhere in the listed sources.** These are the first lines a human should check for invented citations.
