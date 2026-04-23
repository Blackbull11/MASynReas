package env;

import cartago.Artifact;
import cartago.OPERATION;
import cartago.ObsProperty;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.Comparator;
import java.util.Locale;
import java.util.Properties;
import java.util.stream.Stream;

public class PythonExecArtifact extends Artifact {
    private String pythonExecutable;
    private String selectedMode;
    private String datasetId;
    private long masStartEpochMs;
    private long latestLevel1EndEpochMs = -1L;
    private long firstLevel2StartEpochMs = -1L;
    private Path metricsDirectory;
    private Path runtimeEventsPath;
    private Path runContextPath;

    void init() {
        clearResultsDirectory();
        masStartEpochMs = System.currentTimeMillis();
        defineObsProperty("last_run_status", "idle");

        Properties config = loadConfiguration();
        pythonExecutable = readConfiguredPythonExecutable(config);
        selectedMode = readConfiguredMode(config);
        datasetId = readConfiguredDatasetId(config);

        defineObsProperty("selected_mode", selectedMode);
        defineObsProperty("dataset_id", datasetId);
        defineObsProperty("expected_mode_runs", selectedMode, countPythonDetectors(selectedMode));

        initializeMetricsLogging();
    }

    @OPERATION
    public void run_python(String scriptPath) {
        String normalizedPath = normalizeScriptPath(scriptPath);
        boolean isLevel2 = isLevel2Script(normalizedPath);
        String catalogueLevel = isLevel2 ? "level2" : "level1";
        String domainFamily = inferDomainFamily(normalizedPath);
        String phase = inferPhase(normalizedPath);
        long startEpochMs = System.currentTimeMillis();
        String scriptName = Paths.get(normalizedPath).getFileName().toString();

        try {
            File projectRoot = Paths.get("").toAbsolutePath().toFile();
            File scriptFile = new File(projectRoot, normalizedPath);

            if (isLevel2 && firstLevel2StartEpochMs < 0L) {
                firstLevel2StartEpochMs = startEpochMs;
            }

            if (!scriptFile.exists()) {
                appendRuntimeEvent(buildScriptEventJson(
                        "script_missing",
                        normalizedPath,
                        scriptName,
                        catalogueLevel,
                        domainFamily,
                        phase,
                        startEpochMs,
                        startEpochMs,
                        0L,
                        -1,
                        "missing"));
                failed("Python script not found: " + scriptFile.getAbsolutePath());
                return;
            }

            ObsProperty status = getObsProperty("last_run_status");
            status.updateValue("running");

            appendRuntimeEvent(buildScriptEventJson(
                    "script_started",
                    normalizedPath,
                    scriptName,
                    catalogueLevel,
                    domainFamily,
                    phase,
                    startEpochMs,
                    startEpochMs,
                    0L,
                    Integer.MIN_VALUE,
                    "running"));

            ProcessBuilder pb = new ProcessBuilder(pythonExecutable, scriptFile.getAbsolutePath());
            pb.directory(projectRoot);
            pb.redirectErrorStream(true);

            Process process = pb.start();

            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    log("[" + scriptFile.getName() + "] " + line);
                }
            }

            int exitCode = process.waitFor();
            long endEpochMs = System.currentTimeMillis();
            long durationMs = endEpochMs - startEpochMs;

            if (!isLevel2) {
                latestLevel1EndEpochMs = Math.max(latestLevel1EndEpochMs, endEpochMs);
            }

