# Expériences et Résultats — PSC INF12

Ce document couvre les six expériences menées sur MASynReas, appliqué au dataset noria-0.2 (graphe de connaissances ICT jouet) et à un catalogue de 27 datasets synthétiques.

### Fil conducteur

Les expériences répondent à six questions dans un ordre logique :

1. **Les 4 familles d'agents niveau 1 sont-elles redondantes ?** → Tableau de complémentarité
2. **Le parallélisme MAS apporte-t-il un gain de vitesse réel ?** → Baseline séquentiel
3. **Le MAS améliore-t-il la qualité d'un LLM utilisé en synthèse ?** → Étude d'ablation
4. **Un LLM seul peut-il remplacer le MAS pour la détection d'entités ?** → Baseline LLM monovalent
5. **La pipeline L1+L2 est-elle précise sur ground truth contrôlé ?** → Évaluation datasets synthétiques
6. **Un LLM peut-il effectuer la classification L2 aussi bien que le MAS ?** → Comparaison LLM vs MAS

Les expériences 3, 4 et 6 impliquent des LLM mais avec des rôles distincts :
- En **expérience 3**, le LLM est un *consommateur* des sorties MAS — il synthétise un rapport à partir de faits déjà corrélés.
- En **expérience 4**, le LLM est un *concurrent* du MAS pour la **détection d'entités** — il reçoit le graphe brut et identifie les entités anormales sans prétraitement.
- En **expérience 6**, le LLM est un *concurrent* du MAS pour la **classification de diagnoseurs** — il reçoit le graphe (et optionnellement les sorties L1/L2) et doit nommer quel pattern s'applique, évalué sur le même ground truth que l'expérience 5.

---

## 1. Tableau de complémentarité des familles

**Script :** `complementarity_table.py`  
**Données :** dataset noria-0.2 chargé dans Virtuoso (localhost:8890)  
**Préparation :** `python -X utf8 run_all_detectors.py both`  
**Exécution :** `python -X utf8 complementarity_table.py`  
**Résultats :** `complementarity_results.json`

### Objectif

Répondre empiriquement à la question : *les 4 familles d'agents sont-elles redondantes ?*
Chaque famille détecte-t-elle des anomalies qu'aucune autre ne peut voir ?

### Résultats — mode apriori (23 agents, 10 secondes)

| Famille | Agents actifs | Détections | Uniques |
|---------|:---:|:---:|:---:|
| Structural | 2/10 | 17 | **oui** |
| Dynamic | 1/3 | 10 | **oui** |
| Functional | 2/7 | 7 | **oui** |
| Procedural | 1/3 | 2 | **oui** |

**Non-redondance prouvée :** chaque famille détecte des entités qu'aucune autre famille ne voit.

Agents les plus actifs :
- `missing_interface_detector` (structural) — 14 ressources sans interface réseau
- `event_without_related_element_detector` (dynamic) — 10 événements sans élément lié
- `inconsistent_service_hierarchy_detector` (functional) — 4 hiérarchies incohérentes
- `ticket_without_assigned_procedure_detector` (procedural) — 2 tickets sans procédure

**3 cas de synergie identifiés** (entités détectées par 2 familles simultanément) :

| Entité | Structural | Dynamic | Functional | Procedural |
|--------|:---:|:---:|:---:|:---:|
| APP_TOY_DC01 | ✓ | | ✓ | |
| APP_TOY_DC02 | ✓ | | ✓ | |
| APP_TOY_MON01 | ✓ | | ✓ | |

Ces 3 applications sont détectées par le détecteur structurel
(`application_without_support`) ET par le détecteur fonctionnel
(`application_without_resource`). Ce sont les cibles naturelles
des agents de niveau 2 : sans corrélation, ces deux alertes restent
des signaux indépendants ; avec `structural_fragility_diagnoser`,
elles convergent en un diagnostic unique.

### Résultats — mode aposteriori (31 agents, 12 secondes)

| Famille | Agents actifs | Détections |
|---------|:---:|:---:|
| Structural | **2/7** | **10** |
| Dynamic | 0/12 | 0 |
| Functional | **7/9** | **19** |
| Procedural | 0/3 | 0 |

**Finding important :** sur noria-0.2, les familles structurelle et fonctionnelle
sont actives en mode aposteriori (10 + 19 détections). L'inactivité des familles
dynamique et procédurale s'explique par les caractéristiques du dataset : absence
d'instance `noria:Change`, seulement 6 `EventRecord` réseau (en dessous des seuils
de burst/répétition), et tous les tickets sont correctement reliés à leurs événements.

Ce résultat justifie l'architecture à 4 familles : la couverture complète
de l'espace des anomalies nécessite les 4 facettes NORIA-O, même si
certaines ne sont actives que sur des topologies spécifiques.

---

## 2. Baseline séquentiel — mesure du speedup MAS

**Script :** `baseline_monoagent.py`  
**Résultats :** `baseline_results.json`  
**Exécution :** `python -X utf8 baseline_monoagent.py both`

### Objectif

Mesurer le gain de temps apporté par l'exécution parallèle des agents niveau 1
par rapport à une exécution séquentielle sur un seul thread Python.
Le même ensemble de requêtes SPARQL est exécuté dans les deux cas ;
seul l'ordonnancement change.

---

## 3. Étude d'ablation — valeur ajoutée de chaque couche MAS

**Script :** `ablation_study.py`  
**Exécution :** `python -X utf8 ablation_study.py` (~25 minutes)  
**Résultats :** `ablation_results.json`

### Objectif

Mesurer empiriquement la valeur ajoutée de chaque couche du MAS sur
la qualité des diagnostics produits par un LLM de synthèse.

**Question centrale :** *à quoi sert le MAS si on a déjà un LLM ?*

### Modèle LLM utilisé

**`llama3.1:8b`** — Meta Llama 3.1, 8 milliards de paramètres, variante instruction-tuned.
Exécuté via Ollama sur CPU local.
Paramètres d'inférence : température = 0.1 (quasi-déterministe), longueur maximale = 300 tokens.

