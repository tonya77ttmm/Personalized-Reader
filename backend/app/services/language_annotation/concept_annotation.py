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
# 2. Prompt. examples/ paper selection/ ? gap?
# ============================================================
#persona user stories 

#prior parapgraph as context
# high school students

prompt = """Goal:
Help high school students with no background in the academic field understand the important concepts or background knowledge needed to understand an academic paragraph.

Identify only concepts, theories, ideas, events, processes, or other background knowledge that a general reader needs to understand the paragraph. For each selected item, explain it briefly in very simple English.

Input:
<input_data>
{paragraph_id}
{paragraph}
</input_data>

Rules:

1. Select concepts based ONLY on the input paragraph.
   Select concepts, theories, ideas, events, processes, or background knowledge that are important for understanding the paragraph.
   Do NOT select a difficult word only because it is difficult.

2. Be selective.
   Do not explain everything in the paragraph.
   Prioritize concepts that are necessary or useful for comprehension.
   If two concepts express substantially the same underlying idea, keep the one that is more important for understanding the paragraph.
   If no important concept or background knowledge is needed, return an empty "items" list.

3. Give each selected item an importance score:
   - 3 = Essential: Without understanding this concept, the reader would likely misunderstand the main point of the paragraph.
   - 2 = Helpful: The main point is still understandable, but an important part would be difficult to understand without this concept.
   - 1 = Incidental: Useful background knowledge, but not necessary for understanding the main idea.

   Be conservative with score 3.
   When uncertain between 3 and 2, choose 2.

4. Explain each concept for a high school student with no background in the field.
   Use plain, everyday language.
   Prefer ONE sentence.
   Use TWO sentences only when necessary.

   The explanation should answer:
   "What does this concept mean here in simple everyday language?"

5. Explain the underlying idea, not just a simpler synonym or dictionary definition.
   If a concept has several meanings, explain ONLY the meaning relevant to this paragraph.

   GOOD:
   "A stereotype is a simplified idea about a group that may not describe every person in that group."

   GOOD:
   "The Industrial Revolution was a period when machines changed how goods were made and how people worked."

   BAD:
   "The Industrial Revolution refers to a period of socioeconomic transformation characterized by mechanization and industrialization."

6. Avoid unnecessary academic terminology.
   Do not define one difficult concept using another difficult concept.
   If an academic term is necessary, explain it immediately in ordinary language.

   BAD:
   "Social constructionism is an epistemological framework."

   GOOD:
   "It is the idea that what people accept as knowledge or truth can be influenced by society and by the people who produce that knowledge."

7. Explain the concept itself, not the whole paragraph.
   Do NOT summarize, paraphrase, or restate the paragraph.

8. Keep "explanation" and "importance_reason" separate.

   "explanation":
   What the concept means in simple language.

   "importance_reason":
   Why understanding this concept helps the reader understand THIS paragraph.

   Do not include the importance reason inside the explanation.

9. Keep explanations simple but conceptually accurate.
   Do not make a theory or idea stronger, broader, or more absolute than the paragraph supports.

   Avoid claims such as:
   - "There is no truth."
   - "Everything is socially constructed."
   - "Nothing is objective."

   unless the paragraph explicitly supports that claim.

   Avoid words such as "always", "all", "everything", "nothing", and "completely" unless they are justified by the paragraph.

10. Do not introduce outside theories, researchers, events, interpretations, criticism, or technical terms unless they are necessary to explain a selected concept.
    Do not assume the reader already knows related academic concepts.

11. Before producing the answer, review the selected items ONCE:
    - Is each concept important for understanding the paragraph?
    - Are overlapping or redundant concepts removed?
    - Does each explanation reflect what the concept means IN THIS PARAGRAPH?
    - Could a high school student understand it?
    - Is it short and written in ordinary language?
    - Is it accurate without exaggerating the author's claim?
    - Is the importance score justified?

    After this single review, immediately produce the final JSON.
    Do not repeatedly reconsider or review the selection.

Output:
Return valid JSON only.
Do not return reasoning, commentary, Markdown, or any text outside the JSON.

Format:
{
  "paragraph_id": "p2",
  "items": [
    {
      "concept": "social constructionism",
      "importance_score": 3,
      "explanation": "What people accept as knowledge or truth can be influenced by society and by the people who produce that knowledge.",
      "importance_reason": "The paragraph uses this idea to explain why scientific knowledge should not automatically be treated as completely objective."
    }
  ]
}
"""

# ============================================================
# 3. Your article
# ============================================================

