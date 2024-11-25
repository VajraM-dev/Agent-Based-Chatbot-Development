from agent_chain import get_response, api_clear_history
from langchain import hub
from config.llm import llm
from langsmith import evaluate
from langsmith import Client

client = Client()

def create_dataset(examples, dataset_name):
    
    dataset = client.create_dataset(dataset_name=dataset_name)
    inputs, outputs = zip(
        *[({"input": text}, {"output": result}) for text, result in examples]
    )
    client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

def predict_agent_answer(example: dict):
    """Use this for answer evaluation"""

    config = {'configurable': {'session_id': 'eval'}}
    messages = get_response(example["input"], config)
    api_clear_history(config)
    return {"response": messages}

# Grade prompt
grade_prompt_answer_accuracy = prompt = hub.pull("langchain-ai/rag-answer-vs-reference")

def answer_evaluator(run, example) -> dict:
    """
    A simple evaluator for RAG answer accuracy
    """

    # Get question, ground truth answer, RAG chain answer
    input_question = example.inputs["input"]
    reference = example.outputs["output"]
    prediction = run.outputs["response"]

    # Structured prompt
    answer_grader = grade_prompt_answer_accuracy | llm

    # Run evaluator
    score = answer_grader.invoke({"question": input_question,
                                  "correct_answer": reference,
                                  "student_answer": prediction})
    score = score["Score"]

    return {"key": "answer_v_reference_score", "score": score}

def run_eval(dataset_name, experiment_prefix):
    metadata = "V1, questionpro-agent"
    experiment_results = evaluate(
        predict_agent_answer,
        data=dataset_name,
        evaluators=[answer_evaluator],
        experiment_prefix=experiment_prefix + "-response-v-reference",
        num_repetitions=1,
        metadata={"version": metadata},
    )
    resp = client.read_project(project_name=experiment_results.experiment_name, include_stats=True)
    
    return resp.json(indent=2)

def evaluate_agent(examples, dataset_name, experiment_prefix=None, only_create_dataset=False):
    if only_create_dataset is False:
        try:
            create_dataset(examples, dataset_name)
        except Exception as e:
            return f"Error creating the dataset. Error: {e}"

        try:
            run_eval(dataset_name, experiment_prefix)
            return "Evaluation complete"
        except Exception as e:
            return f"Error evaluating the agent. Error: {e}"
    else:
        try:
            create_dataset(examples, dataset_name)
        except Exception as e:
            return f"Error creating the dataset. Error: {e}"

examples = [
        ("<sample_input>", "<sample_output>"),
    ]

dataset_name = "HelloDataset"
experiment_prefix="eval1"

evaluate_agent(examples, dataset_name, experiment_prefix)