            if (exitCode == 0) {
                status.updateValue("success");
                appendRuntimeEvent(buildScriptEventJson(
                        "script_finished",
                        normalizedPath,
                        scriptName,
                        catalogueLevel,
                        domainFamily,
                        phase,
                        startEpochMs,
                        endEpochMs,
                        durationMs,
                        exitCode,
                        "success"));
                signal("python_finished", scriptPath, exitCode);
            } else {
                status.updateValue("failure");
                appendRuntimeEvent(buildScriptEventJson(
                        "script_finished",
                        normalizedPath,
                        scriptName,
                        catalogueLevel,
                        domainFamily,
                        phase,
                        startEpochMs,
                        endEpochMs,
                        durationMs,
                        exitCode,
                        "failure"));
                signal("python_failed", scriptPath, exitCode);
                failed("Python script failed with exit code " + exitCode);
            }

        } catch (Exception e) {
            getObsProperty("last_run_status").updateValue("failure");
            long errorEpochMs = System.currentTimeMillis();
            appendRuntimeEvent(buildScriptEventJson(
                    "script_error",
                    normalizedPath,
                    scriptName,
                    catalogueLevel,
                    domainFamily,
                    phase,
                    startEpochMs,
                    errorEpochMs,
                    errorEpochMs - startEpochMs,
                    -1,
                    "failure"));
            signal("python_failed", scriptPath, -1);
            failed("Error while executing Python script: " + e.getMessage());
        }
    }

    private String normalizeScriptPath(String scriptPath) {
        String trimmedPath = scriptPath == null ? "" : scriptPath.trim();

        if (trimmedPath.startsWith("python3 ")) {
            return trimmedPath.substring("python3 ".length()).trim();
        }

        if (trimmedPath.startsWith("python ")) {
            return trimmedPath.substring("python ".length()).trim();
        }

        return trimmedPath;
    }

    private boolean isLevel2Script(String normalizedPath) {
        String unixPath = normalizedPath.replace("\\", "/");
        return unixPath.contains("/level2/");
    }

    private String inferDomainFamily(String normalizedPath) {
        String unixPath = normalizedPath.replace("\\", "/");

        if (unixPath.contains("/structural/")) {
            return "structural";
        }
        if (unixPath.contains("/dynamic/")) {
            return "dynamic";
        }
        if (unixPath.contains("/functional/")) {
            return "functional";
        }
        if (unixPath.contains("/procedural/")) {
            return "procedural";
        }
        if (unixPath.contains("/level2/")) {
            return "level2";
        }

        return "unknown";
    }

    private String inferPhase(String normalizedPath) {
        String unixPath = normalizedPath.replace("\\", "/");

        if (unixPath.contains("/apriori/")) {
            return "apriori";
        }
        if (unixPath.contains("/aposteriori/")) {
            return "aposteriori";
        }

        return selectedMode != null ? selectedMode : "unknown";
    }

    private void clearResultsDirectory() {
        try {
            Path resultsDir = Paths.get("").toAbsolutePath().resolve("results").normalize();

            if (!Files.exists(resultsDir)) {
                Files.createDirectories(resultsDir);
                return;
            }

            Files.walk(resultsDir)
                    .sorted(Comparator.reverseOrder())
                    .filter(path -> !path.equals(resultsDir))
                    .forEach(this::deletePath);

            Files.createDirectories(resultsDir);
            log("[PythonExecArtifact] Cleared results directory: " + resultsDir);
        } catch (Exception e) {
            failed("Could not clear results directory: " + e.getMessage());
        }
    }

    private Properties loadConfiguration() {
        Path configPath = Paths.get("").toAbsolutePath().resolve("mas.properties");
        Properties properties = new Properties();

        if (!Files.exists(configPath)) {
            failed("MAS configuration file not found: " + configPath);
            return properties;
        }

        try (InputStream inputStream = Files.newInputStream(configPath)) {
            properties.load(inputStream);
        } catch (IOException e) {
            failed("Could not read MAS configuration file: " + e.getMessage());
            return properties;
        }

        return properties;
    }

    private String readConfiguredMode(Properties properties) {
        String configuredMode = properties.getProperty("mode", "").trim().toLowerCase(Locale.ROOT);

        if (!"apriori".equals(configuredMode) && !"aposteriori".equals(configuredMode)) {
            failed("Invalid mode in mas.properties. Expected 'apriori' or 'aposteriori', got: " + configuredMode);
            return "apriori";
        }

        log("[PythonExecArtifact] Selected mode from mas.properties: " + configuredMode);
        return configuredMode;
    }

    private String readConfiguredDatasetId(Properties properties) {
        String configuredDatasetId = properties.getProperty("dataset.id", "").trim();

        if (configuredDatasetId.isEmpty()) {
            log("[PythonExecArtifact] No dataset.id configured in mas.properties, using 'unspecified'.");
            return "unspecified";
        }

        log("[PythonExecArtifact] Selected dataset from mas.properties: " + configuredDatasetId);
        return configuredDatasetId;
    }

    private String readConfiguredPythonExecutable(Properties properties) {
        String configuredPython = properties.getProperty("python.path", "").trim();

        if (!configuredPython.isEmpty()) {
            Path pythonPath = Paths.get(configuredPython);

            if (Files.exists(pythonPath)) {
                log("[PythonExecArtifact] Using Python interpreter: " + configuredPython);
                return configuredPython;
            }

            log("[PythonExecArtifact] Configured python.path does not exist, trying fallbacks: " + configuredPython);
        }

        String fallback = findAvailablePythonExecutable();
        if (fallback != null) {
            log("[PythonExecArtifact] Using fallback Python interpreter: " + fallback);
            return fallback;
        }

        if (configuredPython.isEmpty()) {
            failed("Missing 'python.path' in mas.properties and no fallback interpreter was found.");
            return "python";
        }

        failed("Configured python.path does not exist and no fallback interpreter was found: " + configuredPython);
        return configuredPython;
    }

    private String findAvailablePythonExecutable() {
        String[] candidates = new String[] {
                "python",
                "python3",
                "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\CommonExtensions\\Microsoft\\VC\\SecurityIssueAnalysis\\python\\python.exe"
        };

        for (String candidate : candidates) {
            if (isRunnablePython(candidate)) {
                return candidate;
            }
        }

        return null;
    }

    private boolean isRunnablePython(String candidate) {
        try {
            Process process = new ProcessBuilder(candidate, "--version")
                    .redirectErrorStream(true)
                    .start();
            int exitCode = process.waitFor();
            return exitCode == 0;
        } catch (Exception e) {
            return false;
        }
    }

    private void initializeMetricsLogging() {
        try {
            metricsDirectory = Paths.get("").toAbsolutePath().resolve("results").resolve("metrics");
            Files.createDirectories(metricsDirectory);

            runtimeEventsPath = metricsDirectory.resolve("runtime_events.jsonl");
            runContextPath = metricsDirectory.resolve("run_context.json");

            Files.deleteIfExists(runtimeEventsPath);
            Files.writeString(
                    runContextPath,
                    buildRunContextJson(),
                    StandardOpenOption.CREATE,
                    StandardOpenOption.TRUNCATE_EXISTING
            );
            appendRuntimeEvent(buildMasStartEventJson());
        } catch (Exception e) {
            log("[PythonExecArtifact] Metrics logging initialization failed: " + e.getMessage());
        }
    }

    private void appendRuntimeEvent(String jsonLine) {
        if (runtimeEventsPath == null) {
            return;
        }

        try {
            Files.writeString(
                    runtimeEventsPath,
                    jsonLine + System.lineSeparator(),
                    StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND
            );
        } catch (IOException e) {
            log("[PythonExecArtifact] Could not append runtime event: " + e.getMessage());
        }
    }

    private String buildRunContextJson() {
        return "{\n"
                + "  \"dataset_id\": \"" + escapeJson(datasetId) + "\",\n"
                + "  \"mode\": \"" + escapeJson(selectedMode) + "\",\n"
                + "  \"python_executable\": \"" + escapeJson(pythonExecutable) + "\",\n"
                + "  \"mas_start_epoch_ms\": " + masStartEpochMs + ",\n"
                + "  \"expected_level1_runs\": " + countPythonDetectors(selectedMode) + ",\n"
                + "  \"git_commit\": \"" + escapeJson(readGitCommit()) + "\"\n"
                + "}\n";
    }

    private String buildMasStartEventJson() {
        return "{"
                + "\"event\":\"mas_started\","
                + "\"dataset_id\":\"" + escapeJson(datasetId) + "\","
                + "\"mode\":\"" + escapeJson(selectedMode) + "\","
                + "\"epoch_ms\":" + masStartEpochMs
                + "}";
    }

    private String buildScriptEventJson(
            String event,
            String scriptPath,
            String scriptName,
            String catalogueLevel,
            String domainFamily,
            String phase,
            long startEpochMs,
            long endEpochMs,
            long durationMs,
            int exitCode,
            String status
    ) {
        StringBuilder builder = new StringBuilder();
        builder.append("{");
        builder.append("\"event\":\"").append(escapeJson(event)).append("\",");
        builder.append("\"dataset_id\":\"").append(escapeJson(datasetId)).append("\",");
        builder.append("\"mode\":\"").append(escapeJson(selectedMode)).append("\",");
        builder.append("\"script_path\":\"").append(escapeJson(scriptPath)).append("\",");
        builder.append("\"script_name\":\"").append(escapeJson(scriptName)).append("\",");
        builder.append("\"catalogue_level\":\"").append(escapeJson(catalogueLevel)).append("\",");
        builder.append("\"domain_family\":\"").append(escapeJson(domainFamily)).append("\",");
        builder.append("\"phase\":\"").append(escapeJson(phase)).append("\",");
        builder.append("\"start_epoch_ms\":").append(startEpochMs).append(",");
        builder.append("\"end_epoch_ms\":").append(endEpochMs).append(",");
        builder.append("\"duration_ms\":").append(durationMs).append(",");
        builder.append("\"status\":\"").append(escapeJson(status)).append("\"");

        if (exitCode != Integer.MIN_VALUE) {
            builder.append(",\"exit_code\":").append(exitCode);
        }
        if (firstLevel2StartEpochMs >= 0L) {
            builder.append(",\"first_level2_start_epoch_ms\":").append(firstLevel2StartEpochMs);
        }
        if (latestLevel1EndEpochMs >= 0L) {
            builder.append(",\"latest_level1_end_epoch_ms\":").append(latestLevel1EndEpochMs);
        }
        builder.append("}");
        return builder.toString();
    }

    private String readGitCommit() {
        try {
            Process process = new ProcessBuilder("git", "rev-parse", "HEAD")
                    .directory(Paths.get("").toAbsolutePath().toFile())
                    .redirectErrorStream(true)
                    .start();

            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line = reader.readLine();
                int exitCode = process.waitFor();
                if (exitCode == 0 && line != null) {
                    return line.trim();
                }
            }
        } catch (Exception ignored) {
            // Best-effort metadata only.
        }

        return "";
    }

    private String escapeJson(String value) {
        if (value == null) {
            return "";
        }

        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\r", "\\r")
                .replace("\n", "\\n");
    }

    private int countPythonDetectors(String mode) {
        Path agentsRoot = Paths.get("").toAbsolutePath().resolve("src").resolve("agt");

        if (!Files.exists(agentsRoot)) {
            return 0;
        }

        try (Stream<Path> pathStream = Files.walk(agentsRoot)) {
            return (int) pathStream
                    .filter(Files::isRegularFile)
                    .filter(path -> path.toString().endsWith(".py"))
                    .filter(path -> path.toString().contains(File.separator + mode + File.separator))
                    .filter(path -> !path.toString().contains(File.separator + "level2" + File.separator))
                    .count();
        } catch (IOException e) {
            failed("Could not count detector scripts for mode '" + mode + "': " + e.getMessage());
            return 0;
        }
    }

    private void deletePath(Path path) {
        try {
            Files.deleteIfExists(path);
        } catch (IOException e) {
            throw new RuntimeException("Could not delete " + path + ": " + e.getMessage(), e);
        }
    }
}
