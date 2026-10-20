from openai import OpenAI
import json
import csv
import re


# ============================================================
# 1. OpenAI-compatible local agent
# ============================================================

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    # Do not let client-side retries turn one stage into repeated requests.
    max_retries=0,
)

MODEL = "gemma4:26b"
MAX_OUTPUT_TOKENS = 32500


# ============================================================
# 2. Prompts
# ============================================================

annotation_requirements = """Goal:
Help primary school students whose first language is not English understand important difficult words or phrases in an academic paragraph.

Select only vocabulary that may block or significantly reduce understanding of the paragraph. For each selected term, give a short, simple explanation based on how the term is used in this paragraph.

Rules:

1. Select words or phrases based ONLY on the input paragraph.

2. Be selective.
   Choose only difficult words or phrases that are useful for understanding the paragraph.
   Do not list every unfamiliar or academic-looking word.
   If a term is difficult but not important for understanding the paragraph, leave it out.

3. Give each selected term an importance score:
   - 3 = Essential: Without understanding this term, the reader would likely misunderstand the main idea of the paragraph.
   - 2 = Helpful: The main idea is still understandable, but an important part of the paragraph would be difficult to understand without this term.
   - 1 = Incidental: The term is useful to know, but not knowing it would not significantly affect understanding.

   Be conservative with score 3.
   When uncertain between 3 and 2, choose 2.

4. Explain the meaning of the word or phrase AS IT IS USED IN THIS PARAGRAPH.
   Do not give a broad dictionary definition when the paragraph uses the term in a more specific way.

   Ask:
   "What does this word or phrase mean here?"
   rather than:
   "What are all possible meanings of this word?"

5. Use very simple, concise English.
   Prefer ONE short sentence.
   Avoid explaining a difficult word with other difficult words.
   The explanation should be understandable to a college student who is still learning English.

6. Explain the vocabulary meaning only.
   Do NOT explain:
   - the whole paragraph,
   - background knowledge,
   - theories or academic concepts,
   - the author's overall argument,
   unless that information is necessary to clarify the meaning of the selected word or phrase.

7. Keep "explanation" and "importance_reason" separate.

   "explanation":
   What the word or phrase means in this paragraph.

   "importance_reason":
   Why knowing this term helps the reader understand THIS paragraph.

   Do not include the importance reason inside the explanation.

8. Do not introduce unnecessary outside information, additional academic terminology, or interpretations that are not supported by the paragraph.

9. If no difficult word or phrase is important enough to support comprehension, return an empty "items" list.

"""

json_output_format = """Return valid JSON only.
Do not return reasoning, commentary, Markdown, or any text outside the JSON.

Format:
{
  "paragraph_id": "p2",
  "items": [
    {
      "term": "privileged",
      "importance_score": 3,
      "explanation": "Treated as more important or more trustworthy than others.",
      "importance_reason": "The paragraph says that no person's view should automatically be treated as more trustworthy than another."
    }
  ]
}
"""

draft_prompt = """You are the draft writer.

Create the first vocabulary-annotation draft from the input paragraph. Follow all requirements below. Do not review or critique the draft; produce it directly.

{requirements}

Input:
<input_data>
{paragraph_id}
{paragraph}
</input_data>

{output_format}
"""

editor_prompt = """You are the editor.

Compare the input paragraph with the draft JSON. Make one editing pass: remove terms that should not be included, correct meanings or importance scores when needed, and simplify explanations when needed. Preserve correct work. Do not explain the edits and do not begin another review cycle.

{requirements}

Input paragraph:
<input_data>
{paragraph_id}
{paragraph}
</input_data>

Draft JSON:
<draft_json>
{draft_json}
</draft_json>

{output_format}
"""

reviewer_prompt = """You are the final reviewer.

Check the edited JSON against the input paragraph once. Keep it unchanged when it meets the requirements. Otherwise, make only the necessary final corrections. Do not add commentary, describe the review, or start another review cycle. Return the final JSON directly.

{requirements}

Review criteria for this one final pass:
    - Is each term genuinely difficult for an English learner?
    - Is each term important enough to include?
    - Does the explanation match the meaning in this paragraph?
    - Is the explanation short and written in simple English?
    - Did I avoid explaining background knowledge or the whole paragraph?
    - Is the importance score justified?

Input paragraph:
<input_data>
{paragraph_id}
{paragraph}
</input_data>

Edited JSON:
<edited_json>
{edited_json}
</edited_json>

{output_format}
"""


# ============================================================
# 3. Your article
# ============================================================

