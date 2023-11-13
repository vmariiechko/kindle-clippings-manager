# kindle-clippings-manager
Manage 'My Clippings.txt' from Kindle, removing duplicates and enabling book-specific notes export.


### Run via CLI
1. Place "My Clippings.txt" to repository root folder
2. From project root run CLI with relative path to file:
    ```
    python src/cli/main.py "My Clippings.txt"
    ```

### Tests
Run tests from repositories root directory:
```
poetry run pytest
```

# TODO
- Cover case for "Bookmark" to have 2 empty lines