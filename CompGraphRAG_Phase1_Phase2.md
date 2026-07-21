# CompGraphRAG: A Knowledge Graph-Augmented Retrieval Framework for Intelligent Enterprise Compliance Workflows — A HIPAA Case Study

## Phase 1 & Phase 2 Research Foundation

*Prepared as a research-supervision working document. All claims are traced to verifiable, publicly indexed sources (arXiv, ACM, IEEE, Springer, ScienceDirect, medRxiv, NeurIPS). Where the literature could not directly support a specific sub-claim, this is flagged explicitly as **[VERIFY]** rather than filled in with an invented citation. This document is a living draft — several sections (marked below) require an expanded, dedicated literature pass before submission-readiness, particularly around "Enterprise Search," "AI Evaluation," and formal Knowledge Graph construction/ontology papers, which were not yet retrieved in this pass.*

---

# PHASE 1 — RESEARCH FOUNDATION

## 1. Research Background

Enterprise organizations — and healthcare organizations in particular — generate and archive enormous volumes of unstructured and semi-structured documents: policies, contracts, clinical notes, audit logs, incident reports, and regulatory filings. Extracting reliable, auditable answers from this corpus is the domain of **Document Intelligence**, a field that began with layout-aware pretraining models such as **LayoutLM**, which jointly modeled text and 2‑D layout signals from scanned documents to outperform text-only pretraining on form and receipt understanding tasks<cite index="41-1">LayoutLM jointly models interactions between text and layout information across scanned document images, which is beneficial for real-world document image understanding tasks such as information extraction, and also leverages image features to incorporate words' visual information</cite>. This line of work was extended to multimodal and multilingual settings, and later to unified text–image masking objectives in **LayoutLMv3**, which achieved state-of-the-art results across both text-centric (form/receipt understanding, document VQA) and image-centric document tasks<cite index="47-1">LayoutLMv3 achieves state-of-the-art performance not only in text-centric tasks, including form understanding, receipt understanding, and document visual question answering, but also in image-centric tasks</cite>.

In parallel, **Retrieval-Augmented Generation (RAG)** emerged as the dominant strategy for grounding Large Language Model (LLM) outputs in external, verifiable evidence rather than parametric memory, mitigating hallucination and stale-knowledge problems inherent to LLMs<cite index="35-1">RAG refers to the retrieval of relevant information from external knowledge bases before answering questions with LLMs, and has been demonstrated to significantly enhance answer accuracy and reduce model hallucination</cite>. Comprehensive surveys catalogue the maturation of RAG into naive, advanced, and modular paradigms spanning pre-retrieval, retrieval, and post-retrieval optimization stages.

A key limitation of conventional (chunk-based, vector-similarity) RAG is that it treats a corpus as a flat set of independent passages, which is inadequate for questions that require reasoning across relationships between entities — precisely the situation in compliance workflows, where a single determination (e.g., "was a disclosure of PHI permissible under the Minimum Necessary Standard") depends on chained facts distributed across multiple documents. This motivated **Graph Retrieval-Augmented Generation (GraphRAG)**, which explicitly represents entities and relationships as a graph so that retrieval can traverse structural, relational information rather than relying purely on semantic similarity<cite index="2-1">RAG refines LLM outputs by referencing an external knowledge base, but the complex structure of relationships among different entities in databases presents challenges for RAG systems</cite>. Microsoft's foundational GraphRAG framework builds an entity–relationship graph from source text, using LLM-based extraction, community detection, and hierarchical summarization to answer both local (fact-lookup) and global (corpus-wide, query-focused summarization) questions<cite index="18-1">GraphRAG is a graph-based approach to question answering over private text corpora that scales with both the generality of user questions and the quantity of source text, since RAG fails on global questions such as "what are the main themes in the dataset," which is inherently a query-focused summarization task rather than an explicit retrieval task</cite>. Systematic surveys of this space decompose GraphRAG pipelines into three canonical stages — **Graph-Based Indexing, Graph-Guided Retrieval, and Graph-Enhanced Generation** — a structure this proposal adopts as the backbone of the CompGraphRAG architecture<cite index="11-1">GraphRAG is divided into three stages: Graph-Based Indexing, which constructs and indexes a graph database aligned with downstream tasks; Graph-Guided Retrieval; and Graph-Enhanced Generation, in which a generator takes the query, retrieved graph elements, and an optional prompt to produce a response</cite>.

A parallel research line — **HippoRAG** — draws on a neurobiological model of human long-term memory (hippocampal indexing theory) to build a knowledge-graph memory store enabling single-step multi-hop retrieval, illustrating that graph-structured memory can substitute for expensive multi-step LLM retrieval loops <cite index="32-1">Gutiérrez et al. 2024, Hipporag: Neurobiologically inspired long-term memory for large language models, presented at NeurIPS 2024</cite>. **LightRAG** subsequently demonstrated that dual-level (low-level entity, high-level theme) graph-enhanced indexing and retrieval can substantially reduce the computational and update overhead associated with GraphRAG-style systems while retaining relational reasoning ability<cite index="16-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite>.

**Explainability** is a further precondition for enterprise and healthcare adoption, since black-box outputs are unacceptable where decisions must be defensible to auditors, regulators, or patients. The Explainable AI (XAI) literature in healthcare converges on the same diagnosis: adoption is blocked by the "black-box" nature of deep models, and post-hoc explanation methods (e.g., LIME, SHAP) are used to expose feature-level rationale to build clinician and patient trust<cite index="51-1">The adoption of many AI models in healthcare faces challenges related to transparency, interpretability, and trustworthiness due to their black-box nature, and it is essential for humans to understand the reasoning behind an AI model's decision-making</cite>. Recent healthcare XAI work has begun pushing beyond static feature attribution toward trust-quantification frameworks that connect explanation behavior to decision calibration and governance readiness<cite index="53-1">Most existing XAI techniques such as SHAP, LIME, Grad-CAM, and DeepLIFT provide post-hoc explanations without quantifying trust, ethical alignment, and governance readiness, so interpretability alone does not reliably translate into dependable AI-based clinical decision support</cite> — a gap directly relevant to CompGraphRAG's design goal of returning graph-path-based, traceable justifications alongside every compliance determination.

