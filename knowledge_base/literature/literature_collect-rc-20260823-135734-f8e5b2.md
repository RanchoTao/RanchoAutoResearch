---
created: '2026-08-23T14:00:18+00:00'
evidence:
- stage-04/candidates.jsonl
- stage-04/web_search_result.json
- stage-04/references.bib
- stage-04/search_meta.json
id: literature_collect-rc-20260823-135734-f8e5b2
run_id: rc-20260823-135734-f8e5b2
stage: 04-literature_collect
tags:
- literature_collect
- stage-04
- run-rc-20260
title: 'Stage 04: Literature Collect'
---

# Stage 04: Literature Collect

{"paper_id": "oalex-W2112796928", "title": "Gradient-based learning applied to document recognition", "authors": [{"name": "Yann LeCun", "affiliation": "AT&T (United States)"}, {"name": "Léon Bottou", "affiliation": "AT&T (United States)"}, {"name": "Yoshua Bengio", "affiliation": "Université de Montréal"}, {"name": "Patrick Haffner", "affiliation": "AT&T (United States)"}], "year": 1998, "abstract": "Multilayer neural networks trained with the back-propagation algorithm constitute the best example of a successful gradient based learning technique. Given an appropriate network architecture, gradient-based learning algorithms can be used to synthesize a complex decision surface that can classify high-dimensional patterns, such as handwritten characters, with minimal preprocessing. This paper reviews various methods applied to handwritten character recognition and compares them on a standard handwritten digit recognition task. Convolutional neural networks, which are specifically designed to deal with the variability of 2D shapes, are shown to outperform all other techniques. Real-life document recognition systems are composed of multiple modules including field extraction, segmentation recognition, and language modeling. A new learning paradigm, called graph transformer networks (GTN), allows such multimodule systems to be trained globally using gradient-based methods so as to minimize an overall performance measure. Two systems for online handwriting recognition are described. Experiments demonstrate the advantage of global training, and the flexibility of graph transformer networks. A graph transformer network for reading a bank cheque is also described. It uses convolutional neural network character recognizers combined with global training techniques to provide record accuracy on business and personal cheques. It is deployed commercially and reads several million cheques per day.", "venue": "Proceedings of the IEEE", "citation_count": 59321, "doi": "10.1109/5.726791", "arxiv_id": "", "url": "https://doi.org/10.1109/5.726791", "source": "openalex", "cite_key": "lecun1998gradientbased", "collected_at": "2026-08-23T13:59:50+00:00"}
{"paper_id": "oalex-W2105846236", "title": "A new criterion for assessing discriminant validity in variance-based structural equation modeling", "authors": [{"name": "Jörg Henseler", "affiliation": "Universidade Nova de Lisboa"}, {"name": "Christian M. Ringle", "affiliation": "Universität Hamburg"}, {"name": "Marko Sarstedt", "affiliation": "University of Newcastle Australia"}], "year": 2014, "abstract": "Discriminant validity assessment has become a generally accepted prerequisite for analyzing relationships between latent variables. For variance-based structural equation modeling, such as partial least squares, the Fornell-Larcker criterion and the examination of cross-loadings are the dominant approaches for evaluating discriminant validity. By means of a simulation study, we show that these approaches do not reliably detect the lack of discriminant validity in common research situations. We therefore propose an alternative approach, based on the multitrait-multimethod matrix, to assess discriminant validity: the heterotrait-monotrait ratio of correlations. We demonstrate its superior performance by means of a Monte Carlo simulation study, in which we compare the new approach to the Fornell-Larcker criterion and the assessment of (partial) cross-loadings. Finally, we provide guidelines on how to handle discriminant validity issues in variance-based structural equation modeling.", "venue": "Journal of the Academy of Marketing Science", "citation_count": 35718, "doi": "10.1007/s11747-014-0403-8", "arxiv_id": "", "url": "https://doi.org/10.1007/s11747-014-0403-8", "source": "openalex", "cite_key": "henseler2014criterion", "collected_at": "2026-08-23T13:59:50+00:00"}
{"paper_id": "oalex-W2120145199", "title": "QUANTUM ESPRESSO: a modular and open-source software project for quantum simulations of materials", "authors": [{"name": "Paolo Giannozzi", "affiliation": "University of Udine"}, {"name": "Stefano Baroni", "affiliation": "Scuola Internazionale Superiore di Studi Avanzati"}, {"name": "Nicola Bonini", "affiliation": "Massachusetts Institute of Technology"}, {"name": "Matteo Calandra", "affiliation": "Centre National de la Recherche Scientifique"}, {"name": "Roberto Car", "affiliation": "Princeton University"}, {"name": "Carlo Cavazzoni", "affiliation": "Cineca"}, {"name": "Davide Ceresoli", "affiliation": "Massachusetts Institute of Technology"}, {"name": "G. Chiarotti", "affiliation": "Superconducting and other Innovative Materials and Devices Institute"}, {"name": "Matteo Cococcioni", "affiliation": "University of Minnesota"}, {"name": "Ismaïla Dabo", "affiliation": "Institut national de recherche en sciences et technologies du numérique"}, {"name": "Andrea Dal Corso", "affiliation": "Scuola Internazionale Superiore di Studi Avanzati"}, {"name": "Stefano de Gironcoli", "affi

... (truncated, see full artifact)


{
  "topic": "World Models under Structured Partial Observability: identify a narrow failure mode and a simple latent-dynamics mechanism worth testing",
  "web_results_count": 0,
  "scholar_papers_count": 0,
  "crawled_pages_count": 0,
  "pdf_extractions_count": 0,
  "has_search_answer": false,
  "elapsed_seconds": 27.8651494999649,
  "web_results": [],
  "scholar_papers": []
}

@inproceedings{lecun1998gradientbased,
  title = {Gradient-based learning applied to document recognition},
  author = {Yann LeCun and Léon Bottou and Yoshua Bengio and Patrick Haffner},
  year = {1998},
  booktitle = {Proceedings of the IEEE},
  doi = {10.1109/5.726791},
  url = {https://doi.org/10.1109/5.726791},
}

@article{henseler2014criterion,
  title = {A new criterion for assessing discriminant validity in variance-based structural equation modeling},
  author = {Jörg Henseler and Christian M. Ringle and Marko Sarstedt},
  year = {2014},
  journal = {Journal of the Academy of Marketing Science},
  doi = {10.1007/s11747-014-0403-8},
  url = {https://doi.org/10.1007/s11747-014-0403-8},
}

@article{giannozzi2009quantum,
  title = {QUANTUM ESPRESSO: a modular and open-source software project for quantum simulations of materials},
  author = {Paolo Giannozzi and Stefano Baroni and Nicola Bonini and Matteo Calandra and Roberto Car and Carlo Cavazzoni and Davide Ceresoli and G. Chiarotti and Matteo Cococcioni and Ismaïla Dabo and Andrea Dal Corso and Stefano de Gironcoli and Stefano Fabris and Guido Fratesi and Ralph Gebauer and U. Gerstmann and Christos Gougoussis and Anton Kokalj and Michele Lazzeri and Layla Martin‐Samos and Nicola Marzari and Francesco Mauri and Riccardo Mazzarello and Stefano Paolini and Alfredo Pasquarello and Lorenzo Paulatto and Carlo Sbraccia and Sandro Scandolo and Gabriele Sclauzero and Ari P. Seitsonen and Alexander Smogunov and Paolo Umari and Renata M. Wentzcovitch},
  year = {2009},
  journal = {Journal of Physics Condensed Matter},
  doi = {10.1088/0953-8984/21/39/395502},
  url = {https://doi.org/10.1088/0953-8984/21/39/395502},
}

@article{eck2009software,
  title = {Software survey: VOSviewer, a computer program for bibliometric mapping},
  author = {Nees Jan van Eck and Ludo Waltman},
  year = {2009},
  journal = {Scientometrics},
  doi = {10.1007/s11192-009-0146-3},
  url = {https://doi.org/10.1007/s11192-009-0146-3},
}

@article{everingham2009pascal,
  title = {The Pascal Visual Object Classes (VOC) Challenge},
  author = {Mark Everingham and Luc Van Gool and Christopher K. I. Williams and John Winn and Andrew Zisserman},
  year = {2009},
  journal = {International Journal of Computer Vision},
  doi = {10.1007/s11263-009-0275-4},
  url = {https://doi.org/10.1007/s11263-009-0275-4},
}

@article{shleifer1997survey,
  title = {A Survey of Corporate Governance},
  author = {Andrei Shleifer and Robert W. Vishny},
  year = {1997},
  journal = {The Journal of Finance},
  doi = {10.1111/j.1540-6261.1997.tb04820.x},
  url = {https://doi.org/10.1111/j.1540-6261.1997.tb04820.x},
}

@article{abramson2024accurate,
  title = {Accurate structure prediction of biomolecular interactions with AlphaFold 3},
  author = {Josh Abramson and Jonas Adler and Jack Dunger and Richard Evans and Tim Green and Alexander Pritzel and Olaf Ronneberger and Lindsay Willmore and Andrew J. Ballard and Joshua Bambrick and Sebastian W. Bodenstein and David A. Evans and Chia-Chun Hung and Michael O’Neill and David Reiman and Kathryn Tunyasuvunakool and Zachary Wu and Akvilė Žemgulytė and Eirini Arvaniti and Charles Beattie and Ottavia Bertolli and Alex Bridgland and Alexey V. Cherepanov and Miles Congreve and Alexander I. Cowen-Rivers and Andrew Cowie and Michael Figurnov and Fabian B. Fuchs and Hannah Gladman and Rishub Jain and Yousuf A. Khan and Caroline M. R. Low and Kuba Perlin and Anna Potapenko and Pascal Savy and Sukhdeep Singh and Adrian Stecuła and Ashok Thillaisundaram and Catherine Tong and Sergei Yakneen and Ellen D. Zhong and Michał Zieliński and Augustin Žídek and Victor Bapst and Pushmeet Kohli and Max Jaderberg and Demis Hassabis and John Jumper},
  year = {2024},
  journal = {Nature},
  doi = {10.1038/s41586-024-07487-w},
  url = {https://doi.org/10.1038/s41586-024-07487-w},
}

@article{litjens2017survey,
  title = {A survey on deep learning in medical image analysis},
  author = {Geert Litjens and Thijs Kooi and Babak Ehteshami Bejnordi and Arnaud A. A. Setio and Francesco Ciompi and Mohsen Ghafoorian and Jeroen van der Laak and Bram van Ginneken and Clara I. Sá‎nchez},
  year = {2017},
  journal = {Medical Image Analysis},
  doi = {10.1016/j.media.2017.07.005},
  url = {https://doi.org/10.1016/j.media.2017.07.005},
}

@article{shorten2019survey,
  title = {A survey on Image Data Augmentation for Deep Learning},
  author = {Connor Shorten and Taghi M. Khoshgoftaar},
  year = {2019},
  journal = {Journal Of Big Data},
  doi = {10.1186/s40537-019-0197-0},
  url = {https://doi.org/10.1186/s40537-019-0197-0},
}

@article{eyring2016overview,
  title = {Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6) experimental design and organization},
  author = {Veronika Eyring and Sandrine Bony and Gerald A. Meehl and C. A. Senior and Björn Stevens and Ronald J. Stouffer and Karl E. Taylor},
  year = {2016},
  journal = {Geoscientific model development},
  doi = {10.5194/gmd-9-1937-2

... (truncated, see full artifact)


{
  "real_search": true,
  "queries_used": [
    "learned world models under partial observability",
    "model-based reinforcement learning partial observability belief state",
    "latent dynamics models missing observations sensor dropout",
    "recurrent state space models occlusion and observation masking",
    "predictive state representations for partially observable control",
    "Dreamer world models partial observability",
    "robust world models observation corruption distribution shift",
    "state representation learning under intermittent observations",
    "latent dynamics identifiability partial observability",
    "visual world models occlusion memory"
  ],
  "year_min": 1990,
  "total_candidates": 463,
  "bibtex_entries": 459,
  "ts": "2026-08-23T14:00:18+00:00"
}