# Code Formatting Rules

## Objective
To establish standard code formatting rules for all code repositories that are either original to or hard project forks by Hoyt Harness, including any development organizations he manages, e.g. Positronikal. These requirements apply to both local and online repositories, e.g. GitHub. The result should be that such repositories exist as standardized development environments readable by all. This policy adapts existing code rules and best practices for different programming languages and data structures while maintaining consistency across repositories.

### EXCEPTIONS:
These rules do not apply to contributing repositories that will instead adhere to the rules of their respective origins.

## Default Engineering Philosophy
Default philosophy for all software engineering projects, including contributing forks, follows the [Unix Philosphy](http://www.catb.org/esr/writings/taoup/html/ch01s06.html 'Basics of the Unix Philosphy') very closely.

### Primary Considerations
1. **Rule of Modularity:**
  - Write simple parts connected by clean interfaces.
2. **Rule of Clarity:**
  - Clarity is better than cleverness.
3. **Rule of Composition:**
  - Design programs to be connected to other programs.
4. **Rule of Separation:**
  - Separate policy from mechanism; separate interfaces from engines.
5. **Rule of Simplicity:**
  - Design for simplicity; add complexity only where you must.
6. **Rule of Parsimony:**
  - Write a big program only when it is clear by demonstration that nothing else will do.
7. **Rule of Transparency:**
  - Design for visibility to make inspection and debugging easier.
8. **Rule of Robustness:**
  - Robustness is the child of transparency and simplicity.
9. **Rule of Representation:**
  - Fold knowledge into data so program logic can be stupid and robust.
10. **Rule of Least Surprise:**
  - In interface design, always do the least surprising thing.
11. **Rule of Silence:**
  - When a program has nothing surprising to say, it should say nothing.
12. **Rule of Repair:**
  - When you must fail, fail noisily and as soon as possible.
13. **Rule of Economy:**
  - Programmer time is expensive; conserve it in preference to machine time.
14. **Rule of Generation:**
  - Avoid hand-hacking; write programs to write programs when you can.
15. **Rule of Optimization:**
  - Prototype before polishing. Get it working before you optimize it.
16. **Rule of Diversity:**
  - Distrust all claims for “one true way”.
17. **Rule of Extensibility:**
  - Design for the future, because it will be here sooner than you think.

## Language-specific Formatting
Formatting requirements, rules, or best practices specific to any coding language take priority in all source files. See the [ref/](./ref 'ref/') subdirectory in this repository.

### Formatting Resources for Selected Languages
- **AWK:**
  - [Gawk: Effective AWK Programming](https://www.gnu.org/software/gawk/manual/ 'Gawk: Effective AWK Programming')
  - Linters: `gawk --lint`
- **bash, C, C++:**
  - See [Default Formatting](#default-formatting 'Default Formatting') in this document.
  - Linters: [ShellCheck](https://www.shellcheck.net/ 'ShellCheck'), [Cppcheck](https://cppcheck.sourceforge.io/ 'Cppcheck'), [uncrustify](https://github.com/uncrustify/uncrustify 'uncrustify')
- **CSS, Go, HTML, JavaScript:**
  - [Google Style Guides](https://google.github.io/styleguide/ 'Google Style Guides')
  - Linters: [Stylelint](https://stylelint.io/ 'Stylelint'), [golangci-lint](https://github.com/golangci/golangci-lint 'golangci-lint'), [HTMLHint](https://htmlhint.com/ 'HTMLHint'), [HTML-validate](https://html-validate.org/ 'HTML-validate'), [eslint](https://eslint.org/ 'eslint')
- **Java:**
  - Default: [Java Code Conventions](https://www.oracle.com/docs/tech/java/codeconventions.pdf 'Java Code Conventions')
  - Specific to [Apache Maven](https://maven.apache.org/ 'Apache Maven Project') builds: [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html 'Google Java Style Guide')
  - Linters: [uncrustify](https://github.com/uncrustify/uncrustify 'uncrustify')
- **Perl:**
  - [Perl style guide](https://perldoc.perl.org/perlstyle 'perlstyle - Perl style guide')
  - Linters: [Perl-Critic](https://github.com/Perl-Critic/Perl-Critic 'Perl-Critic')
- **PHP:**
  - [PHP Style](https://doc.php.net/guide/style.md 'PHP Style')
  - [phplint](https://www.npmjs.com/package/phplint 'phplint') - Requires [Node.js](https://nodejs.org/en 'Node.js') and [npm](https://www.npmjs.com/ 'npm').
- **PowerShell 7:**
  - [PowerShell Language Specification](https://learn.microsoft.com/en-us/powershell/scripting/lang-spec/chapter-15?view=powershell-7.5 'PLS 3.0: Grammar')
  - Linters: [PSScriptAnalyzer](https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview?view=ps-modules 'PSScriptAnalyzer')
- **Python 3:**
  - [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/ 'PEP 8 – Style Guide for Python Code')
  - Linters: [Ruff](https://docs.astral.sh/ruff/ 'Ruff')

## Default Formatting
Default rules for source files are found in the [GNU Coding Standards](https://www.gnu.org/prep/standards/ 'GNU Coding Standards'). See the [ref/](./ref 'ref/') subdirectory in this repository.

### Primary Considerations
1. **Line Length:**
  - Keep lines of code to a maximum of 79 characters.
  - Longer lines should be broken into smaller, logically separated lines.
2. **Indentation:**
  - Use spaces for indentation, not tabs.
  - Indentation levels should clearly delineate code blocks and nested structures.
3. **Brace Placement:**
  - Braces `{}` should generally be placed on their own line.
  - Consider placing opening braces on the same line as the statement (e.g., `if`, `for`, `while`) only if it improves readability.
4. **Whitespace:**
  - Use whitespace to enhance readability, such as around operators and within code blocks.
  - Avoid trailing whitespace at the end of lines.
5. **Comments:**
  - Use comments to explain complex logic or non-obvious code sections.
  - Comments should be clear, concise, and consistent with the code they describe.
6. **Operator Precedence:**
  - Be mindful of operator precedence and avoid complex expressions with multiple operators at the same level of indentation.
7. **Line Breaks and Wrapping:**
  - When breaking long lines, ensure that the continuation lines are clearly indented and logically connected to the previous line.
  - Align continuation lines with the opening parenthesis of a function call or other structure.
8. **Naming Conventions:**
  - Follow consistent naming conventions for variables, functions, and other code elements.
  - Use descriptive and meaningful names to improve code readability.
9. **Avoid Tricky Expressions:**
  - Strive for clarity and simplicity in code, avoiding overly complex or obscure expressions.