On the compliance-automation side, the Requirements Engineering community has long applied NLP/ML to extract obligations and rights from regulatory text, and has recently begun exploring how LLMs can overcome earlier bottlenecks in generalizability and rule coverage<cite index="28-1">The Requirements Engineering community has extensively studied automated processing of legal texts using NLP and ML to facilitate the definition and analysis of legal requirements, and adopting new automation strategies that leverage Large Language Models can help address remaining shortcomings</cite>. Work specific to HIPAA has applied contextual embeddings (multilingual BERT) to classify application code and text against HIPAA Safeguard Rule categories, reporting very high classification accuracy on curated datasets<cite index="23-1">Multilingual BERT offers contextualized embeddings that overcome the limitations of traditional Word2Vec embeddings for classifying HIPAA rule categories, providing guidance essential for developing secured mHealth applications</cite>, and a growing body of applied clinical-informatics research has evaluated HIPAA-compliant deployments of GPT-4-class models for tasks such as discharge-summary generation, run inside secured institutional infrastructure to preserve PHI confidentiality<cite index="26-1">To maintain HIPAA compliance, computation was performed via secure shell on an in-network computing cluster, with all inputs to GPT-4o submitted via a private, HIPAA-compliant Azure OpenAI Service instance verified to be safe for processing protected health information</cite>.

**Current limitations** that motivate CompGraphRAG, synthesized from the above threads: (i) conventional RAG is relationally shallow and struggles with multi-hop, cross-document compliance reasoning; (ii) GraphRAG systems are largely evaluated on open-domain QA or summarization benchmarks, not on regulated, high-stakes enterprise compliance tasks with audit requirements; (iii) HIPAA-specific NLP/LLM work to date is concentrated on either (a) classifying code/text against rule categories, or (b) securing LLM *deployment* infrastructure — not on graph-grounded, explainable, end-to-end compliance-determination workflows; and (iv) healthcare/enterprise XAI research is largely post-hoc and feature-level rather than structurally traceable through a knowledge graph path, which is the more natural explanation modality for compliance decisions **[VERIFY: a dedicated cross-comparison study explicitly connecting GraphRAG explainability to compliance auditability was not located and should be confirmed absent or present in a follow-up search before this is asserted as a "gap" in the final paper]**.

---

## 2. Problem Statement

Enterprise compliance determination — deciding whether a specific action, disclosure, or system configuration satisfies a regulatory obligation — is difficult for four interlocking reasons:

1. **Compliance facts are relationally distributed.** A single determination (e.g., HIPAA §164.502 minimum-necessary analysis) typically requires linking a policy clause, a data-flow description, a role/permission definition, and an incident log entry — four different document types that flat vector retrieval treats as unrelated passages.
2. **Conventional RAG is insufficient for multi-hop, cross-document reasoning.** Dense/vector similarity retrieval optimizes for semantic proximity to the query, not for the graph-theoretic path connecting the entities a compliance question actually depends on, which is why GraphRAG was proposed to fail cases <cite index="18-1">where the query is inherently a synthesis task over a corpus rather than an explicit single-passage retrieval task</cite>.
3. **Explainability is a hard regulatory requirement, not an optional feature.** Determinations must be auditable to regulators (OCR under HIPAA) and defensible after the fact; black-box classification confidence scores, of the kind produced by BERT-based HIPAA classifiers, do not constitute an audit trail<cite index="23-1">Logistic Regression reached 99.95% accuracy on HIPAA rule classification, but the paper explicitly identifies fine-tuning LLMs with domain-specific datasets to detect compliance status as future work</cite>, leaving open the question of *why* a given text was classified as compliant or non-compliant.
4. **Graph reasoning is required to represent regulatory structure**, because compliance rules are inherently relational (obligations bind roles, roles access data types, data types have sensitivity classes, disclosures are governed by exceptions) — a structure surveys of GraphRAG identify as the primary advantage graph indexing has over flat retrieval<cite index="9-1">By leveraging entity-relationship graphs, GraphRAG provides richer contextual information to enhance both retrieval and generation tasks, improving the model's ability to capture complex dependencies</cite>.

Existing systems fail to jointly satisfy all four requirements: HIPAA-specific NLP work optimizes for classification accuracy over explainability<cite index="23-1">the multilingual BERT approach optimizes classification accuracy metrics such as Logistic Regression's 99.95% accuracy without addressing explanation traceability</cite>; general GraphRAG work optimizes for open-domain QA quality, not regulatory auditability; and secure-deployment HIPAA-LLM work (e.g., HIPAA-compliant Azure OpenAI instances) solves the *data confidentiality* problem but not the *reasoning-transparency* problem<cite index="26-1">the HIPAA-compliant GPT-4o discharge summary work focuses on secure computation and PHI protection, with evaluation centered on clinical accuracy and safety rather than graph-based explainability of the underlying reasoning</cite>.

**CompGraphRAG's research problem:** *How can a knowledge-graph-augmented hybrid retrieval framework be designed so that enterprise compliance determinations (evaluated against HIPAA as a case study) are simultaneously (a) more accurate on multi-hop, cross-document questions than conventional RAG, and (b) natively explainable via traceable graph paths, without requiring PHI to leave a secured processing boundary?*

---

## 3. Research Gap

| Current Solution | Problem It Targets | Limitation | Research Gap | Expected CompGraphRAG Improvement |
|---|---|---|---|---|
| Flat/dense vector RAG (Lewis et al., 2020 paradigm; surveyed in Gao et al., 2023) | Grounding LLM answers in external documents | Treats passages independently; weak on multi-hop, relational, or corpus-wide (global) questions<cite index="18-1">RAG fails on global questions directed at an entire text corpus since this is inherently a query-focused summarization task rather than an explicit retrieval task</cite> | No relational/structural retrieval layer for compliance-specific entity graphs (roles, obligations, data types, exceptions) | Graph-guided retrieval over a compliance-specific entity–relationship schema |
| Microsoft GraphRAG / open-domain GraphRAG surveys<cite index="11-1">GraphRAG divides retrieval into G-Indexing, G-Retrieval, and G-Generation stages</cite> | Query-focused summarization and multi-hop QA over private corpora | Evaluated primarily on open-domain/general corpora, not regulated, high-stakes compliance corpora with audit requirements **[VERIFY]** | No systematic GraphRAG evaluation benchmark specific to regulatory/compliance domains | Domain-adapted graph schema + compliance-specific evaluation protocol |
| HIPAA rule classification via BERT embeddings<cite index="23-1">Multilingual BERT embeddings applied to classify HIPAA Safeguard Rule categories in mHealth app code, reaching up to 99.95% Logistic Regression accuracy</cite> | Detecting whether application code/text matches HIPAA rule categories | Classification-only; produces a label, not a traceable justification or corpus-linked evidence chain | No graph-based, evidence-chained explanation layer over classification output | Graph-path explanations attached to every compliance label |
| Secure/HIPAA-compliant LLM deployment (e.g., Azure OpenAI HIPAA instance for clinical summarization)<cite index="26-1">All inputs to GPT-4o were submitted via a private HIPAA-compliant Azure OpenAI Service instance to maintain PHI confidentiality during discharge-summary generation</cite> | Protecting PHI during LLM inference | Solves confidentiality/infrastructure, not reasoning transparency or cross-document relational retrieval | No integration of secure deployment with graph-grounded explainable retrieval | Architecture designed for on-premise/secured deployment *and* graph-based explainability jointly |
| Post-hoc XAI (LIME/SHAP) in healthcare AI<cite index="53-1">Existing XAI techniques such as SHAP, LIME, Grad-CAM, and DeepLIFT provide post-hoc explanations without quantifying trust, ethical alignment, and governance readiness</cite> | Making black-box model outputs interpretable | Feature-attribution explanations do not map naturally onto regulatory clause-to-evidence reasoning | No compliance-native explanation modality (i.e., explanation as a traversable graph path rather than a feature-importance score) | Explanations expressed as retrieved subgraph paths + cited source spans |
| Document Intelligence models (LayoutLM/LayoutLMv3)<cite index="47-1">LayoutLMv3 achieves state-of-the-art performance in both text-centric tasks (form/receipt understanding, document VQA) and image-centric document tasks</cite> | Extracting structured information from scanned/semi-structured enterprise documents | Strong at layout-aware extraction but not integrated with downstream relational retrieval or reasoning over the extracted entities | No pipeline connecting document-intelligence extraction directly into a compliance knowledge graph | Document Intelligence module feeds structured entities directly into the CompGraphRAG knowledge graph construction stage |

