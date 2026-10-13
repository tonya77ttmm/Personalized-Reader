
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

MODEL = "gemma4:e4b"


# ============================================================
# 2. Prompt
# ============================================================

prompt = """Goal:
Help college students who are outside the academic field understand the main idea of an academic paragraph. Rewrite the idea of the paragraph in very simple and clear English.

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