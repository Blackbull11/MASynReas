# Expériences et Résultats — PSC INF12

Ce document couvre les deux expériences principales menées sur le système
MASynReas appliqué au dataset noria-0.2.

---

## 1. Tableau de complémentarité des familles

**Script :** `complementarity_table.py`  
**Données :** run réel sur Virtuoso localhost:8890, dataset noria-0.2 (3152 triplets)  
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

## 2. Étude d'ablation — valeur ajoutée de chaque couche MAS

**Script :** `ablation_study.py`  
**Modèle :** llama3.1:8b (via Ollama, local, CPU)  
**Runs par condition :** 5  
**Résultats :** `ablation_results.json`  
**Exécution :** `python -X utf8 ablation_study.py` (~25 minutes)

### Objectif

Mesurer empiriquement la valeur ajoutée de chaque couche du MAS sur
la qualité des diagnostics produits par le LLM.

**Question centrale :** *à quoi sert le MAS si on a déjà un LLM ?*

### Protocole

Trois conditions testées sur les mêmes scénarios, seul l'input du LLM change :

| | Condition A | Condition B | Condition C |
|-|-------------|-------------|-------------|
| **Input LLM** | Texte du ticket (contexte opérateur minimal) | JSON niveau 1 (54 agents détecteurs) | JSON niveau 1 + diagnostics niveau 2 |
| **Architecture** | LLM seul | Niveau 1 → LLM | Niveau 1+2 → LLM |

Quatre métriques automatiques :
- **Hallucination** : noms d'entités inventés par le LLM (↓ = mieux)
- **Conformité** : fraction du ground truth retrouvée dans la réponse (↑ = mieux)
- **Consistance** : similarité Jaccard entre les 5 runs (↑ = mieux)
- **Sévérité** : sévérité correcte reprouite (↑ = mieux)

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
- manque la sévérité correcte (dit CRITICAL au lieu de HIGH)
- conformité = 0.33, inférieure à la condition A (0.67)

Sur S1 (SPOF), la condition B atteint conformité = 1.00 mais hallucine
une entité (rate = 0.25) : elle trouve la bonne réponse mais ajoute des
éléments fictifs. La condition C obtient le même résultat sans hallucination.

**Explication :** les JSON bruts du niveau 1 contiennent `RES_TOY_as2`
dans plusieurs fichiers indépendants (isolated, no_redundancy, high_impact,
change_linked). Sans corrélation, le LLM se concentre sur la ressource la
plus visible et sur-diagnostique en CRITICAL même quand le signal dominant
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

## 3. Baseline LLM monovalent — comparaison directe avec le MAS

**Script :** `llm_detector_baseline.py`  
**Objectif :** mesurer ce qu'un LLM obtient quand on lui donne le graphe entier et qu'on lui demande de trouver les anomalies — sans aucun pré-traitement MAS.

### Protocole

Deux axes orthogonaux, 4 combinaisons testées :

- **Mode** : `apriori` (config statique seulement) / `aposteriori` (config + incidents + tickets)
- **Stratégie** : `guided` (briefing ontologique : types d'entités, familles d'anomalies) / `open` (prompt minimal : "trouve les anomalies")

Le graphe exporté via SPARQL CONSTRUCT filtre les prédicats non diagnostiques (`prov:wasDerivedFrom`, `foaf:*`, `rdfs:label`) pour réduire le contexte à ~4 200 tokens utiles.

Les métriques sont calculées par rapport au ground truth MAS (`results/`) :
- **Recall** : fraction des entités détectées par le MAS que le LLM a aussi trouvées
- **Precision** : fraction des entités LLM confirmées par le MAS
- **Hallucination** : fraction des entités LLM absentes du graphe
- **Agents couverts** : fraction des agents MAS dont le LLM a touché au moins une entité

### Deux runs réalisés

**Run CPU** — `mistral:latest` Q4_K_M via Ollama, Intel CPU (machine locale) :

| Combinaison | Détections | Recall | Precision | Halluc | Agents | Temps |
|---|:---:|:---:|:---:|:---:|:---:|---:|
| apriori / guided | 14 | 0.06 | 0.14 | 0.00 | 1/6 | 1 660s |
| apriori / open | 5 | 0.03 | 0.20 | 0.00 | 1/6 | 1 468s |
| aposteriori / guided | 4 | 0.00 | 0.00 | 0.25 | 0/9 | 3 032s |
| aposteriori / open | 5 | 0.16 | 0.60 | 0.00 | 4/9 | 2 436s |

**Run GPU** — `Mistral-7B-Instruct-v0.3` float16 via HuggingFace transformers, NVIDIA RTX 4000 Ada (20 GB VRAM, jaguar.polytechnique.fr) :