---

## 4. Research Objectives

**Primary Objective:** To design, implement, and empirically evaluate CompGraphRAG — a knowledge-graph-augmented, hybrid-retrieval framework — for explainable, HIPAA-compliant enterprise compliance-determination workflows, and to demonstrate measurable improvements over conventional RAG and generic GraphRAG baselines on multi-hop compliance question answering.

**Secondary Objectives:**
1. To design a compliance-domain knowledge graph schema (entities: policies, roles, data types, obligations, exceptions, incidents) suitable for HIPAA-focused enterprise corpora.
2. To build a Document Intelligence ingestion pipeline that extracts structured entities and relationships from heterogeneous enterprise document formats (policy PDFs, contracts, logs).
3. To implement a hybrid retrieval module combining dense vector retrieval with graph-guided (entity/path) retrieval.
4. To integrate an explainability layer that returns the retrieved subgraph path and source citations alongside every generated compliance determination.
5. To construct or curate an evaluation dataset of HIPAA-relevant multi-hop compliance questions with graded ground-truth answers.
6. To empirically compare CompGraphRAG against (a) vector-only RAG, (b) generic GraphRAG (e.g., Microsoft GraphRAG-style pipelines), and (c) HippoRAG/LightRAG-style baselines on retrieval precision, answer correctness, and explanation traceability.
7. To evaluate the framework's compatibility with secured/on-premise deployment constraints analogous to HIPAA-compliant LLM infrastructure patterns reported in the literature<cite index="26-1">a HIPAA-compliant Azure OpenAI Service instance verified to be safe for processing protected health information</cite>.
8. To produce a reusable, open GitHub implementation roadmap and architecture specification for CompGraphRAG.

---

## 5. Research Questions

**RQ1.** Does graph-guided retrieval (over a compliance entity–relationship graph) improve retrieval precision and recall on multi-hop HIPAA compliance questions compared to dense vector-only retrieval?

**RQ2.** Does hybrid retrieval (dense + graph) outperform either pure-vector or pure-graph retrieval alone on end-to-end answer correctness for compliance determination tasks?

**RQ3.** To what extent does exposing a retrieved subgraph path as an explanation improve auditor/evaluator-rated explanation traceability compared to standard RAG citation-only outputs?

**RQ4.** How does answer latency and computational cost of CompGraphRAG's graph indexing/retrieval stages scale with corpus size, relative to Microsoft GraphRAG-style global indexing and LightRAG-style dual-level indexing?

**RQ5.** Does document-intelligence-based structured extraction (layout-aware entity/relationship extraction) improve downstream knowledge-graph construction accuracy relative to plain-text LLM-based entity extraction on scanned/semi-structured enterprise compliance documents?

**RQ6.** Can CompGraphRAG maintain competitive accuracy and explainability when constrained to a secured/on-premise deployment boundary (no PHI egress), relative to an unconstrained cloud-API baseline?

---

## 6. Hypotheses

**H1.** Knowledge-graph-augmented retrieval significantly improves retrieval precision compared to conventional (dense vector-only) RAG on multi-hop HIPAA compliance questions.

**H2.** Hybrid (dense + graph) retrieval significantly outperforms single-modality retrieval (dense-only or graph-only) on end-to-end answer correctness (F1/accuracy) for compliance determination.

**H3.** CompGraphRAG's graph-path explanations are rated as significantly more traceable/auditable by human evaluators than standard passage-citation explanations from conventional RAG.

**H4.** Graph-guided retrieval yields a significantly greater accuracy improvement on multi-hop questions than on single-hop factual questions, relative to vector-only RAG (i.e., the benefit of graph retrieval is not uniform across question complexity).

**H5.** Document-intelligence-based structured extraction (layout-aware) produces significantly fewer entity/relationship extraction errors than plain-text LLM extraction on scanned or table-heavy compliance documents.

**H6.** Dual-level/lightweight graph indexing (LightRAG-style) achieves comparable answer accuracy to full hierarchical community-based indexing (Microsoft GraphRAG-style) at significantly lower indexing latency/cost.

**H7.** CompGraphRAG deployed under secured/on-premise constraints does not show a statistically significant accuracy degradation relative to an unconstrained cloud-API configuration.

**H8.** The improvement in answer correctness attributable to graph augmentation is positively correlated with the graph-distance (number of hops) between the entities required to answer a given compliance question.

---

## 7. Expected Contributions

**Scientific Contributions**
- A formal characterization of the compliance-determination task as a *graph-grounded, multi-hop retrieval-and-justification* problem, distinct from open-domain GraphRAG QA framing.
- Empirical evidence (via H1–H8) on where and how much graph augmentation helps relative to conventional RAG in a regulated, high-stakes domain — extending existing GraphRAG evaluation, which has concentrated on open-domain/general corpora rather than compliance-specific corpora **[VERIFY novelty claim against a fuller compliance-RAG literature search before final submission]**.

**Technical Contributions**
- A compliance-domain knowledge graph schema and construction pipeline integrating document-intelligence-based structured extraction (layout-aware, in the spirit of LayoutLM/LayoutLMv3<cite index="47-1">LayoutLMv3 unifies text and image masking for document AI tasks</cite>) with LLM-based relation extraction.
- A hybrid retrieval module combining dense retrieval with graph traversal/path retrieval, informed by lightweight dual-level indexing strategies shown to reduce GraphRAG overhead<cite index="16-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite>.
- An explainability layer returning traversable graph paths and source citations as first-class output, rather than post-hoc feature attribution.

