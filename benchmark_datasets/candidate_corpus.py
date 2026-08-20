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
        """Constructs standalone candidate knowledge graph and raw passage corpus with extracted edges."""
        
        # Define candidate edge chains across 1-4 hop compliance paths (including targets & distractors)
        candidate_paths = [
            # Q1-Q6 (1-Hop)
            [{"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception", "confidence": 0.95}],
            [{"source": "PsychotherapyNotes", "relation": "excludedFrom", "target": "TPO_Exception", "confidence": 0.95}],
            [{"source": "PHI_Disclosure", "relation": "subjectToException", "target": "JudicialSubpoena_Exception", "confidence": 0.95}],
            [{"source": "PatientAccessFee", "relation": "satisfiesStandard", "target": "CostBasedFeeRule", "confidence": 0.95}],
            [{"source": "LawEnforcementDisclosure", "relation": "violatessafeguard", "target": "PrivacyRule_LawEnforcement", "confidence": 0.95}],
            [{"source": "EmergencyFamilyDisclosure", "relation": "subjectToException", "target": "EmergencyCarveout", "confidence": 0.95}],
            # Distractors 1-Hop
            [{"source": "PHI_Disclosure", "relation": "requiresAuthorization", "target": "GeneralPatientConsent", "confidence": 0.50}],
            [{"source": "PsychotherapyNotes", "relation": "subjectToException", "target": "GeneralMedicalRecordRule", "confidence": 0.40}],
            
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
            # Distractors 2-Hop
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

        # Build raw un-labeled regulatory passage corpus WITH extracted edge annotations for fair rule engine evaluation
        self.passages = [
            {
                "id": "p01",
                "text": "Under 45 CFR 164.506, covered entities are permitted to use or disclose protected health information for treatment, payment, or health care operations without individual authorization.",
                "edges": [{"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception"}]
            },
            {
                "id": "p02",
                "text": "45 CFR 164.508 mandates that covered entities must obtain an authorization for any use or disclosure of psychotherapy notes, except to carry out treatment or defense in legal proceedings.",
                "edges": [{"source": "PsychotherapyNotes", "relation": "excludedFrom", "target": "TPO_Exception"}]
            },
            {
                "id": "p03",
                "text": "Section 164.512(e) permits covered entities to disclose protected health information in response to an order of a court or administrative tribunal, or valid judicial subpoena.",
                "edges": [{"source": "PHI_Disclosure", "relation": "subjectToException", "target": "JudicialSubpoena_Exception"}]
            },
            {
                "id": "p04",
                "text": "Under 45 CFR 164.524, a covered entity may charge a reasonable, cost-based fee for providing individuals with copies of their medical records.",
                "edges": [{"source": "PatientAccessFee", "relation": "satisfiesStandard", "target": "CostBasedFeeRule"}]
            },
            {
                "id": "p05",
                "text": "Disclosures of PHI to law enforcement officials require a court order, grand jury subpoena, or statutory mandate under 45 CFR 164.512(f).",
                "edges": [{"source": "LawEnforcementDisclosure", "relation": "violatessafeguard", "target": "PrivacyRule_LawEnforcement"}]
            },
            {
                "id": "p06",
                "text": "In emergency circumstances, healthcare providers may disclose PHI relevant to family members or caregivers involved in care under professional judgment rules.",
                "edges": [{"source": "EmergencyFamilyDisclosure", "relation": "subjectToException", "target": "EmergencyCarveout"}]
            },
            {
                "id": "p07",
                "text": "A covered entity may not disclose protected health information to a business associate or cloud service provider without obtaining satisfactory assurances through a written Business Associate Agreement pursuant to 45 CFR 164.502(e) and 164.504(e).",
                "edges": [
                    {"source": "CoveredEntity_A", "relation": "disclosesPHITo", "target": "CloudVendor_B"},
                    {"source": "CloudVendor_B", "relation": "lacksAgreement", "target": "BAA_Document"}
                ]
            },
            {
                "id": "p08",
                "text": "Emergency medical service personnel transmitting patient care reports to receiving hospital staff qualify under treatment activities under HIPAA privacy provisions.",
                "edges": [
                    {"source": "EMT_Provider", "relation": "transmitsPHI", "target": "Hospital_ED"},
                    {"source": "Hospital_ED", "relation": "qualifiesAs", "target": "TreatmentActivity"}
                ]
            },
            {
                "id": "p09",
                "text": "Subcontractor vendors handling protected health information on behalf of a business associate must enter into downstream business associate contracts meeting §164.504(e) standards.",
                "edges": [
                    {"source": "BusinessAssociate_1", "relation": "disclosesPHITo", "target": "SubcontractorHost_2"},
                    {"source": "SubcontractorHost_2", "relation": "lacksAgreement", "target": "SubcontractorBAA"}
                ]
            },
            {
                "id": "p10",
                "text": "Covered hospitals sharing patient billing details with contracted debt collection agencies operating under executed business associate agreements satisfy Privacy Rule requirements.",
                "edges": [
                    {"source": "Hospital_A", "relation": "disclosesPHITo", "target": "CollectionAgency_B"},
                    {"source": "CollectionAgency_B", "relation": "satisfiesStandard", "target": "BAA_Agreement"}
                ]
            },
            {
                "id": "p11",
                "text": "The Security Rule 45 CFR 164.312(e) mandates implementation of technical security measures to guard against unauthorized access to electronic PHI that is being transmitted over an electronic communications network.",
                "edges": [
                    {"source": "BillingDepartment", "relation": "transmitsData", "target": "UnencryptedEmail"},
                    {"source": "UnencryptedEmail", "relation": "violatessafeguard", "target": "SecurityRule_Encryption"}
                ]
            },
            {
                "id": "p12",
                "text": "Health information that meets the de-identification standards of 45 CFR 164.514(a)-(b) is no longer considered protected health information and falls outside HIPAA Privacy Rule restrictions.",
                "edges": [
                    {"source": "DeIdentifiedData", "relation": "transmitsPHI", "target": "AnalyticsVendor"},
                    {"source": "AnalyticsVendor", "relation": "subjectToException", "target": "DeIdentificationSafeHarbor"}
                ]
            },
            {
                "id": "p13",
                "text": "Research use of protected health information is permissible under 45 CFR 164.512(i) if an Institutional Review Board (IRB) or Privacy Board grants a waiver of authorization.",
                "edges": [
                    {"source": "ResearchProject_X", "relation": "usesData", "target": "DeIdentifiedPHI"},
                    {"source": "DeIdentifiedPHI", "relation": "governedBy", "target": "IRB_Waiver"},
                    {"source": "IRB_Waiver", "relation": "satisfiesStandard", "target": "MinimumNecessaryStandard"}
                ]
            },
            {
                "id": "p14",
                "text": "Transmitting unencrypted electronic PHI over public Wi-Fi networks fails to meet technical transmission security standards specified in 45 CFR 164.312(e).",
                "edges": [
                    {"source": "Subcontractor_C", "relation": "transmitsData", "target": "UnencryptedPHI"},
                    {"source": "UnencryptedPHI", "relation": "traversesNetwork", "target": "PublicWiFi"},
                    {"source": "PublicWiFi", "relation": "violatessafeguard", "target": "TechnicalSafeguardsRule"}
                ]
            },
            {
                "id": "p15",
                "text": "Role-based access control procedures required by 45 CFR 164.312(a)(1) dictate that workforce members and contractors be granted access only to the minimum necessary electronic PHI required for their assigned duties.",
                "edges": [
                    {"source": "ITContractor_M", "relation": "accessesData", "target": "FullEHR_Record"},
                    {"source": "FullEHR_Record", "relation": "lacksAgreement", "target": "RoleBasedAccessControl"},
                    {"source": "RoleBasedAccessControl", "relation": "violatessafeguard", "target": "AccessControlStandard"}
                ]
            },
            {
                "id": "p16",
                "text": "A covered entity may disclose a limited data set for public health or research purposes if the disclosure is governed by a data use agreement satisfying 45 CFR 164.514(e).",
                "edges": [
                    {"source": "PublicHealthAgency", "relation": "requestsData", "target": "LimitedDataSet"},
                    {"source": "LimitedDataSet", "relation": "governedBy", "target": "DataUseAgreement"},
                    {"source": "DataUseAgreement", "relation": "satisfiesStandard", "target": "PublicHealthCarveout"}
                ]
            },
            {
                "id": "p17",
                "text": "Under 45 CFR 164.402, the acquisition, access, use, or disclosure of unencrypted protected health information in a manner not permitted under subpart E is presumed to be a reportable breach.",
                "edges": [
                    {"source": "StolenBackupDrive", "relation": "containsData", "target": "UnencryptedDiagnosticPHI"},
                    {"source": "UnencryptedDiagnosticPHI", "relation": "traversesNetwork", "target": "PhysicalTheftIncident"},
                    {"source": "PhysicalTheftIncident", "relation": "violatessafeguard", "target": "BreachNotificationRule"}
                ]
            },
            {
                "id": "p18",
                "text": "Sharing fully anonymized or de-identified data streams under a data transfer agreement complies with statutory de-identification standards under 45 CFR 164.514.",
                "edges": [
                    {"source": "AcademicPartner", "relation": "usesData", "target": "AnonymizedTelemetry"},
                    {"source": "AnonymizedTelemetry", "relation": "governedBy", "target": "DataTransferAgreement"},
                    {"source": "DataTransferAgreement", "relation": "satisfiesStandard", "target": "DeIdentificationRule"}
                ]
            },
            {
                "id": "p19",
                "text": "Foreign subcontractors processing or storing electronic PHI backups overseas must adhere to the HIPAA Security Final Rule and Omnibus Standards including downstream agreement obligations.",
                "edges": [
                    {"source": "ForeignSubcontractor", "relation": "transmitsData", "target": "UnencryptedPHI_Backup"},
                    {"source": "UnencryptedPHI_Backup", "relation": "traversesNetwork", "target": "OverseasServer"},
                    {"source": "OverseasServer", "relation": "lacksAgreement", "target": "DownstreamBAA"},
                    {"source": "DownstreamBAA", "relation": "violatessafeguard", "target": "HIPAA_Security_Omnibus"}
                ]
            },
            {
                "id": "p20",
                "text": "Multi-center clinical research trials sharing pseudonymized genomic data operate compliantly when governed by master IRB approvals, data protection agreements, and executed BAAs.",
                "edges": [
                    {"source": "MultiSiteTrial", "relation": "usesData", "target": "PseudonymizedGenomicPHI"},
                    {"source": "PseudonymizedGenomicPHI", "relation": "governedBy", "target": "IRB_MasterApproval"},
                    {"source": "IRB_MasterApproval", "relation": "satisfiesStandard", "target": "MasterBAA_Agreement"},
                    {"source": "MasterBAA_Agreement", "relation": "subjectToException", "target": "ResearchExemptionStandard"}
                ]
            },
            {
                "id": "p21",
                "text": "API endpoints exposing electronic PHI without proper OAuth scope authorization or access control mechanisms breach technical access control standards under 45 CFR 164.312(a).",
                "edges": [
                    {"source": "MobileApp_Vendor", "relation": "accessesData", "target": "PatientTelemetryAPI"},
                    {"source": "PatientTelemetryAPI", "relation": "traversesNetwork", "target": "CompromisedAPIKey"},
                    {"source": "CompromisedAPIKey", "relation": "lacksAgreement", "target": "OAuthScopePolicy"},
                    {"source": "OAuthScopePolicy", "relation": "violatessafeguard", "target": "TechnicalAccessControls"}
                ]
            },
            {
                "id": "p22",
                "text": "Health information exchanges (HIEs) transmitting encrypted health records under state opt-out framework agreements satisfy treatment, payment, and operations exchange standards.",
                "edges": [
                    {"source": "Regional_HIE", "relation": "transmitsPHI", "target": "EncryptedHealthRecord"},
                    {"source": "EncryptedHealthRecord", "relation": "governedBy", "target": "StatewideOptOutPolicy"},
                    {"source": "StatewideOptOutPolicy", "relation": "satisfiesStandard", "target": "HIE_ParticipationAgreement"},
                    {"source": "HIE_ParticipationAgreement", "relation": "subjectToException", "target": "TPO_ExchangeRule"}
                ]
            },
            {
                "id": "p23",
                "text": "Transmission of unredacted clinical notes to external commercial artificial intelligence APIs without a signed business associate agreement constitutes an impermissible disclosure under 45 CFR 164.502.",
                "edges": [
                    {"source": "HospitalSystem", "relation": "transmitsPHI", "target": "RawClinicalNotes"},
                    {"source": "RawClinicalNotes", "relation": "traversesNetwork", "target": "ExternalLLM_API"},
                    {"source": "ExternalLLM_API", "relation": "lacksAgreement", "target": "VendorBAA_Document"},
                    {"source": "VendorBAA_Document", "relation": "violatessafeguard", "target": "PrivacyRule_Disclosure"}
                ]
            },
            {
                "id": "p24",
                "text": "Reporting epidemiological surveillance data to the Centers for Disease Control and Prevention (CDC) under executive emergency authority is authorized pursuant to public health exception 45 CFR 164.512(b).",
                "edges": [
                    {"source": "StateHealthDept", "relation": "transmitsData", "target": "EpidemiologicalRecords"},
                    {"source": "EpidemiologicalRecords", "relation": "governedBy", "target": "ExecutiveEmergencyOrder"},
                    {"source": "ExecutiveEmergencyOrder", "relation": "satisfiesStandard", "target": "CDC_Mandate"},
                    {"source": "CDC_Mandate", "relation": "subjectToException", "target": "PublicHealthEmergencyCarveout"}
                ]
            },
            # Distractor raw passages
            {
                "id": "d01",
                "text": "Administrative requirements under 45 CFR 164.530 mandate that covered entities designate a privacy official responsible for policy development.",
                "edges": [{"source": "PrivacyOfficial", "relation": "satisfiesStandard", "target": "AdministrativeSafeguard"}]
            },
            {
                "id": "d02",
                "text": "Physical safeguards under 45 CFR 164.310 specify facility access controls and workstation security requirements for covered entities.",
                "edges": [{"source": "FacilityAccess", "relation": "satisfiesStandard", "target": "PhysicalSafeguardsRule"}]
            }
        ]
