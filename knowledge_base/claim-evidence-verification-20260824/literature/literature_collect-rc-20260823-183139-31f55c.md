---
created: '2026-08-23T18:40:24+00:00'
evidence:
- stage-04/candidates.jsonl
- stage-04/web_context.md
- stage-04/web_search_result.json
- stage-04/references.bib
- stage-04/search_meta.json
id: literature_collect-rc-20260823-183139-31f55c
run_id: rc-20260823-183139-31f55c
stage: 04-literature_collect
tags:
- literature_collect
- stage-04
- run-rc-20260
title: 'Stage 04: Literature Collect'
---

# Stage 04: Literature Collect

{"paper_id": "oalex-W3177828909", "title": "Highly accurate protein structure prediction with AlphaFold", "authors": [{"name": "John Jumper", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Richard Evans", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Alexander Pritzel", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Tim Green", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Michael Figurnov", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Olaf Ronneberger", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Kathryn Tunyasuvunakool", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Russ Bates", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Augustin Žídek", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Anna Potapenko", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Alex Bridgland", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Clemens Meyer", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Simon Köhl", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Andrew J. Ballard", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Andrew Cowie", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Bernardino Romera‐Paredes", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Stanislav Nikolov", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Rishub Jain", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Jonas Adler", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Trevor Back", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Stig Petersen", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "David Reiman", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Ellen Clancy", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Michał Zieliński", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Martin Steinegger", "affiliation": "Seoul National University"}, {"name": "Michalina Pacholska", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Tamas Berghammer", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Sebastian W. Bodenstein", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "David Silver", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Oriol Vinyals", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Andrew Senior", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Koray Kavukcuoglu", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Pushmeet Kohli", "affiliation": "Google DeepMind (United Kingdom)"}, {"name": "Demis Hassabis", "affiliation": "Google DeepMind (United Kingdom)"}], "year": 2021, "abstract": "Abstract Proteins are essential to life, and understanding their structure can facilitate a mechanistic understanding of their function. Through an enormous experimental effort 1–4 , the structures of around 100,000 unique proteins have been determined 5 , but this represents a small fraction of the billions of known protein sequences 6,7 . Structural coverage is bottlenecked by the months to years of painstaking effort required to determine a single protein structure. Accurate computational approaches are needed to address this gap and to enable large-scale structural bioinformatics. Predicting the three-dimensional structure that a protein will adopt based solely on its amino acid sequence—the structure prediction component of the ‘protein folding problem’ 8 —has been an important open research problem for more than 50 years 9 . Despite recent progress 10–14 , existing methods fall far short of atomic accuracy, especially when no homologous structure is available. Here we provide the first computational method that can regularly predict protein structures with atomic accuracy even in cases in which no similar structure is known. We validated an entirely redesigned version of our neural network-based model, AlphaFold, in the challenging 14th Critical Assessment of protein Structure Prediction (CASP14) 15 , demonstrating accuracy competitive with experimental structures in a majority of cases and greatly outperforming other methods. Underpinning the latest version of AlphaFold is a novel machine learning approach that incorporates physical and biological knowledge about protein structure, leveraging multi-sequence alignments, into the design of the deep learning algorithm.", "venue": "Nature", "citation_count": 46667, "doi": "10.1038/s41586-021-03819-2", "arxiv_id": "", "url": "https://doi.org/10.1038/s41586-021-03819-2", "source": "openalex", "cite_key": "jumper2021highly", "collected_at": "2026-08-23T18:39:04+00:00"}
{"paper_id": "oalex-W3082188176", "title": "2020 ESC Guidelines for the diagnosis and management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surger

... (truncated, see full artifact)


## Web Search Results
### [1] Artifact-centered Claim-aware Observability for Autonomous Scientific ...
URL: https://arxiv.org/html/2608.18312v1
We argue here that autonomous scientific agentic systems should make artifact lineage and claim-evidence bindings first-class observability records. Span trees and run logs should not be the only portable audit trail. The minimum trace for a scientific agent should include candidate artifacts, the operators that derive them, evaluator outputs attached to those artifacts, archive or selection ...

### [2] Artifact-centered Claim-aware Observability for Autonomous Scientific ...
URL: https://arxiv.org/abs/2608.18312
In this profile, scientific claims are ordinary individuals with explicit evidence bindings and verification records. The profile is intended as a semantic layer that complements current telemetry and provenance standards.

### [3] Science One Framework: A verifiable autonomous research framework via ...
URL: https://research.google/blog/science-one-framework-a-verifiable-autonomous-research-framework-via-chain-of-evidence/
The Science One Framework pipeline. Problem Investigator grounds literature via retrieved PDFs. Discovery module explores and evaluates solutions. Paper writing &amp; verification module writes and verifies the paper with a Claim Verifier ensuring all claims match their evidence source.

### [4] SciTrue: Evidence-Grounded Claim Verification in Science
URL: https://aclanthology.org/2026.eacl-demo.27/
We present SciTrue, a claim verification system providing source-level accountability and evidence traceability. SciTrue links each claim component to explicit, verifiable scientific sources, enabling users to inspect and challenge model inferences, addressing limitations of both general-purpose and search-augmented LLMs.

### [5] SciClaimEval | SciClaimEval: Cross-modal Claim Verification in ...
URL: https://sciclaimeval.github.io/
Scientific claim verification involves determining whether claims made in research papers are supported or refuted by accompanying evidence, such as experimental results, tables, and figures.

### [6] GitHub - AnkitaMuni/VerifyAI-Autonomous-Scientific-Intelligence ...
URL: https://github.com/AnkitaMuni/VerifyAI-Autonomous-Scientific-Intelligence-Platform
VerifyAI is an AI-powered multi-agent platform that audits research papers, repositories, reproducibility claims, and scientific transparency signals using autonomous reasoning agents and repository intelligence workflows. The system combines paper analysis, repository inspection, plausibility verification, reviewer simulation, and scientific trust scoring into a unified scientific auditing ...

### [7] Complex Claim Verification with Evidence Retrieved in the Wild
URL: https://aclanthology.org/2024.naacl-long.196/
Our pipeline includes five components: claim decomposition, raw document retrieval, fine-grained evidence retrieval, claim-focused summarization, and veracity judgment. We conduct experiments on complex political claims in the ClaimDecomp dataset and show that the aggregated evidence produced by our pipeline improves veracity judgments.

### [8] Scientific Claim Verification with Evidence from Text and Structured ...
URL: https://www.cs.cit.tum.de/en/sebis/research/natural-language-processing/scientific-claim-verification-with-evidence-from-text-and-structured-knowledge-verisci/
The holistic process of fact verification involves detecting check-worthy claims, finding relevant documents in a corpus of articles, extracting passages containing appropriate evidence, and finally making a decision on the veracity of the claim by inferring if there is logical entailment between the claim and found evidence.

### [9] RonitM2k06/Scientific_Claim_Verifier - GitHub
URL: https://github.com/RonitM2k06/Scientific_Claim_Verifier
A Scientific Intelligence Platform for evidence-based claim verification, research knowledge graphs, citation intelligence, and scientific literature exploration. - RonitM2k06/Scientific_Claim_Verifier

### [10] SciTrue: Science you can trust
URL: https://scitrue.ai/
Check any scientific claim against real published papers. See the evidence, how strong each study is, and where researchers still disagree.

### [11] GitHub - hflyzju/Awesome-AI-Scientist-Benchmarks
URL: https://github.com/hflyzju/Awesome-AI-Scientist-Benchmarks
📊 Benchmark Comparison Table ... 📚 Core AI-Scientist Benchmarks PaperBench — Evaluating AI&#x27;s ability to replicate AI research. PaperBench tasks agents with end-to-end replication of published ML work: understanding the paper, creating a codebase, running experiments, and matching reported results.

### [12] AstaBench: Benchmarking AI Agents for Science
URL: https://allenai.org/asta/bench
AstaBench is a benchmark suite &amp; leaderboards for evaluating agents on scientific tasks, powered by a more rigorous evaluation framework for AI agents. An evolving evaluation, AstaBench is a comprehensive suite of benchmarks com

... (truncated, see full artifact)


{
  "topic": "Claim-Evidence Verification for Autonomous AI Research",
  "web_results_count": 20,
  "scholar_papers_count": 0,
  "crawled_pages_count": 5,
  "pdf_extractions_count": 0,
  "has_search_answer": false,
  "elapsed_seconds": 80.16043899999931,
  "web_results": [
    {
      "title": "Artifact-centered Claim-aware Observability for Autonomous Scientific ...",
      "url": "https://arxiv.org/html/2608.18312v1",
      "snippet": "We argue here that autonomous scientific agentic systems should make artifact lineage and claim-evidence bindings first-class observability records. Span trees and run logs should not be the only portable audit trail. The minimum trace for a scientific agent should include candidate artifacts, the operators that derive them, evaluator outputs attached to those artifacts, archive or selection ...",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "Artifact-centered Claim-aware Observability for Autonomous Scientific ...",
      "url": "https://arxiv.org/abs/2608.18312",
      "snippet": "In this profile, scientific claims are ordinary individuals with explicit evidence bindings and verification records. The profile is intended as a semantic layer that complements current telemetry and provenance standards.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "Science One Framework: A verifiable autonomous research framework via ...",
      "url": "https://research.google/blog/science-one-framework-a-verifiable-autonomous-research-framework-via-chain-of-evidence/",
      "snippet": "The Science One Framework pipeline. Problem Investigator grounds literature via retrieved PDFs. Discovery module explores and evaluates solutions. Paper writing &amp; verification module writes and verifies the paper with a Claim Verifier ensuring all claims match their evidence source.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "SciTrue: Evidence-Grounded Claim Verification in Science",
      "url": "https://aclanthology.org/2026.eacl-demo.27/",
      "snippet": "We present SciTrue, a claim verification system providing source-level accountability and evidence traceability. SciTrue links each claim component to explicit, verifiable scientific sources, enabling users to inspect and challenge model inferences, addressing limitations of both general-purpose and search-augmented LLMs.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "SciClaimEval | SciClaimEval: Cross-modal Claim Verification in ...",
      "url": "https://sciclaimeval.github.io/",
      "snippet": "Scientific claim verification involves determining whether claims made in research papers are supported or refuted by accompanying evidence, such as experimental results, tables, and figures.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "GitHub - AnkitaMuni/VerifyAI-Autonomous-Scientific-Intelligence ...",
      "url": "https://github.com/AnkitaMuni/VerifyAI-Autonomous-Scientific-Intelligence-Platform",
      "snippet": "VerifyAI is an AI-powered multi-agent platform that audits research papers, repositories, reproducibility claims, and scientific transparency signals using autonomous reasoning agents and repository intelligence workflows. The system combines paper analysis, repository inspection, plausibility verification, reviewer simulation, and scientific trust scoring into a unified scientific auditing ...",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "Complex Claim Verification with Evidence Retrieved in the Wild",
      "url": "https://aclanthology.org/2024.naacl-long.196/",
      "snippet": "Our pipeline includes five components: claim decomposition, raw document retrieval, fine-grained evidence retrieval, claim-focused summarization, and veracity judgment. We conduct experiments on complex political claims in the ClaimDecomp dataset and show that the aggregated evidence produced by our pipeline improves veracity judgments.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "Scientific Claim Verification with Evidence from Text and Structured ...",
      "url": "https://www.cs.cit.tum.de/en/sebis/research/natural-language-processing/scientific-claim-verification-with-evidence-from-text-and-structured-knowledge-verisci/",
      "snippet": "The holistic process of fact verification involves detecting check-worthy claims, finding relevant documents in a corpus of articles, extracting passages containing appropriate evidence, and finally making a decision on the veracity of the claim by inferring if there is logical entailment between the claim and found evidence.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "RonitM2k06/Scien

... (truncated, see full artifact)


@article{jumper2021highly,
  title = {Highly accurate protein structure prediction with AlphaFold},
  author = {John Jumper and Richard Evans and Alexander Pritzel and Tim Green and Michael Figurnov and Olaf Ronneberger and Kathryn Tunyasuvunakool and Russ Bates and Augustin Žídek and Anna Potapenko and Alex Bridgland and Clemens Meyer and Simon Köhl and Andrew J. Ballard and Andrew Cowie and Bernardino Romera‐Paredes and Stanislav Nikolov and Rishub Jain and Jonas Adler and Trevor Back and Stig Petersen and David Reiman and Ellen Clancy and Michał Zieliński and Martin Steinegger and Michalina Pacholska and Tamas Berghammer and Sebastian W. Bodenstein and David Silver and Oriol Vinyals and Andrew Senior and Koray Kavukcuoglu and Pushmeet Kohli and Demis Hassabis},
  year = {2021},
  journal = {Nature},
  doi = {10.1038/s41586-021-03819-2},
  url = {https://doi.org/10.1038/s41586-021-03819-2},
}

@article{hindricks2020guidelines,
  title = {2020 ESC Guidelines for the diagnosis and management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS)},
  author = {Gerhard Hindricks and Tatjana Potpara and Nikolaos Dagres and Elena Arbelo and Jeroen J. Bax and Carina Blomström‐Lundqvist and Giuseppe Boriani and Manuel Castella and Gheorghe-Andrei Dan and Polychronis Dilaveris and Laurent Fauchier and Gerasimos Filippatos and Jonathan M Kalman and Mark La Meir and Deirdre A Lane and Jean‐Pierre Lebeau and Maddalena Lettino and Gregory Y.H. Lip and Fausto J Pinto and G. Neil Thomas and Marco Valgimigli and Isabelle C. Van Gelder and Bart P. van Putte and Caroline Watkins and ESC Scientific Document Group and Paulus Kirchhof and Michael Kühne and Victor Aboyans and Anders Ahlsson and Paweł Balsam and Johann Bauersachs and Stefano Benussi and Axel Brandes and Frieder Braunschweig and A John Camm and Davide Capodanno and Barbara Casadei and David Conen and Harry J.G.M. Crijns and Victoria Delgado and Dobromir Dobrev and Heinz Drexel and Lars Eckardt and Donna Fitzsimons and Thierry Folliguet and Chris P Gale and Bülent Görenek and Karl Georg Hæusler and Hein Heidbüchel and Bernard Iung and Hugo A Katus and Dipak Kotecha and Ulf Landmesser and Christophe Leclercq and Basil S. Lewis and Julia Mascherbauer and José Luís Merino and Béla Merkely and Lluı́s Mont and Christian Mueller and Klaudia V Nagy and Jonas Oldgren and Nikola Pavlović and Roberto F.E. Pedretti and Steffen E. Petersen and Jonathan P. Piccini and Bogdan A Popescu and Helmut Pürerfellner and Dimitrios J. Richter and Marco Roffi and Andrea Rubboli and Daniel Scherr and Renate B. Schnabel and Iain A. Simpson and Е. V. Shlyakhto and Moritz F. Sinner and Jan Steffel and Miguel Sousa-Uva and Piotr Suwalski and Martin Svetlošák and Rhian M Touyz and Nikolaos Dagres and Elena Arbelo and Jeroen J. Bax and Carina Blomström‐Lundqvist and Giuseppe Boriani and Manuel Castella and Gheorghe-Andrei Dan and Polychronis Dilaveris and Laurent Fauchier and Gerasimos Filippatos and Jonathan M Kalman and Mark La Meir and Deirdre A Lane and Jean‐Pierre Lebeau and Maddalena Lettino and Gregory Y.H. Lip and Fausto J Pinto and G. Neil Thomas and Marco Valgimigli},
  year = {2020},
  journal = {European Heart Journal},
  doi = {10.1093/eurheartj/ehaa612},
  url = {https://doi.org/10.1093/eurheartj/ehaa612},
}

@article{chicco2020advantages,
  title = {The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation},
  author = {Davide Chicco and Giuseppe Jurman},
  year = {2020},
  journal = {BMC Genomics},
  doi = {10.1186/s12864-019-6413-7},
  url = {https://doi.org/10.1186/s12864-019-6413-7},
}

@article{kairouz2020advances,
  title = {Advances and Open Problems in Federated Learning},
  author = {Peter Kairouz and H. Brendan McMahan and Brendan Avent and Aurélien Bellet and Mehdi Bennis and Arjun Nitin Bhagoji and Kallista Bonawitz and Zachary Charles and Graham Cormode and Rachel Cummings and Rafael G. L. D’Oliveira and Hubert Eichner and Salim El Rouayheb and David Evans and Joshua Gardner and Zachary Garrett and Adrià Gascón and Badih Ghazi and Phillip B. Gibbons and Marco Gruteser and Zaïd Harchaoui and Chaoyang He and Lingxiao He and Zhouyuan Huo and Ben Hutchinson and Justin Hsu and Martin Jaggi and Tara Javidi and Gauri Joshi and Mikhail Khodak and Jakub Konečný and Aleksandra Korolova and Farinaz Koushanfar and Sanmi Koyejo and Tancrède Lepoint and Yang Liu and Prateek Mittal and Mehryar Mohri and Richard Nock and Ayfer Özgür and Rasmus Pagh and Hang Qi and Daniel Ramage and Ramesh Raskar and Mariana Raykova and Dawn Song and Weikang Song and Sebastian U. Stich and Ziteng Sun and Ananda Theertha Suresh and Florian Tramèr and Praneeth Vepakomma and Jianyu Wang and Li Xiong and Zheng Xu and Qiang Yang and Felix X. Yu and Han Yu and Sen Zhao},
  year = {2020},
  journal = {Foundations and Trends® in Machine Learning},
  doi = {10.1561/2200000083},
  url

... (truncated, see full artifact)


{
  "real_search": true,
  "queries_used": [
    "autonomous scientific claim evidence verification",
    "AI scientist research validation benchmark",
    "research agent artifact verification",
    "automated research bundle evaluation",
    "evidence graph claim verification",
    "adversarial falsification scientific claims",
    "retrieval grounded scientific fact checking",
    "verifier critic scientific reasoning",
    "scientific claim verification benchmarks",
    "research agent evaluation datasets",
    "experiment validity benchmark artifacts",
    "scientific fact checking datasets",
    "claim evidence entailment theory",
    "Bayesian scientific evidence calibration",
    "causal interventions benchmark validity",
    "selective prediction verification risk",
    "automated peer review verification",
    "machine learning reproducibility assessment",
    "literature based novelty checking",
    "scientific artifact consistency checking",
    "scientific support annotation agreement",
    "partial support claim annotation",
    "evidence sufficiency labeling guidelines",
    "unverifiable scientific claim taxonomy",
    "benchmark shortcut detection scientific",
    "mutation template leakage detection",
    "held out intervention families",
    "counterfactual benchmark artifact verification",
    "risk sensitive false support metric",
    "paired intervention consistency evaluation",
    "evidence localization scoring benchmark",
    "paired bootstrap confidence intervals",
    "LLM judge scientific reliability",
    "structured checklist verifier baseline",
    "research verifier calibration fairness",
    "artifact aware claim verifier"
  ],
  "year_min": 2020,
  "total_candidates": 436,
  "bibtex_entries": 436,
  "ts": "2026-08-23T18:40:24+00:00"
}