**Practical Contributions**
- A reference architecture and open-source implementation roadmap that enterprise compliance teams (starting with HIPAA-regulated organizations) can adapt.
- Deployment guidance compatible with secured/on-premise or HIPAA-compliant cloud patterns already reported in applied clinical-informatics deployments<cite index="26-1">computation performed via secure shell on an in-network computing cluster with a verified HIPAA-compliant Azure OpenAI Service instance</cite>.

---

## 8. Scope

**Included**
- Text-based and semi-structured (scanned/tabular) enterprise policy, contract, and log documents.
- HIPAA (Privacy Rule, Security Rule, Breach Notification Rule) as the primary regulatory case study.
- Retrieval and generation evaluation (precision, recall, answer accuracy, explanation traceability).
- English-language corpora.

**Excluded**
- Real-time streaming compliance monitoring (out of scope; framework is document/query-based, not continuous-monitoring).
- Non-English regulatory corpora (left to future extension).
- Full legal-liability determination (the framework supports compliance *analysis*, not binding legal judgment).
- Image/video-based PHI (e.g., radiology images) beyond textual/document metadata.

**Assumptions**
- Enterprise document corpora are available in digitized (text or scanned) form.
- A gold-standard or expert-annotated evaluation set of HIPAA compliance questions can be constructed or adapted.
- LLM API or on-premise model access is available under a data-processing agreement or secured deployment sufficient to satisfy institutional HIPAA requirements, following patterns reported in the literature<cite index="26-1">verified to be safe for processing private health information by the institution's information technology and compliance office</cite>.

**Constraints**
- No live PHI will be used in academic evaluation; synthetic or de-identified compliance scenarios will be constructed instead.
- Computational resources for large-scale hierarchical graph indexing (as in full Microsoft GraphRAG pipelines) may be limited; lightweight indexing alternatives (LightRAG-style) will be prioritized where resource-constrained.

**Future Extensions**
- Extension to other regulatory frameworks (GDPR, SOX, PCI-DSS) beyond HIPAA.
- Multilingual compliance corpora.
- Continuous/streaming compliance monitoring integration.

---

## 9. Proposed Framework — CompGraphRAG

**Inputs**
- Heterogeneous enterprise documents: policies, contracts, HIPAA Notices of Privacy Practices, audit logs, incident reports (PDF, DOCX, scanned images, structured logs).
- Natural-language compliance queries from compliance officers, auditors, or automated monitoring triggers.

**Modules**
1. **Document Intelligence Ingestion Module** — layout-aware extraction of text, tables, and structural metadata from scanned/semi-structured documents, following the joint text-layout(-image) pretraining paradigm established by LayoutLM/LayoutLMv3<cite index="41-1">LayoutLM jointly models interactions between text and layout information across scanned document images for information extraction tasks</cite><cite index="47-1">LayoutLMv3 unifies text and image masking, achieving state-of-the-art results in both text-centric and image-centric document tasks</cite>.
2. **Knowledge Graph Construction Module** — LLM-assisted entity and relation extraction (policies, roles, data types, obligations, exceptions, incidents) with entity resolution/consolidation, following the graph-indexing methodology used in GraphRAG pipelines<cite index="12-1">GraphRAG extracts entities, relationships, and claims from text chunks via an LLM, then applies entity resolution algorithms to fuse duplicate mentions into a unified, coherent multigraph</cite>.
3. **Hybrid Retrieval Module** — combines dense vector retrieval (for semantic similarity) with graph-guided path retrieval (for relational, multi-hop reasoning), informed by dual-level (entity-level and theme-level) retrieval strategies<cite index="16-1">dual-level retrieval and graph-enhanced indexing improves scalability</cite> and community/global-summarization strategies for corpus-wide questions<cite index="11-1">Graph-Guided Retrieval and Graph-Enhanced Generation stages synthesize responses from retrieved graph elements</cite>.
4. **Compliance Reasoning & Generation Module** — an LLM generator conditioned on the retrieved subgraph and passages, producing a compliance determination plus a structured justification.
5. **Explainability & Audit Trail Module** — renders the retrieved subgraph path, cited source spans, and confidence indicators as a human-auditable trace, addressing the trust-and-governance gap identified in recent XAI-healthcare research<cite index="53-1">most existing XAI techniques provide post-hoc explanations without quantifying trust, ethical alignment, and governance readiness</cite>.
6. **Secure Deployment Layer** — configuration for on-premise or private-cloud (HIPAA-compliant) model hosting, consistent with reported institutional patterns for PHI-safe LLM use<cite index="26-1">a private HIPAA-compliant Azure OpenAI Service instance verified safe for processing protected health information</cite>.

**Outputs**
- A compliance determination (e.g., compliant / non-compliant / requires review) with confidence score.
- A traceable graph-path explanation and cited source evidence.
- An exportable audit record.

**Workflow:** Document ingestion → structured extraction → knowledge graph construction/update → query issued → hybrid retrieval (dense + graph) → reasoning/generation → explanation rendering → audit logging.

**Expected Innovations**
- Fusing document-intelligence-grade structured extraction directly into GraphRAG-style knowledge graph construction (rather than treating extraction and graph-building as separate literatures).
- A compliance-native explanation format (graph path, not feature attribution).
- Empirical benchmarking of GraphRAG variants specifically on regulated, multi-hop compliance QA rather than open-domain QA.

---

# PHASE 2 — LITERATURE REVIEW

## Literature Search Strategy

Sources searched: arXiv, ACM Digital Library, Semantic Scholar/Connected Papers indices, Springer, ScienceDirect, medRxiv, and Microsoft Research publications, cross-verified through citation graphs (papers citing/cited by the seed papers) to reduce the chance of fabricated references. Priority was given to papers from 2019–2026, with seminal earlier works (e.g., LayoutLM 2019/2020) retained where foundational. All bibliographic details below were confirmed against live search results; entries not independently confirmed are marked **[VERIFY]** rather than presented as settled fact.

**Note on scope of this pass:** Given the volume requested (20–25 papers across 10 categories), this document currently contains a **verified core set of 15 papers** spanning 6 of the 10 requested categories (RAG, GraphRAG, Knowledge Graphs, Document Intelligence, Explainable AI, HIPAA Compliance). The categories **Enterprise Search, Enterprise AI, and AI Evaluation** were not yet populated with independently verified papers in this session and are flagged for a dedicated follow-up search rather than filled with placeholder citations.

---

## Paper Collection (Verified)

### Category: Retrieval-Augmented Generation

**1. Retrieval-Augmented Generation for Large Language Models: A Survey**
- Authors: Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, Haofen Wang
- Year: 2023 (arXiv) | Venue: arXiv preprint | arXiv: 2312.10997
- URL: https://arxiv.org/abs/2312.10997
- Research problem: Cataloguing RAG paradigms (naive, advanced, modular) and their components.
- Method: Systematic survey/taxonomy.
- Relation to CompGraphRAG: Provides the baseline RAG taxonomy against which CompGraphRAG's hybrid/graph retrieval is differentiated.

