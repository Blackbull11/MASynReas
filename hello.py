import sys

# Get the argument passed from Java/JaCaMo, default to "World" if none
name = sys.argv[1] if len(sys.argv) > 1 else "World"

# Print the output (this is what the Java Artifact will capture)
print(f"Hello {name}, this is Python speaking!")