selected_article = """THE CORE CONCEPT: SITUATED KNOWLEDGES

In practice, situated knowledges and standpoint feminist aspirations were put to work in studies inspired by both Harding’s and Haraway’s new methodologies. In these studies, the illusion of science as the unbiased production of knowledge was questioned, and new critical perspectives on scientific practices were initiated.

One example of this critical approach to science, specifically biological research about sex/gender, was Anne Fausto-Sterling’s work, The Myths of Gender (1985). In this work, she systematically debunked highly respected research on biologically based sex/gender differences. This move made her a part of a scientifically based, but also politically motivated questioning of what sex/gender can tell us about an individual’s character and abilities. Along similar critical and politically motivated lines, Emily Martin’s work The Egg and the Sperm: How Science Has Constructed a Romance Based on Stereotypical Male-Female Roles (1991) revealed how stereotypical perceptions of men and women biased what medical scientists were able to perceive in their research on the sperm and the egg. Once again, unwrapping the highly politically charged message implicit in scientific knowledge about a gender-stereotypically passive egg and a gender-stereotypically active sperm which implied that gender stereotypes were biologically based and therefore immutable. In this way, feminist STS made explicit that culturally based gender stereotypes framed results in biological science that had until then been assumed to be objective and unsituated. 

In other words, feminist STS facilitated an awareness that even very basic social categories such as ‘women’ or ‘men’ were highly charged political categories. This means that, when we lay scientific claim to what a woman’s or a man’s body is, we are implicitly also laying claim to what a woman’s or a man’s body ought to be and what sort of action this female or male body ought to be initiating or participating in. Therefore, feminist STS brings to the fore that one can never achieve knowledge of the gendered body, nor of any topic for that matter, from a neutral standpoint. Knowledge is always situated or entangled within assumptions about epistemology and political preferences. When we are doing research, we are therefore always also doing politics and including or excluding certain bodies from certain spaces. And, contrary to traditional perceptions, it is not that feminist STS introduced a political agenda within scientific practices, but rather that feminist STS make explicit that political agendas were already embedded in the ways research was carried out and is still being carried out today.

THE POLITICAL WORK ON PERCEPTIONS OF SEX AND GENDER

In order to illustrate this entanglement of research practices, epistemological research critiques and politics, it might be useful to provide a few concrete examples of the latent political potential of different scientific understandings of sex and gender.

One example is in this issue’s interview with Nina Lykke, where she presents us with an illustration of the original political potential in the separation of sex and gender. She illustrates the usefulness of the distinction between sex and gender with the fact that her parents both were full-time doctors, yet only her mother took on household duties. The point is that this division of labor was perceived as natural at the time. Against this backdrop, a distinction between sex and gender offered a critical view of socio-cultural norms. In other words, by driving a wedge between biological sex and perceived gender roles, a new feminist perspective on the everyday conditions of family life was unveiled, a perspective that invited the question: if biological sex does not determine gender roles, why have women been given greater responsibilities in the home than men?

This ability to ‘trouble’ norms by distinguishing between sex and gender exposed a significant asymmetric attribution of value between stereotypically feminine-defined tasks in the home and the stereotypically masculine-defined tasks in the workplace, which were valued highly enough to be paid. To challenge this asymmetry between men and women in their everyday lives, new theoretical approaches started to place an emphasis on the value of stereotypically feminine over stereotypically masculine values. This theoretical and political move was expressed in different variations within radical feminism (Firestone 1970), eco-feminism (Mies and Shiva 1993) and sexual difference theory (Irigaray 1985). However, these approaches never succeeded in boosting the feminine values to the level of the masculine ones, and therefore they inadvertently fed into the discourse that women are biologically determined to do different and less significant tasks than men.

In the 1990’s Judith Butler took up the political battle over sex/gender by making the reverse move, that is, fighting against the separation of sex and gender. She did this because, in her view, this seperation had led to a privileging of sex over gender. In her iconic book Gender Trouble (1990), she emphasized that, as long as we speak of sex and gender as two separable entities, we are reiterating sex as the biological cause of gender, thereby contributing to the power hierarchy we are striving to challenge. Many misinterpreted Butler’s work to mean that the body could be reduced to discourse. However, Butler herself did not intend to deny that bodies do exist (as illustrated by her follow up work, Bodies That Matter of 1993). She merely pointed out, in agreement with such writers as Fausto-Sterling, Martin and Haraway, that we can never achieve access to an uncultured body.
"""


# ============================================================
# 4. Split article into paragraphs
# ============================================================

def split_paragraphs(article):
    """
    Split paragraphs based on blank lines.
    """
    paragraphs = re.split(r"\n\s*\n", article.strip())

    # Remove empty paragraphs
    paragraphs = [
        p.strip()
        for p in paragraphs
        if p.strip()
    ]

    return paragraphs


