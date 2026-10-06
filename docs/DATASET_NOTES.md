# Dataset notes

The data is an authored educational reference set, not a scrape of job vacancies or a representative labour-market survey. The five role examples in the supplied specification form the core. Eight related technical roles extend the comparison. Requirements were reviewed for internal consistency, canonical skill references and reasonable role relevance. They have not been validated by employers or an independent domain panel.

`skill_dictionary.csv` contains 110 canonical skills across 17 categories. Each row includes aliases, prerequisites, a study topic, an application exercise, an official resource link and a learning stage. Resource links are starting points; documentation sites can reorganize their pages. No external resources are fetched by the analyzer.

`job_roles.csv` contains 13 roles, descriptions, ordered core and preferred skills, categories and a capstone suggestion. These are broad profiles. For example, Data Analyst includes Power BI because the supplied specification does; an actual analyst vacancy may prefer Tableau or a different stack. Use Custom job to compare a specific description.

No trained hiring-outcome model, Kaggle resume corpus, real candidate data or paid API is used. No dataset licence is implied for external websites. The authored CSVs and synthetic fixtures are distributed with this project for educational modification and demonstration.

To add a skill, use a unique canonical name, narrow aliases and existing prerequisites. Avoid ambiguous single-letter aliases. To add a role, use only canonical skill names, keep core and preferred sets disjoint, and include a realistic project. Restart after edits because only public datasets and the vectorizer are cached. Run the test suite and evaluation after any edit: IDF values and rankings may change when role data changes.