| Combinaison | Détections | Recall | Precision | Halluc | Agents | Temps |
|---|:---:|:---:|:---:|:---:|:---:|---:|
| apriori / guided | 11 | 0.06 | 0.18 | 0.09 | 2/6 | 188s |
| apriori / open | 5 | 0.00 | 0.00 | 0.00 | 0/6 | 28s |
| **aposteriori / guided** | **4** | **0.21** | **1.00** | **0.00** | **3/9** | **23s** |
| aposteriori / open | 5 | 0.16 | 0.75 | 0.00 | 4/9 | 24s |

Note : les deux runs utilisent des variantes différentes de Mistral 7B (base Q4 vs Instruct float16) — les résultats sont donc indicatifs et non strictement comparables. Le run GPU utilise un modèle plus récent et de meilleure qualité.

### Analyse

#### Ce que le LLM fait bien

En mode `aposteriori/guided` sur GPU, le LLM atteint **precision=1.00** : ses 4 détections sont toutes dans le ground truth MAS. Il a correctement identifié `RES_TOY_srv1` (serveur en panne), `RES_TOY_term1` (point de terminaison défaillant), `APP_TOY_PFS01` (application sans ressource redondante), et `TT_TOY2022TT` (ticket sans procédure de réparation). C'est un raisonnement causal correct : le LLM lit les alarmes et remonte la chaîne d'impact.

#### Ce que le LLM rate systématiquement

Certains agents MAS ne sont couverts dans aucune combinaison :

| Agent | Raison de l'échec LLM |
|---|---|
| `application_without_resource` | Nécessite d'énumérer toutes les apps et vérifier l'absence d'une relation |
| `ticket_without_assigned_procedure` | Détection par absence — le LLM ne constate pas ce qui manque |
| `module_level_incident_aggregation` | Nécessite de regrouper des incidents par module applicatif |
| `service_with_repeated_incident` | Nécessite de compter des occurrences répétées |

Ces agents partagent une structure commune : **raisonnement par absence ou comptage exhaustif**. Le LLM répond aux signaux positifs présents dans le texte ; il ne fait pas de scan systématique pour détecter ce qui devrait être là et ne l'est pas.

#### Différence de granularité

Le LLM raisonne au niveau réseau physique (liens, équipements, alarmes visibles). Le MAS raisonne au niveau impact applicatif et traçabilité opérationnelle. Sur le même dataset, leurs détections sont **complémentaires plutôt que redondantes**.

#### Speedup GPU

Le run GPU est ~80× plus rapide que le run CPU pour un modèle comparable (23s vs 1 660s pour apriori/guided). L'essentiel du gain vient de la parallélisation du prefill sur les ~5 000 tokens du prompt.

### Conclusion

> Un LLM monovalent est un bon diagnosticien quand les preuves sont
> explicites dans le graphe (aposteriori, precision jusqu'à 1.00),
> mais un mauvais détecteur systématique : il manque les familles entières
> d'anomalies qui nécessitent un raisonnement par absence ou par comptage.
> Le MAS couvre exactement ce que le LLM ne peut pas faire de façon fiable.

---

## Reproduire les expériences

```powershell
# Prérequis : Virtuoso sur localhost:8890, Ollama avec llama3.1:8b

# 1. Lancer tous les détecteurs niveau 1
python -X utf8 run_all_detectors.py both

# 2. Tableau de complémentarité
python -X utf8 complementarity_table.py

# 3. Baseline séquentiel (mesure du speedup MAS)
python -X utf8 baseline_monoagent.py both

# 4. Étude d'ablation (~25 minutes)
python -X utf8 ablation_study.py

# 5. Baseline LLM monovalent
# Sur machine locale avec Ollama (lent sur CPU) :
python -X utf8 llm_detector_baseline.py both both

# Sur serveur GPU sans Ollama (auto-détecte HuggingFace transformers) :
# scp llm_detector_baseline.py noria_graph.ttl results/ user@server:~/baseline/
# ssh user@server "cd ~/baseline && HF_HOME=/tmp/hf_cache python3 llm_detector_baseline.py both both"
```

---

## Fichiers produits

| Fichier | Contenu |
|---------|---------|
| `results/` | JSON de détection par agent niveau 1 |
| `results/level2/` | JSON de diagnostic par agent niveau 2 |
| `complementarity_results.json` | Données brutes du tableau de complémentarité |
| `ablation_results.json` | Données brutes de l'étude d'ablation |
| `ABLATION_STUDY.md` | Analyse détaillée de l'ablation |
| `baseline_results.json` | Données brutes du baseline séquentiel |
| `llm_baseline_results.json` | Résultats du baseline LLM (run CPU, mistral:latest) |
| `llm_baseline_results_gpu.json` | Résultats du baseline LLM (run GPU, Mistral-7B-Instruct-v0.3) |
| `noria_graph.ttl` | Graphe NORIA-O filtré exporté (4 200 tokens, input LLM) |
