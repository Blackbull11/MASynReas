/*
 * Duplicated Functional Mapping Detector - Functional / A Priori
 *
 * This level-1 executor agent detects resources mapped to several
 * applications, which may indicate duplicated or ambiguous functional
 * mappings.
 */

+selected_mode(apriori)
  <- .print("[DuplicatedFunctionalMappingDetector] Starting detection...");
     run_python("src/agt/functional/apriori/duplicated_functional_mapping_detector.py");
     .print("[DuplicatedFunctionalMappingDetector] Detection finished.").