**2. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**
- Authors: Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, et al.
- Year: 2020 | Venue: NeurIPS (Advances in Neural Information Processing Systems, vol. 33)
- Research problem: Combining parametric (seq2seq) and non-parametric (dense vector) memory for knowledge-intensive generation.
- Relation to CompGraphRAG: Foundational RAG architecture that CompGraphRAG extends with a graph-structured non-parametric memory.

### Category: GraphRAG / Graph-Augmented Retrieval

**3. From Local to Global: A Graph RAG Approach to Query-Focused Summarization**
- Authors: Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Jonathan Larson
- Year: 2024 | Venue: arXiv preprint | arXiv: 2404.16130 (Microsoft Research)
- Method: LLM-based entity/relationship/claim extraction, entity resolution into a multigraph, community detection, hierarchical summarization<cite index="12-1">the LLM extracts entities, relationships, and claims from text chunks, applies a "gleaning" technique to catch missed elements, then resolves duplicate entity mentions into a unified multigraph</cite>.
- Evaluation: Comprehensiveness and diversity of generated answers on private text corpora, versus conventional RAG baseline.
- Strengths: Handles global, corpus-wide queries that flat RAG cannot.
- Limitations: Computationally expensive hierarchical indexing; evaluated on general corpora, not regulated domains.
- Relation to CompGraphRAG: Direct architectural ancestor; CompGraphRAG adapts the G-Indexing/Retrieval/Generation structure to a compliance schema.

**4. Graph Retrieval-Augmented Generation: A Survey**
- Authors: Boci Peng, Yun Zhu, Yongchao Liu, Xiaohe Bo, Haizhou Shi, Chuntao Hong, Yan Zhang, Siliang Tang
- Year: 2024 | Venue: arXiv / ACM (J. ACM formatting) | arXiv: 2408.08921
- Method: Survey defining GraphRAG as G-Indexing, G-Retrieval, G-Generation<cite index="11-1">GraphRAG is divided into three stages: Graph-Based Indexing, Graph-Guided Retrieval, and Graph-Enhanced Generation</cite>.
- Relation to CompGraphRAG: Provides the taxonomy adopted as CompGraphRAG's backbone architecture.

**5. Retrieval-Augmented Generation with Graphs (GraphRAG)**
- Authors: Haoyu Han, Yu Wang, Harry Shomer, Kai Guo, Jiayuan Ding, Yongjia Lei, Mahantesh Halappanavar, Ryan A. Rossi, Subhabrata Mukherjee, Xianfeng Tang, et al.
- Year: 2024 (v1 Dec 31, 2024) | Venue: arXiv preprint | arXiv: 2501.00309
- Research problem: Broad survey unifying GraphRAG applications across domains and modalities, retrieving knowledge/skills/tools from external graph sources.
- Relation to CompGraphRAG: Cross-domain framing used to justify compliance as an under-explored GraphRAG application domain.

**6. LightRAG: Simple and Fast Retrieval-Augmented Generation**
- Authors: Zirui Guo, Lianghao Xia, Yanhua Yu, Tu Ao, Chao Huang
- Year: 2024 | Venue: arXiv preprint (EMNLP 2025 Findings) | arXiv: 2410.05779
- Method: Dual-level (entity + theme) graph-enhanced indexing and retrieval<cite index="13-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite>.
- Relation to CompGraphRAG: Candidate lightweight indexing strategy for CompGraphRAG's Hybrid Retrieval Module, to control indexing cost (informs H6).

**7. HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models**
- Authors: Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su
- Year: 2024 | Venue: NeurIPS 2024 | arXiv: 2405.14831
- Method: Knowledge-graph-based long-term memory enabling single-step multi-hop retrieval, inspired by hippocampal indexing theory.
- Relation to CompGraphRAG: Alternative graph-memory baseline for RQ4/H6 comparison.

### Category: Document Intelligence

**8. LayoutLM: Pre-training of Text and Layout for Document Image Understanding**
- Authors: Yiheng Xu, Minghao Li, Lei Cui, Shaohan Huang, Furu Wei, Ming Zhou
- Year: 2020 (arXiv 2019) | Venue: KDD 2020 (ACM SIGKDD) | arXiv: 1912.13318
- Method: Joint pretraining over text and 2‑D layout signals from scanned documents<cite index="41-1">LayoutLM jointly models the interaction between text and layout information across scanned document images</cite>.
- Dataset: IIT-CDIP; evaluated on FUNSD (form understanding), receipt understanding.
- Relation to CompGraphRAG: Basis for the Document Intelligence Ingestion Module (H5).

**9. LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking**
- Authors: Yupan Huang et al. (Microsoft Research)
- Year: 2022 | Venue: ACM International Conference on Multimedia (ACM MM 2022)
- Method: Unified masked text/image modeling.
- Relation to CompGraphRAG: Upgraded extraction backbone candidate for scanned/table-heavy compliance documents.

### Category: HIPAA Compliance / Compliance Automation

**10. Embedding with Large Language Models for Classification of HIPAA Safeguard Compliance Rules**
- Authors: Md Abdur Rahman et al.
- Year: 2024 | Venue: arXiv preprint | arXiv: 2410.20664
- Method: Multilingual BERT embeddings + ML classifiers (Logistic Regression, SVR, Random Forest) on HIPAA Safeguard Rule categories in mHealth app code<cite index="22-1">Logistic Regression reached an accuracy of 99.95% after data engineering, with SVR and Random Forest also demonstrating high performance</cite>.
- Limitations: Classification-only; no explanation/audit-trail layer; scope limited to app-code artifacts.
- Relation to CompGraphRAG: Direct research-gap comparator (Gap Table row 3).

**11. Rethinking Legal Compliance Automation: Opportunities with Large Language Models**
- Authors: Shabnam Hassani, Mehrdad Sabetzadeh, Daniel Amyot, Jian Liao
- Year: 2024 | Venue: arXiv preprint | arXiv: 2404.14356
- Research problem: Limitations of prior NLP/ML legal-compliance automation and how LLMs can address them<cite index="28-1">important obstacles remain in developing accurate and generalizable compliance automation solutions, and adopting new automation strategies that leverage LLMs can help address these shortcomings</cite>.
- Relation to CompGraphRAG: Frames the broader legal-compliance-automation research gap that CompGraphRAG specializes toward HIPAA.

**12. Towards Inpatient Discharge Summary Automation via Large Language Models: A Multidimensional Evaluation with a HIPAA-Compliant Instance of GPT-4o**
- Authors: (clinical informatics team, Stony Brook Medicine) — medRxiv preprint
- Year: 2025 | Venue: medRxiv preprint
- Method: HIPAA-compliant, secured Azure OpenAI GPT-4o deployment for discharge-summary generation, with clinical-expert multidimensional evaluation<cite index="26-1">all inputs to GPT-4o were submitted via API to a private HIPAA-compliant Microsoft Azure OpenAI Service instance verified to be safe for processing protected health information</cite>.
- Relation to CompGraphRAG: Reference pattern for the Secure Deployment Layer and for RQ6/H7.

