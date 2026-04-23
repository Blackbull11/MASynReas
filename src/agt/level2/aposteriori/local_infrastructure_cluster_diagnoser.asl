/*
 * Local Infrastructure Cluster Diagnoser - Level 2 / A Posteriori
 */

+!run
  <- .print("[LocalInfrastructureClusterDiagnoser] Starting diagnosis...");
     run_python("src/agt/level2/aposteriori/local_infrastructure_cluster_diagnoser.py");
     .print("[LocalInfrastructureClusterDiagnoser] Diagnosis finished.");
     .send(level2_controller, tell, l2_agent_done(local_infrastructure_cluster_diagnoser)).