selected_article = """Academic and activist feminist inquiry has repeatedly tried to come to terms with the question of what we might mean by the curious and inescapable term "objectivity." We have used a lot of toxic ink and trees processed into paper decrying what they have meant and how it hurts us. The imagined "they" constitute a kind of invisible conspiracy of masculinist scientists and philosophers replete with grants and laboratories. The imagined "we" are the embodied others, who are not allowed not to have a body, a finite point of view, and so an inevitably disqualifying and polluting bias in any discussion of consequence outside our own little circles, where a "mass"-subscription journal might reach a few thousand readers composed mostly of science haters. At least, I confess to these paranoid fantasies and academic resentments lurking underneath some convoluted reflections in print under my name in the feminist literature in the history and philosophy of science. We, the feminists in the debates about science and technology, are the Reagan era's "special-interest groups" in the rarified realm of epistemology, where traditionally what can count as knowledge is policed by philosophers codifying cognitive canon law. Of course, a special-interest group is, by Reaganoid definition, any collective historical subject that dares to resist the stripped-down atomism of Star Wars, hypermarket, postmodern, media-simulated citizen-ship. Max Headroom doesn't have a body; therefore, he alone sees everything in the great communicator's empire of the Global Net-work. No wonder Max gets to have a naive sense of humor and a kind of happily regressive, preoedipal sexuality, a sexuality that we ambivalently - with dangerous incorrectness- had imagined to be reserved for lifelong inmates of female and colonized bodies and maybe also white male computer hackers in solitary electronic confinement.

It has seemed to me that feminists have both selectively and flexibly used and been trapped by two poles of a tempting dichotomy on the question of objectivity. Certainly I speak for myself here, and I offer the speculation that there is a collective discourse on these matters. Recent social studies of science and technology, for example, have made available a very strong social constructionist argument for all forms of knowledge claims, most certainly and especially scientific ones. According to these tempting views, no insider's perspective is privileged, because all drawings of inside-outside boundaries in knowledge are theorized as power moves, not moves toward truth. So, from the strong social constructionist perspective, why should we be cowed by scientists' descriptions of their activity and accomplishments; they and their patrons have stakes in throwing sand in our eyes. They tell parables about objectivity and scientific method to students in the first years of their initiation, but no practitioner of the high scientific arts would be caught dead acting on the textbook versions.

Social constructionists make clear that official ideologies about objectivity and scientific method are particularly bad guides to how scientific knowledge is actually made. Just as for the rest of us, what scientists believe or say they do and what they really do have a very loose fit.

The only people who end up actually believing and, goddess forbid, acting on the ideological doctrines of disembodied scientific objectivity - enshrined in elementary textbooks and technoscience booster literature - are nonscientists, including a few very trusting philosophers. Of course, my designation of this last group is probably just a reflection of a residual disciplinary chauvinism acquired from identifying with historians of science and from spending too much time with a microscope in early adulthood in a kind of disciplinary preoedipal and modernist poetic moment when cells seemed to be cells and organisms, organisms. Pace, Gertrude Stein. But then came the law of the father and its resolution of the problem of objectivity, a problem solved by always already absent referents, deferred signifieds, split subjects, and the endless play of signifiers. Who wouldn't grow up warped? Gender, race, the world itself - all seem the effects of warp speeds in the play of signifiers in a cosmic force field.

In any case, social constructionists might maintain that the ideological doctrine of scientific method and all the philosophical verbiage about epistemology were cooked up to distract our attention from getting to know the world effectively by practicing the sciences. From this point of view, science - the real game in town - is rhetoric, a series of efforts to persuade relevant social actors that one's manufactured knowledge is a route to a desired form of very objective power. Such persuasions must take account of the structure of facts and artifacts, as well as of language-mediated actors in the knowledge game. Here, artifacts and facts are parts of the powerful art of rhetoric. Practice is persuasion, and the focus is very much on practice. All knowledge is a condensed node in an agonistic power field. The strong program in the sociology of knowledge joins with the lovely and nasty tools of semiology and deconstruction to insist on the rhetorical nature of truth, including scientific truth. History is a story Western culture buffs tell each other; science is a contestable text and a power field; the content is the form. Period.

So much for those of us who would still like to talk about reality with more confidence than we allow to the Christian Right when they discuss the Second Coming and their being raptured out of the final destruction of the world. We would like to think our appeals to real worlds are more than a desperate lurch away from cynicism and an act of faith like any other cult's, no matter how much space we generously give to all the rich and always historically specific mediations through which we and everybody else must know the world. But the further I get in describing the radical social constructionist program and a particular version of postmodernism, coupled with the acid tools of critical discourse in the human sciences, the more nervous I get. The imagery of force fields, of moves in a fully textualized and coded world, which is the working metaphor in many arguments about socially negotiated reality for the postmodern subject, is, just for starters, an imagery of high-tech military fields, of automated academic battle-fields, where blips of light called players disintegrate each other in order to stay in the knowledge and power game. Technoscience and science fiction collapse into the sun of their radiant (ir)reality - war. It shouldn't take decades of feminist"""


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
        print(f"raw response: {response}")
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

csv_file = "knowledge_support.csv"

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
    "concept",
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
    "concept": item["concept"],
    "importance_score": item["importance_score"],
    "explanation": item["explanation"],
    "importance_reason": item["importance_reason"],
})


print(f"Saved results to: {csv_file}")