# ============================================================
# 5. Run the fixed three-stage workflow for ONE paragraph
# ============================================================

def parse_annotation_response(response, paragraph_id, stage):
    """
    Parse and minimally validate a stage response.
    Return None when the response cannot safely be used.
    """
    if not response.choices:
        print(f"\nERROR: Empty {stage} response for {paragraph_id}")
        return None

    choice = response.choices[0]

    # A length-limited response may contain incomplete JSON. Do not retry it.
    if choice.finish_reason == "length":
        print(f"\nERROR: {stage} reached the output limit for {paragraph_id}")
        return None

    raw_output = (choice.message.content or "").strip()

    # Keep this fallback in case a model returns fences despite JSON mode.
    if raw_output.startswith("```"):
        raw_output = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw_output,
            flags=re.DOTALL
        ).strip()

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        print(f"\nERROR: Invalid JSON from {stage} for {paragraph_id}")
        print(raw_output)
        return None

    if not isinstance(result, dict) or not isinstance(result.get("items"), list):
        print(f"\nERROR: Invalid annotation structure from {stage} for {paragraph_id}")
        return None

    required_item_fields = {
        "term",
        "importance_score",
        "explanation",
        "importance_reason",
    }
    if any(
        not isinstance(item, dict) or not required_item_fields.issubset(item)
        for item in result["items"]
    ):
        print(f"\nERROR: Invalid item structure from {stage} for {paragraph_id}")
        return None

    # The caller controls paragraph IDs, rather than trusting a model response.
    result["paragraph_id"] = paragraph_id
    return result


def call_annotation_stage(prompt, paragraph_id, stage):
    """Make exactly one bounded request for a workflow stage."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=MAX_OUTPUT_TOKENS,
            response_format={"type": "json_object"},
            reasoning_effort="none",
        )
    except Exception as error:
        print(f"\nERROR: {stage} request failed for {paragraph_id}: {error}")
        return None

    return parse_annotation_response(response, paragraph_id, stage)


def analyze_paragraph(paragraph_id, paragraph):
    """
    Produce an annotation through exactly three roles: draft writer, editor,
    and final reviewer. A failed later stage falls back to its valid predecessor.
    """
    draft = call_annotation_stage(
        draft_prompt.format(
            requirements=annotation_requirements,
            paragraph_id=paragraph_id,
            paragraph=paragraph,
            output_format=json_output_format,
        ),
        paragraph_id,
        "draft",
    )

    if draft is None:
        return {"paragraph_id": paragraph_id, "items": []}

    edited = call_annotation_stage(
        editor_prompt.format(
            requirements=annotation_requirements,
            paragraph_id=paragraph_id,
            paragraph=paragraph,
            draft_json=json.dumps(draft, ensure_ascii=False),
            output_format=json_output_format,
        ),
        paragraph_id,
        "editor",
    )

    if edited is None:
        return draft

    reviewed = call_annotation_stage(
        reviewer_prompt.format(
            requirements=annotation_requirements,
            paragraph_id=paragraph_id,
            paragraph=paragraph,
            edited_json=json.dumps(edited, ensure_ascii=False),
            output_format=json_output_format,
        ),
        paragraph_id,
        "final reviewer",
    )

    return reviewed if reviewed is not None else edited


# ============================================================
# 6. Process the whole article
# ============================================================

paragraphs = split_paragraphs(selected_article)

result_list = []

print(f"Found {len(paragraphs)} paragraphs.\n")

for i, paragraph in enumerate(paragraphs, start=1):

    paragraph_id = f"p{i}"

    print(f"Processing {paragraph_id}...")

    result = analyze_paragraph(
        paragraph_id=paragraph_id,
        paragraph=paragraph
    )

    if result is not None:
        result_list.append(result)

        print(
            f"  Found {len(result.get('items', []))} vocabulary items."
        )

print("\nFinished.")


# ============================================================
# 7. Save results to CSV
# ============================================================

csv_file = "language_support.csv"

with open(
    csv_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "paragraph_id",
            "term",
            "importance_score",
            "explanation",
            "importance_reason",
        ]
    )

    writer.writeheader()

    for paragraph_result in result_list:

        paragraph_id = paragraph_result["paragraph_id"]

        for item in paragraph_result.get("items", []):

            writer.writerow({
                "paragraph_id": paragraph_id,
                "term": item["term"],
                "importance_score": item["importance_score"],
                "explanation": item["explanation"],
                "importance_reason": item["importance_reason"],
            })


print(f"Saved results to: {csv_file}")