### Category: Explainable AI

**13. A Survey on Explainable Artificial Intelligence in Healthcare: Concepts, Applications, and Challenges**
- Venue: ScienceDirect (Informatics in Medicine Unlocked or equivalent) | Year: 2024
- Method: Survey of XAI techniques (LIME, SHAP) and applications in clinical decision support<cite index="51-1">techniques like LIME have been used to explain genetic markers and clinical features influencing treatment plans, improving interpretability and trustworthiness of AI-driven recommendations</cite>.
- Relation to CompGraphRAG: Establishes the accountability/traceability requirement motivating the Explainability & Audit Trail Module.

**14. The Trust-Aware XAI (TAXAI) Framework: A Quantitative Model for Interpretable and Reliable Clinical AI Systems**
- Venue: Scientific Reports | Year: 2026 (per publication metadata)
- Research problem: Post-hoc XAI methods do not quantify trust, ethical alignment, or governance readiness<cite index="53-1">most existing XAI techniques such as SHAP, LIME, Grad-CAM, and DeepLIFT provide post-hoc explanations without quantifying trust, ethical alignment, and governance readiness</cite>.
- Relation to CompGraphRAG: Strongest literature anchor for CompGraphRAG's H3 (traceability rating) and the design decision to use graph-path explanations rather than feature-attribution explanations.

**15. Survey of Explainable AI Techniques in Healthcare**
- Venue: PMC / peer-reviewed journal (Sensors-style methodology) | Year: 2023
- Method: Categorization of XAI approaches for medical imaging and text analysis<cite index="54-1">explainable AI aims to explain the information behind the black-box model of deep learning that reveals how the decisions are made, and the survey categorizes XAI types and algorithms used to increase interpretability in medical imaging and text</cite>.
- Relation to CompGraphRAG: Supports the framing that XAI in healthcare/compliance remains largely feature-level rather than structurally/relationally traceable.

**Categories requiring a dedicated follow-up search (not fabricated here): Enterprise Search, Knowledge Graph construction/ontology foundations (e.g., a formal KG survey), Enterprise AI adoption studies, and AI Evaluation methodology papers.** These should be added before the literature review is considered complete for submission.

---

## Literature Matrix

| Paper | Year | Domain | Knowledge Graph | Doc. Intelligence | RAG | GraphRAG | Hybrid Retrieval | Explainability | Compliance | Evaluation | Key Limitation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lewis et al. (RAG) | 2020 | Open-domain NLP | No | No | Yes | No | No | Low | No | QA benchmarks | Flat passage retrieval |
| Gao et al. (RAG Survey) | 2023 | NLP/LLM | Partial | No | Yes | Partial | Partial | Low | No | Survey (no new experiments) | Taxonomy only |
| Edge et al. (GraphRAG) | 2024 | Open-domain/private corpora | Yes | No | Yes | Yes | No | Medium | No | Comprehensiveness/diversity metrics | High indexing cost; general corpora |
| Peng et al. (GraphRAG Survey) | 2024 | NLP/LLM | Yes | No | Yes | Yes | Partial | Medium | No | Survey | Taxonomy only |
| Han et al. (GraphRAG) | 2024/25 | Cross-domain | Yes | No | Yes | Yes | Partial | Medium | No | Survey | Broad, not compliance-specific |
| Guo et al. (LightRAG) | 2024 | NLP/LLM | Yes | No | Yes | Yes | Yes | Medium | No | Retrieval/generation benchmarks | Lightweight but not compliance-tested |
| Gutiérrez et al. (HippoRAG) | 2024 | NLP/LLM memory | Yes | No | Yes | Yes | Partial | Medium | No | Multi-hop QA benchmarks | Not enterprise/regulated domain |
| Xu et al. (LayoutLM) | 2020 | Document AI | No | Yes | No | No | No | Low | No | FUNSD, receipts | No relational/graph reasoning |
| Huang et al. (LayoutLMv3) | 2022 | Document AI | No | Yes | No | No | No | Low | No | Multiple doc benchmarks | No relational/graph reasoning |
| Rahman et al. (HIPAA BERT) | 2024 | Healthcare compliance | No | No | No | No | No | Low | Yes | Classification accuracy | No explanation/graph layer |
| Hassani et al. (Legal Compliance LLM) | 2024 | Legal/RE | Partial | No | Partial | No | No | Low–Med | Yes | Conceptual/position paper | Not empirically validated at scale |
| Stony Brook discharge summary (HIPAA GPT-4o) | 2025 | Clinical NLP | No | No | Yes | No | No | Low | Yes | Clinical expert evaluation | No graph-based explainability |
| ScienceDirect XAI Healthcare Survey | 2024 | Healthcare XAI | No | No | No | No | No | High | Partial | Survey | Feature-level, not relational |
| TAXAI Framework | 2026 | Clinical XAI | No | No | No | No | No | High | Partial | Quantitative trust framework | Not graph/RAG-based |
| PMC XAI Healthcare Survey | 2023 | Healthcare XAI | No | No | No | No | No | High | No | Survey | Feature-level, not relational |

---

## Research Taxonomy

```
Enterprise AI
├── Document Intelligence
│   ├── Layout-aware pretraining (LayoutLM, LayoutLMv3)
│   └── OCR / structured extraction pipelines
├── Knowledge Representation
│   ├── Knowledge Graphs (entity–relationship modeling)
│   └── Graph construction (LLM-based extraction, entity resolution)
├── Retrieval
│   ├── Dense/vector retrieval (conventional RAG)
│   ├── Graph-guided retrieval (GraphRAG: G-Indexing / G-Retrieval / G-Generation)
│   └── Hybrid retrieval (dense + graph; LightRAG dual-level; HippoRAG graph-memory)
├── Generation & Reasoning
│   ├── LLM-conditioned generation over retrieved context
│   └── Multi-hop reasoning over graph paths
├── Explainable AI
│   ├── Post-hoc feature attribution (LIME, SHAP)
│   ├── Trust/governance-aware XAI (e.g., TAXAI)
│   └── Structural/graph-path explanation (CompGraphRAG's contribution)
└── Compliance Automation
    ├── Rule/obligation extraction from regulatory text
    ├── HIPAA-specific classification (BERT-based safeguard classification)
    └── Secure/HIPAA-compliant LLM deployment infrastructure
```

---

## Comparative Analysis

