# kindle-clippings-manager
Manage 'My Clippings.txt' from Kindle, removing duplicates and enabling book-specific notes export.


### New script: run via CLI
1. Install dependencies:
    ```
    poetry install
    poetry shell
    ```
2. Go to [kindle clipping export tool](https://www.mykindletools.com/kindle-clipping-export) and export CSV file.
3. Move downloaded files to `./data/` directory
4. Replace the path to input file in the script.
5. Execute with active poetry venv:
    ```
    python src/cli/main_external_csv.py
    ```

### Old script: run via CLI
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

# TODO
- Add GUI + executable
- Update project README