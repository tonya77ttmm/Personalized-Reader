
from openai import OpenAI
import json
import csv
import re


# ============================================================
# 1. OpenAI-compatible local agent
# ============================================================

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODEL = "gemma4:26b"


# ============================================================
# 2. Prompt
# ============================================================

prompt = """Goal:
Help primary school students who are outside the academic field understand the main idea of an academic paragraph. Rewrite the idea of the paragraph in very simple and clear English.

Input:
<input_data>
{paragraph_id}
{paragraph}
</input_data>

Rules:

1. Explain the main idea of the paragraph based only on the input paragraph.
2. Focus on what the author is trying to say, argue, or explain.
3. Rewrite the idea in simple English that a college student outside the field can understand.
4. Keep the meaning of the original paragraph. Do not add information that is not supported by the paragraph.
5. Include the most important relationship between ideas when necessary, such as cause and effect, comparison, or argument.
6. Do not explain individual difficult words. That is handled by the vocabulary support module.
7. Do not explain background concepts or theories in detail. That is handled by the knowledge support module.
8. Do not simply copy sentences from the original paragraph.
9. Do not summarize every detail. Focus on the central idea.
10. Keep the explanation concise, usually 1–3 sentences.
11. Use simple vocabulary and sentence structures.
12. If the paragraph mainly presents an argument, clearly state the main claim.
13. If the paragraph mainly explains a process, relationship, or finding, clearly explain that relationship.
14. If the paragraph does not contain a clear idea that can be simplified, return an empty "items" list.

Output:
Return valid JSON only. Do not return any other text.

Format:
{
  "paragraph_id": "p2",
  "items": [
    {
      "simplified_idea": "The author argues that scientific knowledge is influenced by the social and cultural context in which it is produced. Therefore, science may not be completely separate from society or personal perspectives."
    }
  ]
}
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

In the 1990’s Judith Butler took up the political battle over sex/gender by making the reverse move, that is, fighting against the separation of sex and gender. She did this because, in her view, this seperation had led to a privileging of sex over gender. In her iconic book Gender Trouble (1990), she emphasized that, as long as we speak of sex and gender as two separable entities, we are reiterating sex as the biological cause of gender, thereby contributing to the power hierarchy we are striving to challenge. Many misinterpreted Butler’s work to mean that the body could be reduced to discourse. However, Butler herself did not intend to deny that bodies do exist (as illustrated by her follow up work, Bodies That Matter of 1993). She merely pointed out, in agreement with such writers as Fausto-Sterling, Martin and Haraway, that we can never achieve access to an uncultured body."""


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
# 5. Call the local LLM for ONE paragraph
# ============================================================

def analyze_paragraph(paragraph_id, paragraph):
    """
    Send one paragraph to the local LLM.
    Return the parsed JSON response.
    """

    current_prompt = prompt.replace(
    "{paragraph_id}", paragraph_id
).replace(
    "{paragraph}", paragraph
)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": current_prompt
            }
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    # Remove Markdown code fences if the model adds them
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
        print(f"\nERROR: Invalid JSON for {paragraph_id}")
        print(raw_output)
        return None

    return result


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
            f"  Found {len(result.get('items', []))} concepts."
        )

print("\nFinished.")


# ============================================================
# 7. Save results to CSV
# ============================================================

csv_file = "paragraph_support.csv"

with open(
    csv_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames = [
    "paragraph_id",
    "simplified_idea",
])

    writer.writeheader()

    for paragraph_result in result_list:

        paragraph_id = paragraph_result["paragraph_id"]

        for item in paragraph_result.get("items", []):

            writer.writerow({
    "paragraph_id": paragraph_id,
    "simplified_idea": item["simplified_idea"],
})


print(f"Saved results to: {csv_file}")