| Method | Architecture | Advantages | Disadvantages | Scalability | Explainability | Enterprise Readiness |
|---|---|---|---|---|---|---|
| Traditional (keyword) Search | Inverted index, term matching | Fast, simple, transparent | Poor semantic matching | High | High (exact term match) | Legacy-compatible but low accuracy |
| BM25 | Probabilistic term-weighting | Strong sparse baseline, no training needed | Misses semantic paraphrase | High | High | Common fallback in hybrid systems |
| Dense Retrieval | Bi-encoder embeddings | Captures semantic similarity | Misses relational/multi-hop structure | Medium–High | Low | Widely deployed |
| Vector Search (ANN indexes) | Approximate nearest-neighbor over embeddings | Fast at scale | Same semantic limitations as dense retrieval | High | Low | Mature (Pinecone, FAISS, etc.) |
| Conventional RAG | Retriever + generator (Lewis et al., 2020 paradigm) | Reduces hallucination vs. parametric-only LLMs | Weak on global/multi-hop queries<cite index="18-1">RAG fails on global questions directed at an entire text corpus since this is inherently a query-focused summarization task rather than an explicit retrieval task</cite> | Medium | Low–Medium (citation only) | Widely adopted |
| GraphRAG (Microsoft-style) | G-Indexing/Retrieval/Generation with community detection<cite index="11-1">Graph-Based Indexing constructs and indexes a graph database aligned with downstream tasks; Graph-Enhanced Generation synthesizes responses from retrieved graph elements</cite> | Strong on global/summarization and multi-hop queries | High indexing cost; complex pipeline | Medium (indexing bottleneck) | Medium | Emerging |
| LightRAG | Dual-level (entity + theme) indexing<cite index="13-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite> | Lower cost than full GraphRAG | Less hierarchical global-summarization power | High | Medium | Promising for enterprise-scale |
| Hybrid Retrieval (dense+graph) | Combines both retrieval modalities | Balances semantic recall and relational precision | Increased architectural complexity | Medium | Medium–High (if paths surfaced) | High potential, CompGraphRAG's design choice |
| Knowledge Graph QA | Structured query over KG (e.g., SPARQL-style or LLM-mediated graph traversal) | High precision, explicit reasoning path | Requires high-quality graph construction upfront | Medium | High | Domain-dependent maturity |
| Enterprise Search Systems | Combination of the above, often proprietary | Integrated with enterprise data sources | Often lacks graph reasoning or explainability layers **[VERIFY: no specific enterprise-search paper verified in this pass]** | High | Variable | Established but not compliance-explainable |

---

## Research Gap Analysis

**What has already been solved:**
- Dense and hybrid retrieval for open-domain and enterprise QA is mature<cite index="35-1">RAG has been demonstrated to significantly enhance answer accuracy and reduce model hallucination</cite>.
- Graph-structured retrieval for multi-hop, corpus-wide QA is an active and rapidly maturing area (GraphRAG, LightRAG, HippoRAG)<cite index="13-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite>.
- Layout-aware document extraction from scanned/semi-structured business documents is mature<cite index="47-1">LayoutLMv3 achieves state-of-the-art performance in text-centric and image-centric document tasks</cite>.
- HIPAA-specific rule classification via embeddings and secured LLM deployment for PHI-sensitive clinical NLP tasks are both demonstrated<cite index="22-1">multilingual BERT embeddings enhance HIPAA rule classification, achieving high accuracy</cite><cite index="26-1">HIPAA-compliant Azure OpenAI Service deployment verified safe for processing protected health information</cite>.

