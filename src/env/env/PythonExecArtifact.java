package env;

import cartago.Artifact;
import cartago.OPERATION;
import cartago.ObsProperty;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.Locale;
import java.util.Properties;
import java.util.stream.Stream;

public class PythonExecArtifact extends Artifact {
    private String pythonExecutable;

    void init() {
        clearResultsDirectory();
        defineObsProperty("last_run_status", "idle");
        Properties config = loadConfiguration();
        pythonExecutable = readConfiguredPythonExecutable(config);
        String selectedMode = readConfiguredMode(config);
        defineObsProperty("selected_mode", selectedMode);
        defineObsProperty("expected_mode_runs", selectedMode, countPythonDetectors(selectedMode));
    }

    @OPERATION
    public void run_python(String scriptPath) {
        try {
            File projectRoot = Paths.get("").toAbsolutePath().toFile();
            String normalizedPath = normalizeScriptPath(scriptPath);
            File scriptFile = new File(projectRoot, normalizedPath);

            if (!scriptFile.exists()) {
                failed("Python script not found: " + scriptFile.getAbsolutePath());
                return;
            }

            ObsProperty status = getObsProperty("last_run_status");
            status.updateValue("running");

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

            if (exitCode == 0) {
                status.updateValue("success");
                signal("python_finished", scriptPath, exitCode);
            } else {
                status.updateValue("failure");
                signal("python_failed", scriptPath, exitCode);
                failed("Python script failed with exit code " + exitCode);
            }

        } catch (Exception e) {
            getObsProperty("last_run_status").updateValue("failure");
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

    private String readConfiguredPythonExecutable(Properties properties) {
        String configuredPython = properties.getProperty("python.path", "").trim();

        if (configuredPython.isEmpty()) {
            failed("Missing 'python.path' in mas.properties.");
            return "python";
        }

        Path pythonPath = Paths.get(configuredPython);

        if (!Files.exists(pythonPath)) {
            failed("Configured python.path does not exist: " + configuredPython);
            return configuredPython;
        }

        log("[PythonExecArtifact] Using Python interpreter: " + configuredPython);
        return configuredPython;
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
