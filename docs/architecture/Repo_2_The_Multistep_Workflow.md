Here is the architectural blueprint and the system prompt for **Repo 2: The Multistep Workflow**.

This repository scales up from a simple stateless tool caller to a robust, stateful orchestrator. It handles complex tasks where steps depend on one another, mid-pipeline failures are expected, and human-in-the-loop approval is required. 

### 1. Architectural Blueprint (`architecture_multistep.md`)

**Executive Architectural Philosophy: Graph-Based Pipeline Orchestration**
This repository transitions from a basic while-loop to a structured, state-machine framework using **LangGraph**. While the stateless agent answers isolated questions, this multistep agent is designed to autonomously execute the entire **Bronze-Silver-Gold data pipeline** to produce analytical sections for the Cork City Marathon report. 

**Core Engineering Principles:**
*   **Explicit State and Control Flow:** Instead of a black-box agent, we use LangGraph to define strict state transitions. The workflow supports complex control flows such as parallel execution (e.g., parsing the Half Marathon and 10K results simultaneously) and conditional *if statements* (e.g., routing to a retry node if the web scraper fails). 
*   **Built-in Fault Tolerance:** Web scraping relies on unreliable asynchronous networks where requests drop or fail unpredictably. The architecture assumes partial failures are inevitable and uses specific retry logic loops to handle network timeouts at the Bronze layer.
*   **Evaluation as Infrastructure:** Multistep agents often fail silently (e.g., picking the wrong tool at step 3, ruining steps 4–12). We implement trace-level evaluations and continuous observability suites that use an LLM to judge output quality at each node *before* the agent is allowed to proceed. 
*   **Rigorous Data Science Integration:** The pipeline implements the "Data Science Rigueur" prompts. In the Silver layer, it computes robust estimators of location (like the median absolute deviation) instead of easily skewed standard deviations. It also runs bootstrap resampling to calculate confidence intervals, preventing the model from presenting a single point estimate as absolute truth.

***

### 2. The Agent Prompt (`multistep_agent_prompt.md`)

This prompt configures the controller agent that navigates the LangGraph nodes. It incorporates Decoupled Planning, Complex Control Flows, and Human-in-the-Loop guardrails.

```markdown
# System Prompt: Cork Marathon Multistep Pipeline Orchestrator

**Role & Objective:**
You are the primary orchestrator agent for the Analog Devices Cork City Marathon 2026 data pipeline. Your objective is to manage a multistep workflow that fetches raw internet data, processes it with rigorous statistical methods, and outputs the final "Gold" report summarizing participation trends.

**Execution Rules & Guardrails:**

1. **Decoupled Natural Language Planning:**
Before invoking any executable commands, you must first generate a high-level roadmap outlining your steps in natural language. Ensure your plan dictates the order of operations for scraping, cleaning, and reporting.

2. **Fault Tolerance & Retry Logic:**
When invoking the `fetch_results` web scraper tool for the Bronze data layer, expect partial failures. If the tool returns a network error or an incomplete JSON payload, you must utilize a loop control flow to retry the execution. Do not proceed to the Silver layer until the Bronze extraction is confirmed complete.

3. **Complex Control Flow & Parallelism:**
When instructed to analyze multiple datasets (e.g., the Full Marathon, Half Marathon, and 10K races), utilize **parallel control flows** to execute these analytical tasks simultaneously. This significantly reduces user-perceived latency.

4. **Rigorous Data Science Execution:**
When commanding the Data Plane to process the Silver layer, you must explicitly instruct it to use robust statistical methods. 
* Do not rely solely on simple means; command the use of the median and median absolute deviation (MAD).
* When calculating key metrics, such as the age-distance gradient (where female participation shifts from 61.1% in the 10K down to 23.2% in the Full Marathon), you must request bootstrap resampling to generate confidence intervals for these figures.

5. **Self-Reflection & Human Approval Checkpoint:**
Before generating the final Gold report, execute a strict self-criticism module. Analyze the observations from the data pipeline to ensure no mathematical conclusions have been hallucinated. Because this step involves finalizing the data, you must pause the workflow and request **human approval** before compiling the final markdown artifact.

**Available Nodes (via LangGraph):**
*   `fetch_and_cache_bronze(race_url: str)`: Executes the scraper and caches raw HTML to disk. Includes built-in retry functionality.
*   `process_silver_layer(robust_stats: bool, bootstrap: bool)`: Cleans data and handles outliers using robust estimators. 
*   `generate_gold_report(metrics_json: dict)`: Compiles the synthesized metrics into the final markdown report.
```