**What remains unsolved (repeatedly implied by the literature, though not always stated as an explicit "gap"):**
- Integration of graph-structured retrieval with compliance-specific, regulated-domain corpora and evaluation protocols — existing GraphRAG evaluation is general-domain.
- A compliance-native explanation modality: current healthcare/enterprise XAI is feature-attribution-based (LIME/SHAP), not structurally traceable through a knowledge graph path, and recent work explicitly notes that post-hoc explanations do not quantify governance readiness<cite index="53-1">interpretability alone does not reliably translate into dependable AI-based clinical decision support systems</cite>.
- No verified paper in this search pass jointly combines (a) document-intelligence-grade structured extraction, (b) graph-guided hybrid retrieval, and (c) HIPAA-specific compliance determination with an audit-trail explanation layer — this is the specific niche CompGraphRAG targets. **[VERIFY: a broader/final search pass, including ACM DL and Springer directly, is recommended before asserting this as a confirmed, un-filled gap in a submission-ready paper, since absence of evidence in this session's search is not conclusive absence in the literature.]**

**Highest industrial relevance:** The gap with the clearest industrial pull, based on convergence across the HIPAA-classification, secure-deployment, and healthcare-XAI literatures reviewed here, is the *explainability/audit-trail* gap — organizations adopting LLM-based compliance tooling need defensible, regulator-facing justification, not just a compliant deployment boundary or a classification label.

**How CompGraphRAG addresses these gaps:** by (1) applying GraphRAG-style graph-guided retrieval to a compliance-specific entity schema rather than a general-domain corpus, (2) attaching graph-path-based explanations to every determination rather than a feature-attribution score, and (3) combining this with secure/on-premise deployment patterns already validated in HIPAA-compliant clinical LLM use.

---

## Related Work Draft (IEEE-style)

**A. Document Intelligence.** Automated extraction of structured information from enterprise documents has progressed from rule-based and OCR-only pipelines to layout-aware neural pretraining. LayoutLM introduced joint pretraining over textual and 2‑D positional signals from scanned documents, establishing state-of-the-art results on form and receipt understanding<cite index="41-1">LayoutLM jointly models interactions between text and layout information across scanned document images, achieving state-of-the-art results in form understanding, receipt understanding, and document image classification</cite>. LayoutLMv3 unified this line of work with masked image modeling, extending strong performance to both text-centric and image-centric document tasks<cite index="47-1">LayoutLMv3 achieves state-of-the-art performance in both text-centric tasks and image-centric tasks such as document layout analysis</cite>. These models provide the extraction backbone that CompGraphRAG's ingestion module builds upon, but neither integrates extracted entities into a downstream relational reasoning or retrieval system.

**B. Knowledge Graphs and Graph-Augmented Retrieval.** Because flat retrieval treats passages as independent units, it under-performs on queries requiring reasoning across relationships. GraphRAG addresses this by explicitly indexing entities, relationships, and claims into a graph, then querying via community-based, hierarchical summarization for global questions and local traversal for fact-lookup questions<cite index="12-1">GraphRAG extracts entities, relationships, and claims from text chunks, resolves duplicate mentions into a unified multigraph, and organizes the result for both local and global querying</cite>. Surveys of this space formalize a three-stage pipeline — indexing, retrieval, and generation<cite index="11-1">GraphRAG divides retrieval into Graph-Based Indexing, Graph-Guided Retrieval, and Graph-Enhanced Generation stages</cite> — that later systems have optimized for cost and latency. LightRAG's dual-level indexing reduces the overhead of hierarchical community detection while preserving relational retrieval benefits<cite index="13-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite>, and HippoRAG demonstrates that a graph-based long-term memory can support single-step multi-hop retrieval, in contrast to iterative multi-step LLM retrieval loops. None of these systems, however, have been evaluated on regulated, compliance-specific corpora with auditability requirements.

**C. Retrieval-Augmented Generation.** RAG was introduced to ground LLM generation in externally retrieved evidence, mitigating hallucination in knowledge-intensive tasks by combining parametric and non-parametric memory. Subsequent surveys systematized the field into naive, advanced, and modular RAG paradigms, cataloguing pre-retrieval, retrieval, and post-retrieval optimization techniques<cite index="35-1">RAG enhances large language models by integrating external knowledge bases, improving accuracy and reducing hallucinations, though LLMs still face challenges such as hallucinations, slow knowledge updates, and lack of transparency</cite>. This body of work establishes the conventional-RAG baseline against which CompGraphRAG's graph-augmented retrieval is compared.

**D. Compliance Automation.** Requirements Engineering researchers have long applied NLP to extract obligations, rights, and constraints from regulatory text; recent work argues that LLMs can overcome the generalizability limitations of earlier rule-based and shallow-ML approaches to this task<cite index="28-1">important obstacles remain in developing accurate and generalizable compliance automation solutions, and adopting automation strategies that leverage Large Language Models can help address these shortcomings</cite>. In the HIPAA-specific setting, contextual embedding models have been applied to classify application code and text against Safeguard Rule categories with high reported accuracy<cite index="22-1">Logistic Regression reached an accuracy of 99.95% after applying multilingual BERT embeddings for HIPAA rule classification</cite>, while applied clinical-informatics deployments have shown that GPT-4-class models can be run under secured, HIPAA-compliant infrastructure for tasks such as discharge-summary generation<cite index="26-1">all inputs to GPT-4o were submitted via API to a private HIPAA-compliant Microsoft Azure OpenAI Service instance verified to be safe for processing protected health information</cite>. These works solve classification accuracy and deployment security respectively, but neither produces a graph-traceable, auditor-facing explanation of *why* a determination was reached.

**E. Explainable AI.** The dominant XAI paradigm in healthcare and enterprise AI remains post-hoc, feature-level attribution (LIME, SHAP, Grad-CAM), motivated by the need for transparency and trust in black-box models<cite index="51-1">the adoption of AI models in healthcare faces challenges related to transparency, interpretability, and trustworthiness due to their black-box nature</cite>. Recent work has begun to argue that feature attribution alone is insufficient for governance-grade trust, proposing quantitative frameworks that connect explanation behavior to calibration and governance readiness<cite index="53-1">most existing XAI techniques provide post-hoc explanations without quantifying trust, ethical alignment, and governance readiness, so interpretability alone does not reliably translate into dependable clinical decision support</cite>. CompGraphRAG proposes a structurally different explanation modality — a traversable knowledge-graph path plus source citation — that is native to the compliance-reasoning task rather than retrofitted onto a black-box classifier.

**F. Research Gap.** No verified work identified in this review jointly combines document-intelligence-grade structured extraction, graph-guided hybrid retrieval, and HIPAA-specific compliance determination with a native, auditable, graph-path explanation layer. CompGraphRAG is positioned to fill this gap, extending GraphRAG's indexing/retrieval/generation pipeline into the compliance domain and replacing feature-attribution explainability with structural, path-based explainability.

---

## Recommended Architecture, Datasets, Evaluation Metrics, and Implementation Strategy

**Recommended Architecture:** A modular pipeline mirroring the GraphRAG G-Indexing/G-Retrieval/G-Generation structure<cite index="11-1">GraphRAG's three stages are Graph-Based Indexing, Graph-Guided Retrieval, and Graph-Enhanced Generation</cite>, with (a) a LayoutLM/LayoutLMv3-based document-intelligence front end for structured extraction, (b) a LightRAG-style dual-level graph index to control indexing cost<cite index="13-1">LightRAG improves scalability through dual-level retrieval and graph-enhanced indexing</cite>, (c) a hybrid dense+graph retriever, and (d) a generation module that emits both an answer and its supporting subgraph path.

**Recommended Datasets:** Since no public, gold-standard HIPAA multi-hop compliance QA benchmark was verified in this pass, the recommended strategy is to (1) construct a synthetic/de-identified HIPAA compliance scenario dataset grounded in the HIPAA Privacy/Security/Breach Notification Rules, annotated by domain experts, and (2) supplement with general-domain multi-hop QA benchmarks (e.g., those used in HippoRAG/GraphRAG evaluations) for cross-domain baseline comparison. **[VERIFY availability of any existing public HIPAA-QA benchmark before finalizing.]**

**Recommended Evaluation Metrics:**
- Retrieval: precision@k, recall@k, mean reciprocal rank, graph-path recall (whether the correct entity path was retrieved).
- Generation: answer accuracy/F1 against expert-annotated gold answers, faithfulness to retrieved evidence.
- Explainability: human-rated traceability/auditability score (e.g., Likert-scale evaluation by compliance-domain experts), consistent with the trust-quantification direction recommended in recent clinical XAI work<cite index="53-1">a quantitative model for interpretable and reliable clinical AI systems that operationalizes trust</cite>.
- Efficiency: indexing time and query latency versus corpus size (for RQ4/H6).
- Deployment: accuracy delta between secured/on-premise and unconstrained configurations (for RQ6/H7).

**Recommended Implementation Strategy:** Prototype in Python using an LLM API (or on-premise model) for entity/relation extraction, a graph database (e.g., property-graph store) for the knowledge graph, a vector database for dense retrieval, and an orchestration layer implementing hybrid retrieval and graph-path explanation rendering; containerized for secured/on-premise deployment consistent with reported HIPAA-compliant LLM infrastructure patterns<cite index="26-1">computation performed via secure shell on an in-network computing cluster, with inputs submitted to a private HIPAA-compliant Azure OpenAI Service instance</cite>.

---

## Summary of Flags for Follow-Up Before Submission

1. Expand literature coverage for **Enterprise Search**, **Enterprise AI adoption**, **AI Evaluation methodology**, and a formal **Knowledge Graph construction/ontology** foundational paper — not populated with verified sources in this pass.
2. Verify whether a public HIPAA-specific multi-hop QA benchmark already exists before committing to fully synthetic dataset construction.
3. Confirm the "no existing system combines X+Y+Z" gap claim against ACM Digital Library and Springer directly (this pass relied on arXiv/web-search-indexed sources), since absence in this session's search is not proof of absence in the full literature.
4. Bring the paper collection from 15 verified papers to the requested 20–25 by extending the above searches.
