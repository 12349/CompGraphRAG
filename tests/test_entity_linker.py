"""
Unit tests for EntityLinker — added per Stage 5 Task 5 recommendation.
Tests cover: general linking, synonym expansion, no-match handling,
novel-scenario generalization, and a harness accuracy regression pin.

Stage 6 (2026-08-20): These tests were absent when the datasets/ → benchmark_datasets/
rename bug silently degraded the encoder; the regression test here ensures that
kind of silent drop gets caught automatically in CI.
"""

import os
import unittest
from benchmark_datasets.candidate_corpus import CandidateCorpus
from retrieval.entity_linker import EntityLinker


class TestEntityLinker(unittest.TestCase):

    def setUp(self):
        self.corpus = CandidateCorpus()
        self.linker = EntityLinker([{"id": n, "label": n}
                                    for n in self.corpus.graph.nodes()])

    # -------------------------------------------------------------------
    # Test 1: General linking — PHI + BAA query
    # -------------------------------------------------------------------
    def test_general_linking_phi_baa(self):
        """A covered entity disclosing PHI to a cloud vendor should link
        CoveredEntity_A, CloudVendor_B, and BAA_Document."""
        query = ("Can a covered entity disclose PHI to a cloud vendor without "
                 "an executed Business Associate Agreement?")
        linked = self.linker.link_query_entities(query)
        pred = {n for n, c in linked if c >= 0.25}

        self.assertIn("CoveredEntity_A", pred,
                      "CoveredEntity_A should be linked for 'covered entity' query")
        self.assertIn("CloudVendor_B", pred,
                      "CloudVendor_B should be linked for 'cloud vendor' query")
        # BAA_Document is expected to be reachable via synonym 'baa' → 'BAA'
        self.assertTrue(
            any("BAA" in n for n in pred),
            "At least one BAA node should be linked when 'BAA' appears in query"
        )

    # -------------------------------------------------------------------
    # Test 2: EMT treatment-exception linking
    # -------------------------------------------------------------------
    def test_emt_treatment_exception_linking(self):
        """An EMT query should link EMT_Provider and Hospital_ED via the 'emt'
        synonym expansion. The linker expands 'emt' → 'EMT' which matches
        EMT_Provider tokens. Query must contain the acronym 'EMT' for expansion
        to fire (the linker does not handle 'emergency medical technician' as a
        multi-token phrase expansion — that is a documented gap in the synonym
        table)."""
        query = "Is an EMT allowed to share PHI with a receiving hospital during transport?"
        linked = self.linker.link_query_entities(query)
        pred = {n for n, c in linked if c >= 0.25}

        self.assertIn("EMT_Provider", pred,
                      f"EMT_Provider should be linked for 'EMT' query. Got: {pred}")
        self.assertIn("Hospital_ED", pred,
                      f"Hospital_ED should be linked for hospital query. Got: {pred}")

    # -------------------------------------------------------------------
    # Test 3: No-match handling — gibberish query should not create
    # high-confidence spurious links
    # -------------------------------------------------------------------
    def test_no_match_gibberish_query(self):
        """A query with no HIPAA terminology should return no high-confidence links."""
        query = "xkqz blorp frungulate qwerty 123 zzz test gibberish"
        linked = self.linker.link_query_entities(query)
        high_conf = [n for n, c in linked if c >= 0.5]
        self.assertEqual(high_conf, [],
                         "Gibberish query should produce no high-confidence links")

    # -------------------------------------------------------------------
    # Test 4: Novel-scenario generalization — encryption violation
    # -------------------------------------------------------------------
    def test_novel_unencrypted_ftp_links_encryption_nodes(self):
        """A novel query about unencrypted FTP to an overseas company should
        link billing/encryption nodes even though this exact scenario is not
        in the 24-item benchmark."""
        query = ("A hospital billing department sends patient records via "
                 "unencrypted FTP to an overseas revenue cycle vendor.")
        linked = self.linker.link_query_entities(query)
        pred = {n for n, c in linked if c >= 0.25}

        # Expect UnencryptedEmail or similar unencrypted-PHI node to fire
        unencrypted_nodes = {n for n in pred if "Unencrypted" in n or "Billing" in n}
        self.assertTrue(len(unencrypted_nodes) > 0,
                        f"Expected unencrypted/billing nodes in links, got {pred}")

    # -------------------------------------------------------------------
    # Test 5: Synonym expansion — 'irb' maps to IRB nodes
    # -------------------------------------------------------------------
    def test_synonym_irb_expansion(self):
        """Query mentioning 'IRB' (acronym) should expand to link IRB_Waiver
        or IRB_MasterApproval nodes."""
        query = "Does research using de-identified data require an IRB waiver?"
        linked = self.linker.link_query_entities(query)
        pred = {n for n, c in linked if c >= 0.25}

        irb_nodes = {n for n in pred if "IRB" in n}
        self.assertTrue(len(irb_nodes) > 0,
                        f"IRB synonym should expand to at least one IRB node, got {pred}")


class TestEvalHarnessAccuracyRegression(unittest.TestCase):
    """
    Regression test: pins the harness to its current verified accuracy so
    any future silent change to the retrieval pipeline, encoder, or dataset
    is caught immediately — not five audit stages later.

    This test is intentionally strict: exact match, not a range.
    If the number changes, the test fails, which forces a conscious decision
    about whether the change was intentional and correct.

    Canonical result (Stage 6, 2026-08-20):
        CG=100.0% (24/24), VR=87.5% (21/24)
        Encoder: sentence-transformers/all-MiniLM-L6-v2
        Revision: 1110a243fdf4706b3f48f1d95db1a4f5529b4d41
    """

    def test_harness_accuracy_pinned(self):
        """CompGraphRAG must achieve exactly 24/24 on the benchmark."""
        dataset_file = os.path.join(
            os.path.dirname(__file__), "..", "datasets", "hipaa_gold_dataset.json"
        )
        # Import here so the test only fails if accuracy changes, not on import errors
        from eval.eval_harness import CompGraphRAGEvaluator
        evaluator = CompGraphRAGEvaluator(dataset_file)
        results = evaluator.run_evaluation(run_stats=False)  # skip stats for speed

        cg = results["overall_compgraphrag_accuracy"]
        vr = results["overall_vector_rag_accuracy"]

        self.assertEqual(results["total_queries_evaluated"], 24,
                         "Dataset must contain exactly 24 queries")
        self.assertAlmostEqual(cg, 1.0, places=4,
                               msg=f"CG accuracy regressed: expected 1.0000, got {cg:.4f} "
                                   f"({round(cg*24)}/24). Check encoder, dataset, corpus, "
                                   f"or retrieval changes.")
        self.assertAlmostEqual(vr, 0.875, places=4,
                               msg=f"VR accuracy changed: expected 0.8750, got {vr:.4f}")

    def test_encoder_is_real_not_hash_fallback(self):
        """Verify the real sentence-transformers encoder is active.
        If this fails, the datasets/ namespace collision has been re-introduced
        or the sentence-transformers library is unavailable."""
        from retrieval.hybrid_scorer import HybridScorer
        scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1, force_hash_fallback=False)
        enc = scorer._get_encoder()
        self.assertIsNot(enc, False,
                         "Real ST encoder must be active. If False, the `benchmark_datasets` "
                         "package rename may have been reverted, or ST is not installed.")
        emb = enc.encode("HIPAA PHI disclosure")
        self.assertEqual(len(emb), 384,
                         f"Expected 384-dim all-MiniLM-L6-v2 embedding, got {len(emb)}-dim. "
                         "Encoder may have changed model.")


if __name__ == "__main__":
    unittest.main()
