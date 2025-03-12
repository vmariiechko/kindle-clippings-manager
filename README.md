# kindle-clippings-manager
Manage 'My Clippings.txt' from Kindle, removing duplicates and enabling book-specific notes export.


## Run via CLI
1. Install dependencies:
    ```
    poetry install
    poetry shell
    ```
2. Place "My Clippings.txt" to repository root folder
3. Explore available CLI options
    ```
    python src/cli/main.py --help
    ```
4. From project root run CLI:
    ```
    python src/cli/main.py
    # or
    python src/cli/main.py -f bullet
    ```

### Tests
Run tests from repositories root directory:
```
poetry run pytest
```

# TODO later
- Add GUI + executable
- Update project README