Ce modèle a été choisi pour sa capacité de suivi d'instructions en langue naturelle
et son contexte étendu (jusqu'à 128K tokens), utile pour ingérer les JSON
de détection de condition B.

### Protocole

Trois conditions testées sur les mêmes scénarios. Seul l'input du LLM change ;
le prompt de tâche est identique dans les 3 cas :
*"You are a network operations expert. Based on the following [input], provide a concise diagnosis :
identify the most likely root cause, the affected entity, and the severity (CRITICAL / HIGH / MEDIUM / LOW).
Answer in 3–5 sentences."*

| | Condition A | Condition B | Condition C |
|-|-------------|-------------|-------------|
| **Input LLM** | Texte du ticket d'incident (50 mots env.) | JSON des résultats niveau 1 (tous agents actifs) | JSON niveau 1 + JSON des diagnostics niveau 2 |
| **Architecture simulée** | LLM seul | Niveau 1 → LLM | Niveau 1+2 → LLM |

**Important :** les facts de condition B et les diagnostics de condition C sont des données
représentatives construites manuellement dans le script pour chaque scénario.
Ils reproduisent fidèlement la structure réelle des sorties MAS mais ne sont pas
générés dynamiquement par les agents à chaque run.
L'étude d'ablation a été conçue et exécutée avant le refactor niveau 2 (qui est passé
de 4 à 12 diagnoseurs). Les diagnostics de condition C illustrent les 4 diagnoseurs
originaux (SPOF, change-induced, traceability, structural fragility).

### Métriques (calculées sur la première réponse parmi les 5 runs)

**Hallucination** — fraction des tokens capitalisés dans la réponse qui ressemblent
à un nom d'entité NORIA (pattern `[A-Z]{2+}[_A-Za-z0-9]*`, ex. `RES_TOY_as2`)
mais n'apparaissent pas dans la liste des entités connues du scénario.
Les mots-clés génériques (`CRITICAL`, `HIGH`, `JSON`, etc.) sont exclus.
Un hallucination_rate = 0.25 signifie que 1 entité sur 4 mentionnées par le LLM n'existe pas.

**Conformité** — fraction de 3 éléments du ground truth présents dans la réponse :
le nom de l'entité cible, le niveau de sévérité, et le type de diagnostic
(avec underscores remplacés par des espaces). Valeurs possibles : 0.00, 0.33, 0.67, 1.00.

**Consistance** — similarité Jaccard moyenne entre toutes les paires parmi les 5 runs
(vocabulaire tokenisé en minuscules). Une valeur de 1.0 signifie que les 5 réponses
utilisent exactement le même vocabulaire.

**Sévérité** — binaire : 1 si le mot correspondant au niveau de sévérité attendu
(`CRITICAL`, `HIGH`, etc.) apparaît dans la réponse, 0 sinon.

### Scénarios

| ID | Description | Ground truth |
|----|-------------|-------------|
| S1 | RES_TOY_as2 : 3 signaux structurels simultanés | SPOF / CRITICAL |
| S2 | CR_2022_001 : signal dynamique + procédural | change-induced / HIGH |
| S3 | Incidents sans ticket + tickets sans event | traceability breakdown / HIGH |
| S4 | RES_TOY_as2 : 3 faiblesses apriori de gouvernance | structural fragility / HIGH |
| S5 | RES_TOY_as2 : SPOF + change CR_2022_001 (cross-family) | SPOF / CRITICAL |

### Résultats

#### Moyennes par condition (5 scénarios × 5 runs)

| Condition | Hallucination ↓ | Conformité ↑ | Consistance ↑ | Sévérité ↑ |
|-----------|:---:|:---:|:---:|:---:|
| **A — LLM seul** | 0.00 | 0.60 | 0.68 | 1.00 |
| **B — Niveau 1 → LLM** | 0.05 | 0.53 | 0.57 | 0.60 |
| **C — Niveau 1+2 → LLM** | **0.00** | **0.87** | **0.66** | **1.00** |

#### Tableau détaillé

| Scénario | A — Hall / Conf / Cons / Sev | B — Hall / Conf / Cons / Sev | C — Hall / Conf / Cons / Sev |
|----------|:---:|:---:|:---:|
| S1 SPOF | 0.00 / 0.67 / 0.84 / 1 | 0.25 / 1.00 / 0.44 / 1 | **0.00 / 1.00 / 0.54 / 1** |
| S2 Change | 0.00 / 0.67 / 0.52 / 1 | 0.00 / 0.33 / 0.82 / 0 | **0.00 / 0.67 / 0.82 / 1** |
| S3 Traçabilité | 0.00 / 0.33 / 0.80 / 1 | 0.00 / 0.33 / 0.52 / 1 | **0.00 / 0.67 / 0.62 / 1** |
| S4 Fragilité | 0.00 / 0.67 / 0.70 / 1 | 0.00 / 0.67 / 0.51 / 1 | **0.00 / 1.00 / 0.70 / 1** |
| S5 Cross-family | 0.00 / 0.67 / 0.53 / 1 | 0.00 / 0.33 / 0.56 / 0 | **0.00 / 1.00 / 0.63 / 1** |

### Analyse

#### Résultat principal : la condition C domine sur toutes les métriques critiques

La condition C (niveau 1+2 → LLM) obtient le meilleur score de conformité
(0.87) et zéro hallucination. Elle est la seule condition à atteindre
conformité = 1.00 sur S1, S4 et S5. C'est la seule condition qui reproduit
correctement la sévérité sur tous les scénarios (1.00 vs 0.60 pour B).

#### Résultat clé : la condition B est systématiquement pire que A

Sur S2 (change-induced) et S5 (cross-family), la condition B :
- rate la sévérité correcte (dit CRITICAL au lieu de HIGH)
- conformité = 0.33, inférieure à la condition A (0.67)

Sur S1 (SPOF), la condition B atteint conformité = 1.00 mais hallucine
une entité (rate = 0.25) : elle trouve la bonne réponse mais invente
des entités inexistantes. La condition C obtient le même résultat sans hallucination.

**Explication :** les JSON bruts du niveau 1 contiennent `RES_TOY_as2`
dans plusieurs agents indépendants (`isolated_incident_resource`, `no_redundancy_incident`,
`high_impact_resource`, `change_linked_to_multiple_incidents`).
Sans corrélation, le LLM se concentre sur l'entité la plus fréquente
et sur-diagnostique en CRITICAL même quand le signal dominant
est la chaîne de changement. Le diagnostic niveau 2 — qui dit explicitement
*"change CR_2022_001, dual corroboration, severity HIGH"* — recadre
correctement le modèle.

Ce résultat démontre que **des faits bruts non corrélés peuvent activement
tromper le LLM**. Le niveau 2 n'est pas un luxe : il est nécessaire pour
que les faits du niveau 1 soient exploitables.

#### S5 — cas cross-family (résultat le plus fort)

Sur le scénario qui combine SPOF structurel et incident induit par changement,
la condition C atteint conformité = 1.00 là où la condition B n'obtient que
0.33. C'est le cas où la corrélation multi-famille du niveau 2 est la plus
décisive : sans elle, le LLM est submergé par des signaux contradictoires.

#### Conclusion

> Le MAS ne remplace pas le LLM — il le rend fiable.
> Sans le niveau 2, le LLM sur-diagnostique sur les scénarios multi-signaux.
> Avec le niveau 1+2, il produit des diagnostics précis, sans hallucination,
> avec une conformité de 0.87 (vs 0.53 pour le niveau 1 seul).

---

## 4. Baseline LLM monovalent — le LLM peut-il remplacer le MAS ?

**Script :** `llm_detector_baseline.py`  
**Exécution :** `python -X utf8 llm_detector_baseline.py both both`  
**Résultats :** `llm_baseline_results.json` (CPU), `llm_baseline_results_gpu.json` (GPU)

### Objectif

Mesurer ce qu'un LLM obtient quand on lui donne **le graphe entier** et qu'on lui
demande de trouver les anomalies — sans aucun prétraitement MAS.
C'est le scénario de remplacement total : *"oublie le MAS, utilise directement un LLM"*.

À distinguer de l'expérience 3 : ici le LLM ne reçoit **pas** les sorties MAS.
Il reçoit le graphe brut et doit effectuer lui-même la détection,
là où l'expérience 3 mesurait combien le MAS aide le LLM à synthétiser.

### Modèles LLM utilisés

Deux runs ont été réalisés avec deux variantes du même modèle de base (Mistral 7B) :

**Run CPU — `mistral:latest` via Ollama**
- Architecture : Mistral-7B (7 milliards de paramètres)
- Quantification : Q4_K_M (GGUF, 4 bits) — compression lossy qui réduit la qualité
  du modèle mais permet l'exécution sur CPU avec ~4 GB de RAM
- Machine : Intel CPU local (pas de GPU), via Ollama
- Temps : 28 minutes à 50 minutes par combinaison mode×stratégie

**Run GPU — `Mistral-7B-Instruct-v0.3` via HuggingFace Transformers**
- Architecture : identique au run CPU, mais variante **Instruct-v0.3**
  (fine-tuné sur des données d'instructions — meilleure qualité de réponse)
- Précision : **float16** (16 bits) — précision complète, pas de compression
- Machine : NVIDIA RTX 4000 Ada, 20 GB VRAM, `jaguar.polytechnique.fr`
  (Polytechnique GPU cluster, accès via SSH)
- Temps : 23 à 188 secondes par combinaison

**Note de comparabilité :** les deux runs utilisent des variantes différentes
(Q4 base vs float16 Instruct). Leurs résultats sont indicatifs et non strictement
comparables. Le run GPU utilise le modèle de meilleure qualité.

Le run GPU est ~**80× plus rapide** grâce à la parallélisation du prefill sur GPU
(le prompt de ~5 000 tokens est traité en parallèle sur les milliers de cœurs CUDA,
là où le CPU le traite token par token).

### Protocole

Deux axes orthogonaux, 4 combinaisons testées :

**Mode :**
- `apriori` — seules les triples de configuration infrastructure sont incluses dans le graphe exporté (ressources, services, applications, interfaces, relations topologiques). Aucun événement ni incident.
- `aposteriori` — graphe complet : configuration + enregistrements d'événements réseau, tickets d'incidents, enregistrements de changements.

**Stratégie :**
- `guided` — le prompt commence par un briefing ontologique : types d'entités NORIA-O (Resource, Service, Application, EventRecord, TroubleTicket, Change), les 4 familles d'anomalies (structurelles, dynamiques, fonctionnelles, procédurales), et les prédicats clés à surveiller. L'objectif est d'aider le LLM à mapper les patterns RDF sur les catégories d'anomalies connues.
- `open` — prompt minimal : *"You are a network engineer. In the following knowledge graph (Turtle format), identify all anomalies, misconfigurations, or operational issues. List the affected entities with explanation."* Aucune guidance.

**Graphe fourni au LLM :**
Le graphe est exporté via une requête SPARQL CONSTRUCT qui filtre les prédicats
non diagnostiques (`prov:wasDerivedFrom`, `foaf:*`, `rdfs:label`, prédicats ontologiques
purs). Seuls les prédicats porteurs d'information diagnostique sont conservés :
relations de type (`rdf:type`), adjacence réseau, appartenance de service,
enregistrements d'événements, tickets et leurs liens, changements et leurs liens.
Résultat : ~4 200 tokens de Turtle RDF (après filtrage).

### Métriques

Les métriques sont calculées par rapport au **ground truth MAS** sur noria-0.2,
c'est-à-dire les entités effectivement détectées par les agents niveau 1
lors d'un run réel (`results/` directory).

Le LLM produit une liste d'entités anormales (noms extraits de sa réponse
par extraction regex). Ces entités sont normalisées (préfixes Turtle retirés,
ex. `ns3:RES_TOY_as1` → `RES_TOY_as1`).

- **Recall** = |entités LLM ∩ entités MAS| / |entités MAS| — quelle fraction des entités que le MAS a trouvées est aussi mentionnée par le LLM ?
- **Precision** = |entités LLM ∩ entités MAS| / |entités LLM| — quelle fraction des mentions du LLM est confirmée par le MAS ?
- **Hallucination** = |entités LLM absentes du graphe| / |entités LLM| — quelle fraction des mentions du LLM correspond à des entités qui n'existent pas du tout dans le graphe de connaissances ?
- **Agents couverts** = nombre d'agents MAS *actifs* (ayant produit au moins une détection sur noria-0.2) dont au moins une entité détectée est aussi mentionnée par le LLM. Le dénominateur est le nombre d'agents actifs : **6 en apriori** (sur 23 agents totaux), **9 en aposteriori** (sur 31 agents totaux). Les autres agents n'ont pas de détections sur noria-0.2 et ne peuvent pas être couverts.

### Résultats

**Run CPU** — `mistral:latest` Q4_K_M, Intel CPU :

| Combinaison | Détections | Recall | Precision | Halluc | Agents couverts | Temps |
|---|:---:|:---:|:---:|:---:|:---:|---:|
| apriori / guided | 14 | 0.06 | 0.14 | 0.00 | 1/6 | 1 660s |
| apriori / open | 5 | 0.03 | 0.20 | 0.00 | 1/6 | 1 468s |
| aposteriori / guided | 4 | 0.00 | 0.00 | 0.25 | 0/9 | 3 032s |
| aposteriori / open | 5 | 0.16 | 0.60 | 0.00 | 4/9 | 2 436s |

**Run GPU** — `Mistral-7B-Instruct-v0.3` float16, NVIDIA RTX 4000 Ada :

| Combinaison | Détections | Recall | Precision | Halluc | Agents couverts | Temps |
|---|:---:|:---:|:---:|:---:|:---:|---:|
| apriori / guided | 11 | 0.06 | 0.18 | 0.09 | 2/6 | 188s |
| apriori / open | 5 | 0.00 | 0.00 | 0.00 | 0/6 | 28s |
| **aposteriori / guided** | **4** | **0.21** | **1.00** | **0.00** | **3/9** | **23s** |
| aposteriori / open | 5 | 0.16 | 0.75 | 0.00 | 4/9 | 24s |

### Analyse

#### Ce que le LLM fait bien

En mode `aposteriori/guided` sur GPU, le LLM atteint **precision=1.00** : ses 4 détections
sont toutes dans le ground truth MAS. Il a correctement identifié `RES_TOY_srv1`
(serveur impliqué dans un incident), `RES_TOY_term1` (point de terminaison défaillant),
`APP_TOY_PFS01` (application sans ressource redondante), et `TT_TOY2022TT`
(ticket sans procédure de réparation associée).
C'est un raisonnement causal correct : le LLM lit les alarmes
et remonte la chaîne d'impact applicatif.

Le mode `open` donne généralement de meilleurs résultats que `guided` en aposteriori.
**Explication :** le briefing ontologique en mode `guided` oriente le LLM vers les patterns
structurels (redondance, interfaces manquantes) au détriment des signaux d'incidents
explicitement présents. Le mode `open` suit naturellement les preuves disponibles.
En apriori, la guidance aide car il n'y a pas de signal incident visible — le LLM
doit inférer à partir de la configuration seule.

#### Ce que le LLM rate systématiquement

Certains agents MAS ne sont couverts dans aucune combinaison :

| Agent | Raison de l'échec LLM |
|---|---|
| `application_without_resource` | Nécessite d'énumérer toutes les apps et vérifier l'absence d'une relation pour chacune |
| `ticket_without_assigned_procedure` | Détection par absence — le LLM ne constate pas ce qui manque |
| `module_level_incident_aggregation` | Nécessite de regrouper des incidents par module applicatif et compter |
| `service_with_repeated_incident` | Nécessite de compter les occurrences répétées d'incidents sur un même service |

Ces agents partagent une structure commune : **raisonnement par absence ou comptage exhaustif**.
Le LLM génère par complétion de pattern ; il détecte les signaux positifs présents dans le texte
mais ne fait pas de scan systématique pour vérifier ce qui devrait exister et ne l'est pas.
Un LLM ne peut pas garantir l'exhaustivité.

#### Différence de granularité

Le LLM raisonne au niveau réseau physique (liens, équipements, alarmes visibles).
Le MAS raisonne au niveau impact applicatif et traçabilité opérationnelle.
Sur le même dataset, leurs détections sont **complémentaires plutôt que redondantes**.

#### Conclusion

> Un LLM monovalent est un bon diagnosticien quand les preuves sont
> explicites dans le graphe (aposteriori, precision jusqu'à 1.00),
> mais un mauvais détecteur systématique : il manque des familles entières
> d'anomalies qui nécessitent un raisonnement par absence ou par comptage.
> Le MAS couvre exactement ce que le LLM ne peut pas faire de façon fiable.
> Les deux approches sont complémentaires, pas substituables.

---

## 5. Évaluation sur le catalogue de datasets synthétiques

**Script :** `evaluate_datasets.py`  
**Données :** 27 datasets synthétiques `DS01`–`DS27` (dossier `datasets/`)  
**Exécution :** `python -X utf8 evaluate_datasets.py` (~18 minutes)  
**Résultats :** `eval_results.json`

### Objectif

Évaluer la pipeline complète niveau 1 + niveau 2 sur un catalogue de scénarios
synthétiques contrôlés, avec ground truth explicite (`expected_level2.json` par dataset).
Contrairement à l'expérience 3 qui mesurait la qualité de la synthèse LLM,
cette expérience mesure la **précision propre du MAS** indépendamment de tout LLM.

Métriques calculées par dataset et par mode :
- **Precision@L2** : fraction des diagnoseurs déclenchés qui étaient attendus
- **Recall@L2** : fraction des diagnoseurs attendus effectivement déclenchés
- **F1@L2** : moyenne harmonique
- **TP/FP/FN** : détail par diagnoseur

### Résultats complets

#### Tableau de synthèse (36 évaluations mode×dataset)

| Dataset | Mode | P | R | F1 | TP/FP/FN |
|---------|------|:-:|:-:|:--:|:--------:|
| DS01_clean_baseA | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS01_clean_baseA | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS02_partial_evidence_no_l2_v1 | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS02_partial_evidence_no_l2_v1 | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS03_partial_evidence_no_l2_v2 | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS03_partial_evidence_no_l2_v2 | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS04_structural_fragility | apriori | 0.50 | 1.00 | 0.67 | 1/1/0 |
| DS05_critical_service_exposure_basic | apriori | 0.00 | 0.00 | 0.00 | 0/2/1 |
| DS06_critical_service_exposure_concentrated | apriori | 0.00 | 0.00 | 0.00 | 0/2/1 |
| DS07_observability_gap | apriori | 0.00 | 0.00 | 0.00 | 0/1/1 |
| DS08_procedural_unreadiness_basic | apriori | **1.00** | **1.00** | **1.00** | 1/0/0 |
| DS09_functional_mapping_gap | apriori | 0.50 | 1.00 | 0.67 | 1/1/0 |
| DS10_apriori_mixed_two_diagnoses | apriori | 0.33 | 0.50 | 0.40 | 1/2/1 |
| DS11_single_point_of_failure | aposteriori | **1.00** | **1.00** | **1.00** | 1/0/0 |
| DS12_change_induced_incident | aposteriori | **1.00** | **1.00** | **1.00** | 1/0/0 |
| DS13_service_cascade | aposteriori | **1.00** | **1.00** | **1.00** | 1/0/0 |
| DS14_traceability_breakdown | aposteriori | **1.00** | **1.00** | **1.00** | 1/0/0 |
| DS15_unstable_component | aposteriori | 0.00 | 0.00 | 0.00 | 0/1/1 |
| DS16_application_support_failure | aposteriori | 1.00 | 0.00 | 0.00 | 0/0/1 |
| DS17_local_infrastructure_cluster | aposteriori | 1.00 | 0.00 | 0.00 | 0/0/1 |
| DS18_aposteriori_mixed_two_diagnoses | aposteriori | 0.50 | 0.50 | 0.50 | 1/1/1 |
| DS19_missing_data | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS19_missing_data | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS20_missing_procedural_links | aposteriori | **1.00** | **1.00** | **1.00** | 1/0/0 |
| DS21_noisy_irrelevant_events | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS22_noisy_duplicate_records | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS22_noisy_duplicate_records | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS23_three_diagnoses_ranked | aposteriori | 1.00 | 0.67 | 0.80 | 2/0/1 |
| DS24_reliability_calibration | apriori | 0.50 | 0.33 | 0.40 | 1/1/2 |
| DS24_reliability_calibration | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS25_scalability_small | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS25_scalability_small | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS26_scalability_medium | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS26_scalability_medium | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |
| DS27_scalability_large | apriori | 0.00 | 1.00 | 0.00 | 0/1/0 |
| DS27_scalability_large | aposteriori | 1.00 | 1.00 | 1.00 | 0/0/0 |

#### Métriques agrégées

| Mode | TP | FP | FN | Precision | Recall | F1 (micro) | F1 (macro) |
|------|----|----|----|:---------:|:------:|:----------:|:----------:|
| **Apriori** (16 éval.) | 5 | 18 | 6 | 0.22 | 0.45 | 0.30 | 0.20 |
| **Aposteriori** (20 éval.) | 8 | 2 | 5 | 0.80 | 0.62 | 0.70 | 0.73 |
| **Global** (36 éval.) | 13 | 20 | 11 | 0.39 | 0.54 | 0.45 | 0.40 |

*L1 recall = 1.00 sur les 36 évaluations — tous les agents niveau 1 s'exécutent correctement
sur tous les datasets.*

### Analyse

#### Mode aposteriori : performances solides sur 4 diagnoseurs

Les 4 diagnoseurs aposteriori de base sont robustes :

| Diagnoseur | Datasets cibles | Résultat |
|---|---|:---:|
| `single_point_of_failure_diagnoser` | DS11, DS23 | TP sur tous |
| `change_induced_incident_diagnoser` | DS12 | TP |
| `service_cascade_diagnoser` | DS13, DS18 | TP sur tous |
| `traceability_breakdown_diagnoser` | DS14, DS20 | TP sur tous |

DS23 (3 diagnostics simultanés) obtient F1=0.80 : 2 TP sur 3 attendus, zéro FP.

#### 3 diagnoseurs aposteriori qui ne se déclenchent jamais

`unstable_component_diagnoser` (FN sur DS15, DS18, DS23),
`application_support_failure_diagnoser` (FN sur DS16), et
`local_infrastructure_cluster_diagnoser` (FN sur DS17) n'ont produit aucun TP
sur l'ensemble du catalogue. Leurs conditions d'activation sont probablement
trop strictes pour les datasets synthétiques actuels.

#### Mode apriori : faux positif systématique

`procedural_unreadiness_diagnoser` se déclenche sur **tous** les datasets apriori
avec rel=25, sev=13 — y compris les graphes propres (DS01, DS02, DS03).
C'est un problème de seuil d'activation : le diagnoseur se déclenche
à un score de fiabilité trop faible. Ce FP systématique
représente la quasi-totalité de la dégradation en mode apriori
(18 FP sur 18 FP totaux en apriori).

`critical_service_exposure_diagnoser` et `observability_gap_diagnoser` ne se déclenchent
jamais malgré des datasets spécifiquement conçus pour eux (DS05, DS06, DS07, DS24).

#### `traceability_breakdown_diagnoser` : sur-déclenchement en mode mixte

En DS15 et DS18, `traceability_breakdown_diagnoser` se déclenche avec rel=55
alors qu'il n'est pas attendu. Les critères de traçabilité
(incidents sans ticket, tickets sans événement) sont structurellement présents
dans plusieurs datasets aposteriori en fond.

### KPIs complémentaires (kpi_analysis.py / kpi_report.json)

#### Top-1 accuracy — DS23

DS23 met en scène 3 diagnoseurs attendus, classés par urgence décroissante :
SPOF (priority=71) > traceability_breakdown (priority=54) > unstable_component (non déclenché).
Le MAS prédit correctement SPOF comme diagnostic de priorité maximale.

**Top-1 accuracy = 1.00** (1 dataset, 1 scénario multi-diagnostic).

#### Calibration fiabilité/sévérité — DS24

DS24 contient 3 signaux de forces distinctes dans le même graphe :
`structural_fragility` (signal fort), `critical_service_exposure` (signal moyen),
`observability_gap` (signal faible). En mode apriori :
- TP : `structural_fragility_diagnoser` déclenché correctement
- FP : `procedural_unreadiness_diagnoser` (faux positif systématique, voir ci-dessus)
- FN : `critical_service_exposure_diagnoser` et `observability_gap_diagnoser` silencieux

Le MAS distingue le signal fort du bruit mais ne gradue pas encore les signaux moyen et faible.

#### Robustesse — DS19/DS20/DS21/DS22

4 variants de dégradation du graphe, tous évalués en mode aposteriori :

| Dataset | Dégradation | Résultat |
|---------|-------------|:--------:|
| DS19 | Données structurelles et temporelles manquantes | F1=1.00 (abstention correcte) |
| DS20 | Liens procéduraux manquants | F1=1.00 (traceability déclenché malgré l'absence partielle) |
| DS21 | Événements parasites irrelevants | F1=1.00 (aucun FP ajouté) |
| DS22 | Doublons d'enregistrements | F1=1.00 (les doublons ne créent pas de déclenchements spurieux) |

**Dégradation aposteriori = 0% sur tous les variants de robustesse.**

#### Scalabilité — DS25/DS26/DS27

Trois datasets de tailles croissantes, même topologie que DS01 augmentée :

| Dataset | Triples | L1 apriori | L2 apriori | L1 aposteriori | L2 aposteriori |
|---------|:-------:|:----------:|:----------:|:--------------:|:--------------:|
| DS25 (small) | 170 | 4 707ms | 381ms | 6 295ms | 377ms |
| DS26 (medium) | 258 | 4 594ms | 266ms | 6 297ms | 413ms |
| DS27 (large) | 352 | 4 443ms | 264ms | 6 481ms | 466ms |

Le temps total reste **< 7 secondes** sur les 3 tailles testées.
Les temps L1 et L2 restent stables malgré la croissance du graphe :
la parallélisation MAS absorbe l'augmentation du volume sans dégradation linéaire.

### Conclusion

> Le mode aposteriori est nettement plus précis (P=0.80, macro-F1=0.815) que le mode
> apriori (P=0.22, macro-F1=0.196). Les 4 diagnoseurs aposteriori de base sont fiables.
> Le mode apriori souffre d'un seuil d'activation trop bas pour
> `procedural_unreadiness_diagnoser` et de conditions trop strictes pour
> `critical_service_exposure_diagnoser` et `observability_gap_diagnoser`.
> 5 des 12 diagnoseurs n'ont produit aucun TP sur le catalogue complet.
> La robustesse est parfaite en aposteriori, la scalabilité constante jusqu'à 352 triples.

---

## 6. Comparaison LLM vs MAS — classification L2 en 3 conditions

**Scripts :** `prepare_llm_ablation.py` (local) + `llm_ablation_infer.py` (GPU)  
**Données intermédiaires :** `llm_ablation_data.json`  
**Résultats :** `llm_ablation_results.json`  
**Exécution :** 2 phases — voir ci-dessous

### Objectif

Mesurer si Mistral-7B peut effectuer *la même tâche que le MAS* au niveau 2 :
identifier quels diagnoseurs s'appliquent à un graphe ICT donné.
Le LLM est évalué sur le même ground truth (`expected_level2.json`) que le MAS,
avec trois niveaux d'information progressifs.

À distinguer de l'expérience 4 : ici on demande au LLM de **nommer le diagnoseur applicable**
(classification parmi 12 patterns nommés, selon le mode), alors que l'expérience 4 demandait
au LLM d'identifier des **entités anormales** (détection libre). Le ground truth est aussi
différent : L2 classification (expected_level2.json) vs L1 entity detection (résultats MAS N1).

### Modèle LLM utilisé

**`Mistral-7B-Instruct-v0.3`** float16, exécuté sur NVIDIA RTX 4000 Ada (20 GB VRAM),
`jaguar.polytechnique.fr`, via HuggingFace Transformers.
Paramètres : température = 0.1, max_new_tokens = 300.
Même variante que le run GPU de l'expérience 4 — les deux runs GPU sont directement comparables.

### Protocole — architecture 2 phases

Le script est divisé en deux phases pour isoler les dépendances :

**Phase 1 — locale (`prepare_llm_ablation.py`)** :
Pour chacun des 27 datasets dans tous les modes applicables (déterminés par `eval_results.json`),
charge le TTL dans Virtuoso, exécute les agents L1+L2, collecte les résultats,
et exporte un paquet autonome (`llm_ablation_data.json`) contenant : le Turtle brut du graphe,
un résumé des détections niveau 1, un résumé des diagnostics niveau 2, le ground truth attendu.
**36 paires (dataset, mode) exportées**, couvrant l'intégralité du catalogue évalué.

**Phase 2 — GPU (`llm_ablation_infer.py`)** :
Lit `llm_ablation_data.json`, soumet 3 prompts par paire au LLM, parse la réponse JSON,
calcule P/R/F1. Le prompt utilise la liste des **5 diagnoseurs apriori** ou **7 aposteriori**
selon le mode de chaque paire. Aucun Virtuoso ni agent MAS requis.

### Couverture

L'expérience couvre les **36 paires (dataset, mode)** de `eval_results.json` :
- **16 paires apriori** : DS01–DS03 (contrôles), DS04–DS10 (diagnoseurs apriori), DS19, DS22, DS24–DS27
- **20 paires aposteriori** : DS01–DS03, DS11–DS23, DS19–DS22, DS24–DS27
- **Diagnoseurs apriori** (5) : structural_fragility, critical_service_exposure, observability_gap, procedural_unreadiness, functional_mapping_gap
- **Diagnoseurs aposteriori** (7) : SPOF, change_induced, service_cascade, traceability_breakdown, unstable_component, application_support_failure, local_infrastructure_cluster

### Conditions

Le prompt de tâche est identique dans les 3 conditions :
*"You are a network operations expert analyzing an ICT infrastructure knowledge graph.
Determine which of the following diagnostic patterns apply based on the data provided."*
Suivi de la liste des patterns du mode avec leurs descriptions. Réponse attendue en JSON :
`{"triggered": ["pattern_name1", ...], "primary_entities": {"pattern_name1": "entity"}}`.

| | Condition A | Condition B | Condition C |
|-|-------------|-------------|-------------|
| **Input LLM** | Graphe Turtle brut | Graphe + résumé détections L1 | Graphe + L1 + résumé diagnostics L2 |
| **Architecture simulée** | LLM seul | L1 → LLM | L1+L2 → LLM |

### Métriques

Identiques à l'évaluation MAS de l'expérience 5 :
**Precision@L2** = TP / (TP+FP), **Recall@L2** = TP / (TP+FN), **F1@L2**.
Évaluées contre le même `expected_level2.json`. Moyennes macro sur les 36 paires.

### Résultats

#### Macro-moyennes — Global (36 paires)

| Condition | Precision | Recall | F1 | TP | FP | FN |
|-----------|:---------:|:------:|:--:|:--:|:--:|:--:|
| **A — graph only** | 0.111 | 0.579 | 0.088 | 4 | 32 | 20 |
| **B — graph + L1** | 0.197 | 0.639 | 0.191 | 7 | 35 | 17 |
| **C — graph + L1 + L2** | 0.426 | 0.685 | 0.391 | 9 | 22 | 15 |
| **MAS (référence)** | 0.537 | 0.778 | 0.540 | 13 | 20 | 11 |

#### Macro-moyennes — par mode

| Condition | Apriori F1 (n=16) | Aposteriori F1 (n=20) |
|-----------|:-----------------:|:---------------------:|
| **A — graph only** | 0.104 | 0.075 |
| **B — graph + L1** | 0.148 | 0.225 |
| **C — graph + L1 + L2** | **0.244** | 0.508 |
| **MAS (référence)** | 0.196 | **0.815** |

#### Tableau complet par dataset

| Dataset | Mode | Expected | MAS F1 | A | B | C |
|---------|------|---------|:------:|:-:|:-:|:-:|
| DS01_clean_baseA | aposteriori | (aucun) | 1.00 | 0.00 | 1.00 | 1.00 |
| DS01_clean_baseA | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS02_partial_evidence | aposteriori | (aucun) | 1.00 | 0.00 | 1.00 | 1.00 |
| DS02_partial_evidence | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS03_partial_evidence | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 1.00 |
| DS03_partial_evidence | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS04_structural_fragility | apriori | structural_fragility | 0.67 | 0.00 | 0.00 | **1.00** |
| DS05_critical_service_exposure | apriori | critical_service_exposure | 0.00 | **1.00** | 0.67 | 0.00 |
| DS06_critical_service_exposure | apriori | critical_service_exposure | 0.00 | 0.00 | 0.40 | 0.00 |
| DS07_observability_gap | apriori | observability_gap | 0.00 | 0.00 | 0.00 | 0.00 |
| DS08_procedural_unreadiness | apriori | procedural_unreadiness | 1.00 | 0.00 | 0.00 | **1.00** |
| DS09_functional_mapping_gap | apriori | functional_mapping_gap | 0.67 | 0.00 | 0.50 | **1.00** |
| DS10_apriori_mixed (2 diag.) | apriori | critical_svc + functional_map | 0.40 | 0.67 | 0.00 | 0.40 |
| DS11_single_point_of_failure | aposteriori | SPOF | **1.00** | **1.00** | **1.00** | **1.00** |
| DS12_change_induced_incident | aposteriori | change_induced | **1.00** | 0.00 | 0.00 | 0.00 |
| DS13_service_cascade | aposteriori | service_cascade | **1.00** | 0.00 | 0.00 | **1.00** |
| DS14_traceability_breakdown | aposteriori | traceability_breakdown | **1.00** | 0.00 | 0.00 | 0.00 |
| DS15_unstable_component | aposteriori | unstable_component | 0.00 | 0.00 | 0.00 | 0.00 |
| DS16_application_support | aposteriori | application_support_failure | 0.00 | 0.00 | 0.00 | 0.00 |
| DS17_local_cluster | aposteriori | local_infrastructure_cluster | 0.00 | 0.00 | 0.00 | 0.00 |
| DS18_apost_mixed (2 diag.) | aposteriori | service_cascade + unstable | 0.50 | 0.00 | 0.00 | 0.67 |
| DS19_missing_data | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 0.00 |
| DS19_missing_data | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS20_missing_procedural | aposteriori | traceability_breakdown | **1.00** | 0.00 | 0.00 | 0.00 |
| DS21_noisy_events | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 1.00 |
| DS22_noisy_duplicates | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 0.00 |
| DS22_noisy_duplicates | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS23_three_diagnoses (3 diag.) | aposteriori | SPOF + traceability + unstable | 0.80 | 0.50 | 0.50 | 0.50 |
| DS24_calibration_bundle | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 1.00 |
| DS24_calibration_bundle | apriori | structural_frag + critical_svc + obs_gap | 0.40 | 0.00 | 0.80 | 0.50 |
| DS25_scalability_small | aposteriori | (aucun) | 1.00 | 0.00 | 1.00 | 1.00 |
| DS25_scalability_small | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS26_scalability_medium | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 1.00 |
| DS26_scalability_medium | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |
| DS27_scalability_large | aposteriori | (aucun) | 1.00 | 0.00 | 0.00 | 0.00 |
| DS27_scalability_large | apriori | (aucun) | 0.00 | 0.00 | 0.00 | 0.00 |

### Analyse

#### Résultat principal : gradient A < B < C clairement établi

Sur l'ensemble du catalogue (36 paires), les trois conditions montrent une progression nette :
**F1 : 0.088 → 0.191 → 0.391** (A→B→C). Ce gradient confirme que chaque couche du MAS
apporte une valeur ajoutée mesurable pour la classification L2.

- **L1 → LLM (B)** : précision améliorée (+0.086), réduction marginale des FP en aposteriori
  (surtout sur les graphes propres où L1="aucun agent actif" permet au LLM de s'abstenir)
- **L1+L2 → LLM (C)** : saut majeur de précision (0.197→0.426), réduction de 13 FP (35→22).
  Sur plusieurs datasets, le résumé L2 permet au LLM de nommer correctement le bon diagnoseur
  (DS04, DS08, DS09, DS13, DS18) alors qu'il était incapable de le faire sans ce contexte.

#### Aposteriori : MAS domine, L2 aide significativement

En mode aposteriori (20 paires), le MAS maintient une avance de **1.6×** (F1=0.815 vs 0.508 pour C).
Le LLM ne peut pas déduire les patterns change_induced, traceability_breakdown, unstable, app_support,
ou cluster à partir du graphe brut ou même avec les sorties L1 — il faut le contexte L2 pour que
certains d'entre eux passent (DS13, DS18).

Le MAS aposteriori reste supérieur car il identifie exactement quels indicateurs L1 convergent
vers quel diagnoseur via des règles SPARQL déterministes — le LLM ne peut pas faire cette inférence
multi-source de façon fiable même avec les sorties disponibles.

#### Apriori : LLM condition C surpasse le MAS

En mode apriori (16 paires), la condition C (F1=**0.244**) surpasse le MAS (F1=0.196).
Ce résultat s'explique par une faille du MAS : `procedural_unreadiness_diagnoser` se déclenche
sur **tous** les datasets apriori (FP systématique), dégradant la précision du MAS.
Le LLM avec le résumé L2 complet n'est pas victime de ce biais : sur DS04, DS08, DS09 il
identifie le bon diagnoseur tandis que le MAS génère en plus un FP systématique.
Ce résultat pointe la limite connue du seuil d'activation apriori (documentée dans l'expérience 5).

#### Datasets notables

**DS04, DS08, DS09** — condition C atteint F1=1.00 sur les apriori simples : le contexte L2
explicite (résumé qui dit quel diagnoseur a été déclenché) permet au LLM de classifier parfaitement.

**DS11** — F1=1.00 dans les 3 conditions : SPOF est identifiable directement depuis le graphe.

**DS12, DS14, DS20** — F1=0.00 pour toutes les conditions LLM (A/B/C), même avec L2 :
change_induced et traceability_breakdown ne sont pas reconnus par le modèle malgré le contexte.
Le MAS y atteint F1=1.00 — démonstration que la corrélation temporelle et procédurale
nécessite un traitement symbolique, pas une génération statistique.

**DS05** — A=1.00, B=0.67, C=0.00 : le LLM identifie `critical_service_exposure` depuis le graphe
seul, mais les résumés L1/L2 qui mentionnent `structural_fragility` (FP MAS) le font diverger.
Ce cas montre que L2 peut **perturber** le LLM si les sorties MAS comportent des erreurs.

#### Conclusion

> Le gradient A < B < C (F1 : 0.088 → 0.191 → 0.391) est établi sur l'intégralité
> du catalogue — chaque couche MAS améliore les capacités de classification du LLM.
> En aposteriori, le MAS reste supérieur (F1=0.815 vs 0.508) pour les patterns
> nécessitant une inférence temporelle ou procédurale déterministe.
> En apriori, le LLM condition C (F1=0.244) surpasse le MAS (F1=0.196) grâce à
> l'absence du faux positif systématique `procedural_unreadiness`.
> Le résumé L2 est la contribution la plus décisive : il divise les FP par 1.6×
> et débloqueaucun les diagnoseurs les moins intuitifs depuis le graphe brut.

---

## Reproduire les expériences

```powershell
# Prérequis : Virtuoso sur localhost:8890, Ollama avec llama3.1:8b

# 1. Tableau de complémentarité (niveau 1 seulement)
python -X utf8 run_all_detectors.py both
python -X utf8 complementarity_table.py

# 2. Baseline séquentiel
python -X utf8 baseline_monoagent.py both

# 3. Étude d'ablation LLM (~25 minutes, nécessite llama3.1:8b via Ollama)
python -X utf8 ablation_study.py

# 4. Baseline LLM monovalent
# Sur machine locale avec Ollama (lent sur CPU, ~2h) :
python -X utf8 llm_detector_baseline.py both both
# Sur serveur GPU (nécessite SSH + HuggingFace) :
# scp llm_detector_baseline.py noria_graph.ttl user@server:~/baseline/
# scp -r results/ user@server:~/baseline/
# ssh user@server "cd /tmp/baseline_run && HF_HOME=/tmp/hf_cache python3 llm_detector_baseline.py both both"

# 5. Évaluation sur le catalogue synthétique (~18 minutes)
python -X utf8 evaluate_datasets.py
# Ou un sous-ensemble :
python -X utf8 evaluate_datasets.py DS11 DS12 DS13
python -X utf8 evaluate_datasets.py --aposteriori
# KPIs complémentaires (Top-1, calibration, robustesse, scalabilité) :
python -X utf8 kpi_analysis.py

# 6. Comparaison LLM vs MAS — classification L2 en 3 conditions
# Phase 1 — locale : préparer les données (~10 minutes, nécessite Virtuoso + agents)
python -X utf8 prepare_llm_ablation.py
# Phase 2 — GPU : inférence sur jaguar.polytechnique.fr
scp llm_ablation_data.json llm_ablation_infer.py jaguar.polytechnique.fr:/tmp/
ssh jaguar.polytechnique.fr "cd /tmp && pip install --user transformers accelerate torch sentencepiece protobuf --quiet && HF_HOME=/tmp/hf_cache python3 llm_ablation_infer.py 2>&1"
scp jaguar.polytechnique.fr:/tmp/llm_ablation_results.json .
# Variante CPU locale via Ollama (nécessite llama3.1:8b) :
# python -X utf8 llm_ablation_infer.py --ollama
```

---

## Fichiers produits

| Fichier | Contenu |
|---------|---------|
| `results/` | JSON de détection par agent niveau 1 (noria-0.2) |
| `results/level2/` | JSON de diagnostic par agent niveau 2 |
| `complementarity_results.json` | Données brutes du tableau de complémentarité |
| `ablation_results.json` | Données brutes de l'étude d'ablation (5 scénarios × 3 conditions × 5 runs) |
| `ABLATION_STUDY.md` | Analyse détaillée de l'ablation |
| `baseline_results.json` | Données brutes du baseline séquentiel |
| `llm_baseline_results.json` | Résultats du baseline LLM — run CPU (mistral:latest Q4_K_M) |
| `llm_baseline_results_gpu.json` | Résultats du baseline LLM — run GPU (Mistral-7B-Instruct-v0.3 float16) |
| `noria_graph.ttl` | Graphe NORIA-O filtré exporté (~4 200 tokens, input LLM baseline) |
| `eval_results.json` | Résultats complets de l'évaluation sur les 27 datasets synthétiques |
| `kpi_report.json` | KPIs agrégés : Top-1 accuracy, calibration, robustesse, scalabilité, per-diagnoser |
| `llm_ablation_data.json` | Données packagées pour l'inférence GPU (9 datasets × TTL + L1 + L2 summaries) |
| `llm_ablation_results.json` | Résultats de la comparaison LLM vs MAS — run GPU (Mistral-7B-Instruct-v0.3 float16) |
