"""
Prompt templates for CompGraphRAG pipeline.
Covers extraction, hybrid generation, neuro-symbolic rule evaluation, and graph-faithfulness relation extraction.
"""

EXTRACTION_PROMPT = """
You are a Compliance Knowledge Graph Extractor operating under the CompGraphRAG HIPAA TBox.
Extract all entities and relations from the text below according to the schema:
Entities: [Regulation, Rule, Obligation, Role (CoveredEntity, BusinessAssociate), DataType (PHI), Exception (TPO, MinimumNecessary), Incident]
Relations: [governs, imposesObligation, appliesToRole, accessesData, subjectToException, supersededBy]

Return JSON array of triples: [{"subject": "...", "subject_type": "...", "relation": "...", "object": "...", "object_type": "...", "confidence": 0.95}]

Input Document:
{document_text}
"""

GENERATION_PROMPT = """
You are an Enterprise Compliance Determination Engine for HIPAA standards.
Query: {query}

Retrieved Context Passages:
{retrieved_chunks}

Retrieved Knowledge Subgraph (Path π):
{retrieved_subgraph}

Rule-Check Layer Findings:
{rule_findings}

Instructions:
1. Make a compliance determination: [COMPLIANT, NON-COMPLIANT, REQUIRES-REVIEW].
2. Provide a step-by-step natural language explanation strictly grounded in the retrieved Knowledge Subgraph π and rule-check findings.
3. Explicitly cite the traversed graph path (nodes and edges) supporting your reasoning.
4. If there is ambiguity or missing BAA/TPO evidence, output REQUIRES-REVIEW.

Format:
DETERMINATION: [COMPLIANT / NON-COMPLIANT / REQUIRES-REVIEW]
EXPLANATION: <natural language justification>
TRAVERSED_PATH_CITATIONS: [<node1> -> <relation> -> <node2>, ...]
"""

FAITHFULNESS_EXTRACTION_PROMPT = """
Extract all key relational assertions (subject, relation, object) implied by the following natural language explanation.

Explanation:
{explanation_text}

Return JSON list: [{"subject": "...", "relation": "...", "object": "..."}]
"""
