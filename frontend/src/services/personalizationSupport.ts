export type SupportKind = "language" | "concept" | "paragraph";

export type LanguageSupportRow = {
  paragraph_id: string;
  term: string;
  importance_score: number;
  explanation: string;
  importance_reason: string;
};

export type ConceptSupportRow = {
  paragraph_id: string;
  concept: string;
  importance_score: number;
  explanation: string;
  importance_reason: string;
};

export type ParagraphSupportRow = {
  paragraph_id: string;
  simplified_idea: string;
};

export type PersonalizationSupportItem = {
  paragraphId: string;
  kind: SupportKind;
  title: string;
  text: string;
  source: string;
};

export type FixationEntry = {
  paragraphId: string;
  timestamp: number;
  confusion: number;
};

export const languageSupportRows: LanguageSupportRow[] = [
  {
    paragraph_id: "p1",
    term: "situated knowledges",
    importance_score: 3,
    explanation: "Ideas shaped by a person’s background, experiences, and place in society.",
    importance_reason: "This is the core idea the paragraph introduces.",
  },
  {
    paragraph_id: "p2",
    term: "unbiased",
    importance_score: 2,
    explanation: "Not taking sides or being completely neutral.",
    importance_reason: "The paragraph argues that science is not always neutral.",
  },
  {
    paragraph_id: "p3",
    term: "objective",
    importance_score: 2,
    explanation: "Based only on facts, without personal or social bias.",
    importance_reason: "The paragraph says this belief about science is often assumed but questioned.",
  },
  {
    paragraph_id: "p4",
    term: "neutral standpoint",
    importance_score: 2,
    explanation: "A position that is not shaped by personal opinions or social politics.",
    importance_reason: "The paragraph argues that researchers cannot be fully neutral.",
  },
  {
    paragraph_id: "p6",
    term: "latent political potential",
    importance_score: 2,
    explanation: "A hidden ability for a scientific idea to affect politics or social power later.",
    importance_reason: "The author says scientific definitions can cause political effects even if they seem neutral.",
  },
  {
    paragraph_id: "p7",
    term: "division of labor",
    importance_score: 2,
    explanation: "How work and household tasks are split between people.",
    importance_reason: "It helps explain why housework was assigned unequally in the example.",
  },
];

export const conceptSupportRows: ConceptSupportRow[] = [
  {
    paragraph_id: "p2",
    concept: "situated knowledges",
    importance_score: 3,
    explanation: "What people know is shaped by their background, experiences, and social position.",
    importance_reason: "This is the main framework introduced in the paragraph.",
  },
  {
    paragraph_id: "p3",
    concept: "feminist STS",
    importance_score: 3,
    explanation: "A way of studying science that asks how social ideas and gender influence research.",
    importance_reason: "It is the lens used to explain why scientific claims about sex and gender are questioned.",
  },
  {
    paragraph_id: "p4",
    concept: "political categories",
    importance_score: 2,
    explanation: "Labels for social groups that carry expectations and political meaning.",
    importance_reason: "This helps explain why terms like men and women are not just biological facts.",
  },
  {
    paragraph_id: "p7",
    concept: "sex and gender distinction",
    importance_score: 3,
    explanation: "The idea that sex is about biology while gender is about social roles and expectations.",
    importance_reason: "This distinction is central to the argument that gender roles are not naturally fixed by biology.",
  },
  {
    paragraph_id: "p9",
    concept: "power hierarchy",
    importance_score: 2,
    explanation: "A system where some groups or ideas are treated as more important or more powerful than others.",
    importance_reason: "Butler argues that separating sex and gender can keep unfair hierarchies in place.",
  },
];

export const paragraphSupportRows: ParagraphSupportRow[] = [
  {
    paragraph_id: "p2",
    simplified_idea: "Researchers used new methods to challenge the idea that science is always neutral and unbiased.",
  },
  {
    paragraph_id: "p3",
    simplified_idea: "The author argues that scientific research about sex and gender is often shaped by stereotypes and social assumptions.",
  },
  {
    paragraph_id: "p4",
    simplified_idea: "The author argues that science is never truly neutral because it is always shaped by social and political assumptions.",
  },
  {
    paragraph_id: "p6",
    simplified_idea: "The author will use examples to show that scientific ideas about sex and gender can also carry political effects.",
  },
  {
    paragraph_id: "p7",
    simplified_idea: "The author explains that separating biological sex from social gender roles helps question why women were expected to do more housework.",
  },
  {
    paragraph_id: "p9",
    simplified_idea: "Judith Butler argues that we should not treat sex and gender as separate because doing so makes biology look like the cause of gender and keeps unfair power structures in place.",
  },
];

export function inferFixationMode(
  entries: FixationEntry[],
  windowMs = 3000,
): string | null {
  const now = Date.now();
  const recentEntries = entries.filter(
    (entry) => now - entry.timestamp <= windowMs,
  );

  if (recentEntries.length === 0) {
    return null;
  }

  const counts = new Map<string, number>();
  for (const entry of recentEntries) {
    counts.set(entry.paragraphId, (counts.get(entry.paragraphId) ?? 0) + 1);
  }

  const [modeParagraphId] = [...counts.entries()].sort((a, b) => b[1] - a[1])[0] ?? [null];
  return modeParagraphId ?? null;
}

export function getLanguageSupportForParagraph(
  paragraphId: string,
): PersonalizationSupportItem[] {
  return languageSupportRows
    .filter((row) => row.paragraph_id === paragraphId)
    .slice(0, 3)
    .map((row) => ({
      paragraphId,
      kind: "language",
      title: row.term,
      text: row.explanation,
      source: "language_support.csv",
    }));
}

export function getConceptSupportForParagraph(
  paragraphId: string,
): PersonalizationSupportItem[] {
  return conceptSupportRows
    .filter((row) => row.paragraph_id === paragraphId)
    .slice(0, 3)
    .map((row) => ({
      paragraphId,
      kind: "concept",
      title: row.concept,
      text: row.explanation,
      source: "knowledge_support.csv",
    }));
}

export function getParagraphSupportForParagraph(
  paragraphId: string,
): PersonalizationSupportItem[] {
  return paragraphSupportRows
    .filter((row) => row.paragraph_id === paragraphId)
    .slice(0, 1)
    .map((row) => ({
      paragraphId,
      kind: "paragraph",
      title: `Paragraph support`,
      text: row.simplified_idea,
      source: "paragraph_support.csv",
    }));
}
