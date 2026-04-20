# MASynReas

MASynReas is a multi-agent system for anomaly diagnosis in a knowledge graph representing an ICT or telecommunication network.

The project is implemented with:
- JaCaMo for the multi-agent system
- Python scripts for SPARQL query execution
- OpenLink Virtuoso as the SPARQL endpoint
- NORIA-O as the ontology used to structure the graph

## Current Scope

The repository currently contains implemented structural agents in two families:
- `src/agt/structural/apriori`
- `src/agt/structural/aposteriori`

The long-term architecture also includes dynamic, functional, and procedural families, but those are not yet implemented in this repository.

## Execution Modes

The MAS can be launched in two modes:
- `apriori`: runs the agents that detect structural weaknesses independently of any incident context
- `aposteriori`: runs the agents that diagnose anomalies and errors in an incident context

The selected mode is configured in the root file [`mas.properties`](/C:/Users/rdesb/psc/MASynReas/mas.properties):

```properties
mode=apriori
```

Accepted values are:
- `apriori`
- `aposteriori`

Before launching the MAS, edit `mas.properties` and set the desired mode.

## Running the MAS

From the project root, run:

```powershell
jacamo multiagentSystem.jcm
```

There is no interactive console prompt for the mode anymore. The MAS reads the mode directly from `mas.properties` at startup.

## Current Behavior

- only the agents belonging to the selected mode are activated
- the `results/` folder is cleared at startup so that it only contains results from the current run
- in `apriori` mode, the MAS stops automatically after all active detectors have completed
- in `aposteriori` mode, automatic shutdown is not enabled by the current controller logic

## Main Entry Files

- [`multiagentSystem.jcm`](/C:/Users/rdesb/psc/MASynReas/multiagentSystem.jcm)
- [`mas.properties`](/C:/Users/rdesb/psc/MASynReas/mas.properties)
- [`src/env/env/PythonExecArtifact.java`](/C:/Users/rdesb/psc/MASynReas/src/env/env/PythonExecArtifact.java)
- [`src/agt/structural/README.md`](/C:/Users/rdesb/psc/MASynReas/src/agt/structural/README.md)
