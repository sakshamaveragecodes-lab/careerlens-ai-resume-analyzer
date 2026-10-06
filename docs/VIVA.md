# Viva preparation

**1. What problem does the project solve?**
It helps a student see which technical skills are communicated by a resume, how they overlap with a role profile, and what to learn or document next. It is a guidance system, not an automated recruiter.

**2. What are the seven modules?**
Resume upload, extraction and cleaning, skill extraction, job-role data, matching and recommendation, skill-gap analysis, and the Streamlit dashboard.

**3. How is text extracted?**
`pypdf.PdfReader` reads each PDF page. `python-docx` reads paragraphs and table cells in a DOCX. Bytes are parsed in memory. Scanned PDFs contain images and need OCR before this app can use them.

**4. Why is text cleaning necessary?**
Documents contain inconsistent whitespace, line breaks and decorative separators. Cleaning makes comparisons more reliable. We preserve punctuation in C++, C#, .NET, Node.js and CI/CD so the meaning is not destroyed.

**5. How are skills detected?**
We match a controlled dictionary of 110 canonical skills and aliases with token boundaries. For example, Postgres maps to PostgreSQL. Java does not match JavaScript. Results are deduplicated and grouped by category.

**6. What is TF-IDF?**
Term frequency describes how often a term occurs in a document. Inverse document frequency gives more weight to terms appearing in fewer corpus documents. This project uses binary term presence so repeating a keyword does not earn more points. The corpus is the 13 curated role profiles.

**7. What does cosine similarity measure?**
It measures how aligned two vectors are: their dot product divided by the product of their lengths. With nonnegative TF-IDF vectors, the result is between zero and one. Zero vectors are handled as zero similarity.

**8. How is the score calculated?**
It is 75 times core skill coverage, plus 15 times preferred coverage, plus 10 times TF-IDF cosine similarity. All three inputs are fractions. A target without preferred skills uses 90 times core coverage plus 10 times similarity. The result is rounded to one decimal.

**9. Why does adding a relevant skill not reduce a score?**
The resume vector is projected onto the target's skills and uses the same fixed weights as the role vector. Similarity then increases as more of the target's weighted skill set is covered. Coverage also cannot decrease. Tests add skills in different orders for every role.

**10. Does the score understand the whole resume semantically?**
No. It measures controlled, lexical skill alignment. Full-text embeddings are not implemented. Education and project sections are displayed for context and feedback, but the numerical score uses skill presence only.

**11. Why can keywords miss relevant skills?**
A person may use a synonym absent from the dictionary, describe an action without naming the technology, or use an unusual document layout. A missing keyword is not proof of missing ability.

**12. How are weak skills identified?**
We do not infer weak ability. We label a term as a contextual mention when it appears in Projects, Experience or Internships, otherwise as mention only. This indicates the amount of resume context, not a verified competence level.

**13. How does the roadmap work?**
It starts from missing core requirements, adds any missing prerequisite topics, orders them before dependent topics, skips already-detected skills and ends with a role-specific applied project. Preferred requirements can be added with a toggle.

**14. What are Sentence Transformers?**
They are models that create vector representations of sentences or passages, often used for semantic similarity and retrieval. They could help with paraphrases, but require model downloads and careful evaluation. They are future scope here, not an implemented dependency.

**15. Why exclude protected attributes?**
They are not evidence of job-related skill and can create discriminatory outcomes. The scoring vocabulary contains technical skills only, recognized personal fields are filtered, and counterfactual tests check that changing protected fields leaves results unchanged. Those tests do not establish population-wide fairness.

**16. How is privacy handled?**
The app keeps uploads and results in session memory, has no account database and makes no external AI calls. Only public datasets are cached. Clear session removes the app's references and resets the upload controls. Downloaded PDFs belong to the user's device.

**17. How is the custom job description analyzed?**
Its technical skill terms are extracted with the same dictionary. Required/Preferred headings determine the two sets, which the interface displays for review. The same scoring engine compares them with the resume. Location, pay and eligibility requirements are not scored.

**18. Is this a supervised machine-learning classifier?**
No. There is no labelled hiring-outcome dataset and no trained acceptance model. It is an NLP information-extraction and vector-similarity application with deterministic rules. Using scikit-learn does not by itself make it a supervised model.

**19. What did evaluation show?**
Read `reports/evaluation_summary.json` and `docs/VERIFICATION.md` for the executed results. The sample evaluation covers three manually labelled fictional profiles, each exported to PDF and DOCX. Explain the limited sample size and avoid claiming real-world accuracy from it.

**20. What are the main limitations and improvements?**
No OCR, limited headings and aliases, broad role templates, no proficiency validation and no real-world benchmark. Improvements would begin with consented labelled evaluation, better error analysis, reviewed aliases, isolated OCR, multilingual support and measured semantic matching.

**21. Why Streamlit instead of a separate frontend and API?**
It supports a complete Python workflow with uploads, charts and state without an extra server layer. That reduces setup work for a college project. A separate API could be added if multiple clients or larger workloads justified it.

**22. Why no database?**
The core task does not require persistent candidate records. Keeping analysis in memory simplifies privacy and deployment. Saved reports/accounts were optional and are intentionally not part of this implementation.

**23. How would you describe an example result?**
Say: 'The selected role's core skill terms are X of Y, giving this much coverage. These terms were not detected. This study sequence addresses the gaps.' Do not say: 'The candidate has this probability of being hired.'
