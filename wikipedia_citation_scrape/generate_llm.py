import torch
from tqdm import tqdm
from transformers import GemmaTokenizerFast, GemmaForCausalLM, AutoModelForCausalLM, AutoTokenizer
import json
import sys

DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

def get_model():
    model_id = "google/gemma-1.1-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
    ).to(DEVICE)

    return tokenizer, model

# def prompt_get_claims(abstract, num):
#     prompt = "<start_of_turn>user\n"
#     prompt += f"List the {num} most important claims of the following abstract. Rewrite the claims to be direct and to the point."
#     prompt += "\nDo not include any extra text or formatting."
#     prompt += "\n\nABSTRACT:\n"
#     prompt += "\""+abstract+"\"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#
#     return prompt
#
# def prompt_get_questions(claim):
#     prompt = "<start_of_turn>user\n"
#     prompt += "The following claim may include terms whose referent is unclear because the claim has been removed from context.\n"
#     prompt += "If there are any such terms, list them without any extra explanation.\n"
#     prompt += "Only include terms whose original context has been removed, which might confuse an educated audience.\n"
#     prompt += "If there are no such terms, say \"No terms given\"."
#
#     prompt += "CLAIM: " + claim + "\n"
#
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#     return prompt
#
# def prompt_get_answers(questions, abstract):
#     prompt = "<start_of_turn>user\n"
#     prompt += "Your goal is to contextualize each term you are given.\n"
#     prompt += "If terms are given, expand them based on what exactly the term refers to in the paragraph.\n"
#     prompt += "Do not provide any extra explanation.\n"
#     prompt += "If no terms are given, only reply with \"No clarification needed\"."
#     prompt += "PARAGRAPH: \n"+abstract+"\n"
#     prompt += "TERMS: \n"+questions+"\n"
#
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#     return prompt
#
# def prompt_get_rewrite(claim, clarif):
#     prompt = "<start_of_turn>user\n"
#     prompt += "You will be given a sentence and a list of terms that need extra clarification. Rewrite the sentence to include this information.\n"
#     prompt += "If no clarification is needed, just return the original sentence."
#     prompt += "SENTENCE: " + claim +"\n"
#     prompt += "CLARIFICATION: \n"+clarif+"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\nREWRITTEN SENTENCE: "
#     return prompt

# def prompt_get_topic(abstract):
#     prompt = "<start_of_turn>user\n"
#     prompt += "Write a brief topic phrase for the following abstract. Return the phrase without any explanation."
#     prompt += "\n\nABSTRACT:\n"
#     prompt += "\""+abstract+"\"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#
#     return prompt
#
# def prompt_get_contextualized(claim, topic):
#     prompt = "<start_of_turn>user\n"
#     prompt += "You will be given a topic and a fact. Incorporate any missing information from the topic into the fact. "
#     prompt += "Ensure that important keywords from the topic are present in the rewritten sentence. Be careful not to contradict the original fact."
#     prompt += "If no clarification is needed, just return the original sentence. \n"
#     prompt += "TOPIC: \n"+topic+"\n"
#     prompt += "FACT: " + claim +"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\REWRITTEN FACT: "
#     return prompt

# def prompt_get_claimses(abstract, num):
#     prompt = "<start_of_turn>user\n"
#     prompt += "Read the abstract and write the topic as a brief phrase, including the specific subject of the article."
#     prompt += f"Then, list the {num} most important claims of the following abstract, written to include information from the topic phrase. "
#     prompt += "You MUST include each keyword from the topic in its entirety in every single sentence. "
#     prompt += "The claims must be direct and to the point. "
#     prompt += "\nDo not include any extra text or formatting."
#     prompt += "\n\nABSTRACT:\n"
#     prompt += "\""+abstract+"\"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#
#     return prompt

# def prompt_get_claimses(abstract, num):
#     prompt = "<start_of_turn>user\n"
#     prompt += f"List the {num} most important claims of the following abstract. \n"
#     prompt += "Rewrite them to be concise and direct. Only use common words.\n"
#     prompt += "The claims cannot contain the words this, that, these, and those. Replace these words with the full noun they refer to in the abstract. "
#     prompt += "\nDo not include any extra text or formatting."
#     prompt += "\n\nABSTRACT:\n"
#     prompt += "\""+abstract+"\"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#
#     return prompt

