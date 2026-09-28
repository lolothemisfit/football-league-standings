# Copilot Project Instructions

## Initial Project Prompt

I am completing a software engineering assessment. I want you to act as an AI development collaborator, not simply generate the entire solution for me.

First, analyze the assessment requirements below and help me plan the solution before we write implementation code.

### Requirements

* Build a production-ready command-line application that calculates a football league standing table.
* The solution may use Java, Python, Golang, C# (.NET Core on Linux), or Scala.
* Use the rules that applied to the English First Division in the 1974/75 season.
* Use the application to calculate the English First Division standings after week 10 of the 1974/75 season.
* Input and output SHOULD be CSV files.
* Input contains one game result per line.
* Output should be a conventional league standing table.
* Include the input and output files in the submission.
* Include automated tests.
* The application must be suitable for a Unix-like environment.
* Avoid committing installed package dependencies.
* Document any complicated setup.
* The assessment also evaluates AI collaboration.

### Initial Instructions

Do not implement the application yet.

Instead:

1. Identify the domain rules we need to research and verify.
2. Identify ambiguities in the requirements.
3. Propose a simple production-ready architecture.
4. Recommend how the CSV input/output should be structured.
5. Identify the core domain objects/functions we should probably have.
6. Propose a testing strategy.
7. Identify edge cases and validation requirements.
8. Suggest a sensible project structure.
9. Explain any assumptions that need to be verified before implementation.

Prefer a simple maintainable solution over unnecessary frameworks or abstractions.