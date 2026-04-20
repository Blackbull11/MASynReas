import cartago.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class PythonRunner extends Artifact {

    @OPERATION
    void runScript(String scriptName, String arg, OpFeedbackParam<String> result) {
        try {
            // Set up the process to call the python executable
            ProcessBuilder pb = new ProcessBuilder("python3", scriptName, arg);
            pb.redirectErrorStream(true); // Merge errors into standard output
            Process process = pb.start();

            // Read the output from the Python script
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }

            process.waitFor(); // Wait for the script to finish
            
            // Send the result back to the agent
            result.set(output.toString().trim());

        } catch (Exception e) {
            failed("Failed to execute Python script: " + e.getMessage());
        }
    }
}