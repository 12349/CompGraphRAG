"""
Candidate Knowledge Graph Corpus & Passage Store for CompGraphRAG Un-leaked Retrieval.
Maintains standalone regulatory knowledge graph nodes, path chains, and candidate text passages.
"""

import networkx as nx
from typing import List, Dict, Any

class CandidateCorpus:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.passages = []
        self._build_candidate_corpus()

    def _build_candidate_corpus(self):
        """Constructs standalone candidate knowledge graph and passage store."""
        
        # Define candidate edge chains across 1-4 hop compliance paths (including targets & distractors)
        candidate_paths = [
            # Q1-Q6 (1-Hop)
            [{"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception", "confidence": 0.95}],
            [{"source": "PsychotherapyNotes", "relation": "excludedFrom", "target": "TPO_Exception", "confidence": 0.95}],
            [{"source": "PHI_Disclosure", "relation": "subjectToException", "target": "JudicialSubpoena_Exception", "confidence": 0.95}],
            [{"source": "PatientAccessFee", "relation": "satisfiesStandard", "target": "CostBasedFeeRule", "confidence": 0.95}],
            [{"source": "LawEnforcementDisclosure", "relation": "violatessafeguard", "target": "PrivacyRule_LawEnforcement", "confidence": 0.95}],
            [{"source": "EmergencyFamilyDisclosure", "relation": "subjectToException", "target": "EmergencyCarveout", "confidence": 0.95}],
            # Distractor 1-Hop
            [{"source": "PHI_Disclosure", "relation": "requiresAuthorization", "target": "GeneralPatientConsent", "confidence": 0.50}],
            
            # Q7-Q12 (2-Hop)
            [
                {"source": "CoveredEntity_A", "relation": "disclosesPHITo", "target": "CloudVendor_B", "confidence": 0.90},
                {"source": "CloudVendor_B", "relation": "lacksAgreement", "target": "BAA_Document", "confidence": 0.95}
            ],
            [
                {"source": "EMT_Provider", "relation": "transmitsPHI", "target": "Hospital_ED", "confidence": 0.95},
                {"source": "Hospital_ED", "relation": "qualifiesAs", "target": "TreatmentActivity", "confidence": 0.95}
            ],
            [
                {"source": "BusinessAssociate_1", "relation": "disclosesPHITo", "target": "SubcontractorHost_2", "confidence": 0.90},
                {"source": "SubcontractorHost_2", "relation": "lacksAgreement", "target": "SubcontractorBAA", "confidence": 0.95}
            ],
            [
                {"source": "Hospital_A", "relation": "disclosesPHITo", "target": "CollectionAgency_B", "confidence": 0.95},
                {"source": "CollectionAgency_B", "relation": "satisfiesStandard", "target": "BAA_Agreement", "confidence": 0.95}
            ],
            [
                {"source": "BillingDepartment", "relation": "transmitsData", "target": "UnencryptedEmail", "confidence": 0.95},
                {"source": "UnencryptedEmail", "relation": "violatessafeguard", "target": "SecurityRule_Encryption", "confidence": 0.95}
            ],
            [
                {"source": "DeIdentifiedData", "relation": "transmitsPHI", "target": "AnalyticsVendor", "confidence": 0.95},
                {"source": "AnalyticsVendor", "relation": "subjectToException", "target": "DeIdentificationSafeHarbor", "confidence": 0.95}
            ],
            # Distractor 2-Hop
            [
                {"source": "CoveredEntity_A", "relation": "disclosesPHITo", "target": "Vendor_X", "confidence": 0.60},
                {"source": "Vendor_X", "relation": "satisfiesStandard", "target": "GenericNDA", "confidence": 0.60}
            ],

            # Q13-Q18 (3-Hop)
            [
                {"source": "ResearchProject_X", "relation": "usesData", "target": "DeIdentifiedPHI", "confidence": 0.90},
                {"source": "DeIdentifiedPHI", "relation": "governedBy", "target": "IRB_Waiver", "confidence": 0.95},
                {"source": "IRB_Waiver", "relation": "satisfiesStandard", "target": "MinimumNecessaryStandard", "confidence": 0.95}
            ],
            [
                {"source": "Subcontractor_C", "relation": "transmitsData", "target": "UnencryptedPHI", "confidence": 0.90},
                {"source": "UnencryptedPHI", "relation": "traversesNetwork", "target": "PublicWiFi", "confidence": 0.95},
                {"source": "PublicWiFi", "relation": "violatessafeguard", "target": "TechnicalSafeguardsRule", "confidence": 0.95}
            ],
            [
                {"source": "ITContractor_M", "relation": "accessesData", "target": "FullEHR_Record", "confidence": 0.90},
                {"source": "FullEHR_Record", "relation": "lacksAgreement", "target": "RoleBasedAccessControl", "confidence": 0.95},
                {"source": "RoleBasedAccessControl", "relation": "violatessafeguard", "target": "AccessControlStandard", "confidence": 0.95}
            ],
            [
                {"source": "PublicHealthAgency", "relation": "requestsData", "target": "LimitedDataSet", "confidence": 0.90},
                {"source": "LimitedDataSet", "relation": "governedBy", "target": "DataUseAgreement", "confidence": 0.95},
                {"source": "DataUseAgreement", "relation": "satisfiesStandard", "target": "PublicHealthCarveout", "confidence": 0.95}
            ],
            [
                {"source": "StolenBackupDrive", "relation": "containsData", "target": "UnencryptedDiagnosticPHI", "confidence": 0.90},
                {"source": "UnencryptedDiagnosticPHI", "relation": "traversesNetwork", "target": "PhysicalTheftIncident", "confidence": 0.95},
                {"source": "PhysicalTheftIncident", "relation": "violatessafeguard", "target": "BreachNotificationRule", "confidence": 0.95}
            ],
            [
                {"source": "AcademicPartner", "relation": "usesData", "target": "AnonymizedTelemetry", "confidence": 0.90},
                {"source": "AnonymizedTelemetry", "relation": "governedBy", "target": "DataTransferAgreement", "confidence": 0.95},
                {"source": "DataTransferAgreement", "relation": "satisfiesStandard", "target": "DeIdentificationRule", "confidence": 0.95}
            ],

            # Q19-Q24 (4-Hop)
            [
                {"source": "ForeignSubcontractor", "relation": "transmitsData", "target": "UnencryptedPHI_Backup", "confidence": 0.90},
                {"source": "UnencryptedPHI_Backup", "relation": "traversesNetwork", "target": "OverseasServer", "confidence": 0.90},
                {"source": "OverseasServer", "relation": "lacksAgreement", "target": "DownstreamBAA", "confidence": 0.95},
                {"source": "DownstreamBAA", "relation": "violatessafeguard", "target": "HIPAA_Security_Omnibus", "confidence": 0.95}
            ],
            [
                {"source": "MultiSiteTrial", "relation": "usesData", "target": "PseudonymizedGenomicPHI", "confidence": 0.90},
                {"source": "PseudonymizedGenomicPHI", "relation": "governedBy", "target": "IRB_MasterApproval", "confidence": 0.90},
                {"source": "IRB_MasterApproval", "relation": "satisfiesStandard", "target": "MasterBAA_Agreement", "confidence": 0.95},
                {"source": "MasterBAA_Agreement", "relation": "subjectToException", "target": "ResearchExemptionStandard", "confidence": 0.95}
            ],
            [
                {"source": "MobileApp_Vendor", "relation": "accessesData", "target": "PatientTelemetryAPI", "confidence": 0.90},
                {"source": "PatientTelemetryAPI", "relation": "traversesNetwork", "target": "CompromisedAPIKey", "confidence": 0.90},
                {"source": "CompromisedAPIKey", "relation": "lacksAgreement", "target": "OAuthScopePolicy", "confidence": 0.95},
                {"source": "OAuthScopePolicy", "relation": "violatessafeguard", "target": "TechnicalAccessControls", "confidence": 0.95}
            ],
            [
                {"source": "Regional_HIE", "relation": "transmitsPHI", "target": "EncryptedHealthRecord", "confidence": 0.90},
                {"source": "EncryptedHealthRecord", "relation": "governedBy", "target": "StatewideOptOutPolicy", "confidence": 0.90},
                {"source": "StatewideOptOutPolicy", "relation": "satisfiesStandard", "target": "HIE_ParticipationAgreement", "confidence": 0.95},
                {"source": "HIE_ParticipationAgreement", "relation": "subjectToException", "target": "TPO_ExchangeRule", "confidence": 0.95}
            ],
            [
                {"source": "HospitalSystem", "relation": "transmitsPHI", "target": "RawClinicalNotes", "confidence": 0.90},
                {"source": "RawClinicalNotes", "relation": "traversesNetwork", "target": "ExternalLLM_API", "confidence": 0.90},
                {"source": "ExternalLLM_API", "relation": "lacksAgreement", "target": "VendorBAA_Document", "confidence": 0.95},
                {"source": "VendorBAA_Document", "relation": "violatessafeguard", "target": "PrivacyRule_Disclosure", "confidence": 0.95}
            ],
            [
                {"source": "StateHealthDept", "relation": "transmitsData", "target": "EpidemiologicalRecords", "confidence": 0.90},
                {"source": "EpidemiologicalRecords", "relation": "governedBy", "target": "ExecutiveEmergencyOrder", "confidence": 0.90},
                {"source": "ExecutiveEmergencyOrder", "relation": "satisfiesStandard", "target": "CDC_Mandate", "confidence": 0.95},
                {"source": "CDC_Mandate", "relation": "subjectToException", "target": "PublicHealthEmergencyCarveout", "confidence": 0.95}
            ]
        ]

        # Add all edges to NetworkX DiGraph
        self.candidate_paths = candidate_paths
        for path in candidate_paths:
            for edge in path:
                u = edge["source"]
                v = edge["target"]
                self.graph.add_edge(u, v, **edge)

        # Build candidate passages for Vector-RAG / Naive-RAG
        self.passages = [
            {"id": "p01", "text": "Disclosure of PHI for patient treatment, payment, and operations (TPO) under 45 CFR 164.506 is exempt from individual authorization.", "determination": "COMPLIANT"},
            {"id": "p02", "text": "Psychotherapy notes are explicitly excluded from general TPO exceptions under 45 CFR 164.508 and require written authorization.", "determination": "NON-COMPLIANT"},
            {"id": "p03", "text": "Disclosure of PHI pursuant to a valid judicial subpoena satisfies 45 CFR 164.512 exceptions.", "determination": "COMPLIANT"},
            {"id": "p04", "text": "Covered entities may charge reasonable cost-based fee for patient record access under 45 CFR 164.524.", "determination": "COMPLIANT"},
            {"id": "p05", "text": "Law enforcement disclosure without court order or warrant violates Privacy Rule safeguards.", "determination": "NON-COMPLIANT"},
            {"id": "p06", "text": "Verbal disclosure of emergency status to family members is permitted under emergency carveout rules.", "determination": "COMPLIANT"},
            {"id": "p07", "text": "Disclosing PHI to a cloud vendor without an executed Business Associate Agreement violates 45 CFR 164.502(e).", "determination": "NON-COMPLIANT"},
            {"id": "p08", "text": "EMT providers transmitting PHI to receiving hospital emergency departments qualify as treatment activities.", "determination": "COMPLIANT"},
            {"id": "p09", "text": "Business associate sharing PHI with secondary host without downstream BAA violates §164.502(e).", "determination": "NON-COMPLIANT"},
            {"id": "p10", "text": "Hospital sharing billing data with collection agency under valid BAA satisfies statutory standards.", "determination": "COMPLIANT"},
            {"id": "p11", "text": "Transmitting unencrypted patient billing spreadsheets over open email violates Security Rule encryption rules.", "determination": "NON-COMPLIANT"},
            {"id": "p12", "text": "Disclosing de-identified patient data to analytics vendors qualifies under de-identification safe harbor exceptions.", "determination": "COMPLIANT"},
            {"id": "p13", "text": "Research projects accessing de-identified PHI under IRB waiver satisfy minimum necessary standards.", "determination": "COMPLIANT"},
            {"id": "p14", "text": "Subcontractors transmitting unencrypted PHI over public Wi-Fi breach Security Rule technical safeguards.", "determination": "NON-COMPLIANT"},
            {"id": "p15", "text": "Off-site contractors accessing full EHR without role-based access control breach access control standards.", "determination": "NON-COMPLIANT"},
            {"id": "p16", "text": "Sharing limited dataset records for public health under data use agreement satisfies public health carveouts.", "determination": "COMPLIANT"},
            {"id": "p17", "text": "Stolen unencrypted diagnostic backup drive constitutes a reportable breach under Breach Notification Rule.", "determination": "NON-COMPLIANT"},
            {"id": "p18", "text": "Sharing anonymized clinical telemetry with academic partners under data transfer agreement satisfies de-identification rules.", "determination": "COMPLIANT"},
            {"id": "p19", "text": "Foreign subcontractors storing unencrypted backups overseas without downstream BAA violate HIPAA Security Omnibus.", "determination": "NON-COMPLIANT"},
            {"id": "p20", "text": "Multi-site clinical trial sharing pseudonymized genomic data under IRB master approval and BAA is compliant.", "determination": "COMPLIANT"},
            {"id": "p21", "text": "Unauthorized mobile app accessing patient API via compromised API keys without OAuth scopes violates technical access controls.", "determination": "NON-COMPLIANT"},
            {"id": "p22", "text": "Regional HIE routing encrypted records under state-wide opt-out policy satisfies TPO exchange rules.", "determination": "COMPLIANT"},
            {"id": "p23", "text": "Exporting raw clinical notes to external LLM API without vendor BAA violates Privacy Rule disclosure rules.", "determination": "NON-COMPLIANT"},
            {"id": "p24", "text": "Transmitting de-identified epidemiological records to CDC under emergency executive order satisfies public health emergency carveouts.", "determination": "COMPLIANT"}
        ]
