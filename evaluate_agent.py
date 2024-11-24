from agent_chain import get_response, api_clear_history
from langchain import hub
from config.llm import llm
from langsmith import evaluate

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

def run_eval(dataset_name, experiment_prefix, metadata):

    experiment_results = evaluate(
        predict_agent_answer,
        data=dataset_name,
        evaluators=[answer_evaluator],
        experiment_prefix=experiment_prefix + "-response-v-reference",
        num_repetitions=3,
        metadata={"version": metadata},
    )

    return experiment_results

experiment_prefix="eval1"
metadata = "V1, questionpro-agent"
dataset_name = "ds-false-manservant-64"
print(run_eval(dataset_name, experiment_prefix, metadata))