# def prompt_get_claimses(abstract, num):
#     prompt = "<start_of_turn>user\n"
#     prompt += "First, rewrite the abstract to remove all demonstratives (this, that, these, those) and acronyms."
#     prompt += f"Then, list the {num} most important claims of the rewritten abstract. \n"
#     prompt += "\n\nABSTRACT:\n"
#     prompt += "\""+abstract+"\"\n"
#     prompt += "<end_of_turn>\n<start_of_turn>model\n"
#
#     return prompt

def prompt_get_claimses(abstract, num):
    prompt = "<start_of_turn>user\n"
    prompt += "First, create a very short topic phrase that best represents the article and its keywords."
    prompt += f"Then, list the {num} most important claims of the rewritten abstract. Each claim must be direct and to the point. \n"
    prompt += "\nList the topic and claims without any extra explanation or formatting."
    prompt += "\n\nABSTRACT:\n"
    prompt += "\""+abstract+"\"\n"
    prompt += "<end_of_turn>\n<start_of_turn>model\n"

    return prompt

def extract_claims(response):
    response_lines = response.split("\n")
    topic = response_lines[0].split(":")[1][3:]
    claims = [x[3:] for x in response_lines[1:] if len(x) > 16]

    # textlines = [x for x in response_lines if len(x) > 3 and "<end_of_turn>" not in x]
    return topic, claims

def generate_result(prompt, model, tokenizer, tokens=256):
    input_ids = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    outputs = model.generate(**input_ids, max_new_tokens=tokens)
    prompt_length = input_ids['input_ids'].shape[1]
    response = tokenizer.decode(outputs[0][prompt_length:])
    return response.replace("<end_of_turn>", "").replace("<eos>", "")

if __name__ == "__main__":

    start_pos = 0 if len(sys.argv) <= 1 else int(sys.argv[1])
    num_to_run = -1 if len(sys.argv) <= 2 else int(sys.argv[2])

    with open('rawtext_dataset.txt', 'r', encoding='UTF-8') as infile:
        dataset = json.load(infile)
    abstracts = {}

    for i, x in enumerate(dataset):
        if x['abstract'][0] != '>' and x['doi'] not in abstracts:
            abstracts[x['doi']] = x['abstract']

    tokenizer, model = get_model()
    responses = {}
    print(len(abstracts))
    dois = list(abstracts.keys())
    if num_to_run >= 0:
        dois = dois[start_pos:start_pos+num_to_run]

    for i, doi in tqdm(enumerate(dois)):
        if len(abstracts[doi]) < 50:
            responses[doi] = {}
            responses[doi]["abstract"] = abstracts[doi]
            responses[doi]["claims"] = []
            continue

        prompt1 = prompt_get_claimses(abstracts[doi], 3)
        response = generate_result(prompt1, model, tokenizer)

        extracted_topic, extracted_claims = extract_claims(response)
        # print("1")
        # print(extracted)

        # promptB = prompt_get_topic(abstracts[doi])
        # topic = generate_result(promptB, model, tokenizer)
        # print("B")
        # print(topic)
        #
        # for j, e in enumerate(extracted):
        #     promptC = prompt_get_contextualized(e, topic)
        #     rewrite = generate_result(promptC, model, tokenizer)
        #     print("C", j)
        #     print(rewrite)

        #     prompt2 = prompt_get_questions(e)
        #     qs = generate_result(prompt2, model, tokenizer)
        #     print("2", j)
        #     print(qs)
        #
        #     prompt3 = prompt_get_answers(qs, abstracts[doi])
        #     ans = generate_result(prompt3, model, tokenizer)
        #     print("3", j)
        #     print(ans)
        #
        #     prompt4 = prompt_get_rewrite(e, ans)
        #     rewrite = generate_result(prompt4, model, tokenizer)
        #     print("4", j)
        #     print(rewrite)
        #
            # rewritten.append(rewrite.strip())


        responses[doi] = {}
        responses[doi]["abstract"] = abstracts[doi]
        responses[doi]["claims"] = extracted_claims
        responses[doi]["topic"] = extracted_topic

        print(json.dumps(responses[doi], indent=2))

        if i % 100 == 0:
            with open('generated_claims_prog.txt', 'w', encoding='UTF-8') as outfile:
                json.dump(responses, outfile, indent=2)

    with open('generated_claims.txt', 'w', encoding='UTF-8') as outfile:
        json.dump(responses, outfile, indent=2)
