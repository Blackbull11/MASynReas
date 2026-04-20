package env;

import jason.asSyntax.StringTerm;
import jason.asSyntax.Structure;
import jason.environment.Environment;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.file.Paths;
import java.util.logging.Logger;

public class PythonExecEnvironment extends Environment {

    private final Logger logger = Logger.getLogger(PythonExecEnvironment.class.getName());

    @Override
    public boolean executeAction(String agName, Structure action) {
        try {
            if (action.getFunctor().equals("run_python") && action.getArity() == 1) {
                String scriptPath = ((StringTerm) action.getTerm(0)).getString();

                File projectRoot = Paths.get("").toAbsolutePath().toFile();
                File scriptFile = new File(projectRoot, scriptPath);

                ProcessBuilder pb = new ProcessBuilder("python", scriptFile.getPath());
                pb.directory(projectRoot);
                pb.redirectErrorStream(true);

                logger.info("[" + agName + "] Running Python script: " + scriptFile.getPath());

                Process process = pb.start();

                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        logger.info("[" + agName + "][python] " + line);
                    }
                }

                int exitCode = process.waitFor();
                logger.info("[" + agName + "] Python script finished with exit code " + exitCode);

                return exitCode == 0;
            }

            logger.warning("[" + agName + "] Unknown action: " + action);
            return false;

        } catch (Exception e) {
            logger.severe("[" + agName + "] Error while executing action " + action + ": " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
}