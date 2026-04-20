/*
 * Criticality vs Structural Weakness Detector - Structural / A Priori
 *
 * This agent detects critical applications whose visible technical support
 * appears too weak with respect to their business importance.
 *
 * Such cases may indicate single points of failure, incomplete infrastructure
 * mapping, weak resilience design, or architectural inconsistencies.
 */

+selected_mode(apriori)
  <- .print("[CriticalityStructuralWeaknessDetector] Starting detection...");
     run_python("src/agt/structural/apriori/criticality_structural_weakness_detector.py");
     .print("[CriticalityStructuralWeaknessDetector] Detection finished.") .


{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
