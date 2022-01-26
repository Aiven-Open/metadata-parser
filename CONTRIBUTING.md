# Welcome!

Contributions are very welcome on Aiven Metadata Parser. When contributing please keep this in mind:

- Open an issue to discuss new bigger features.
- Write code consistent with the project style and make sure the tests are passing.
- Stay in touch with us if we have follow up questions or requests for further changes.

# Development

More information about how the metadata parser is currently parsing the instances can be found in the [PARSING document](PARSING.md).

Guidelines for naming of nodes can be found in [GUIDELINES document](GUIDELINES.md).


## Manual testing

You can test the metadata parser by executing it over any Aiven project.
If you don't have a project with running services, you can create  them with the `create_services.sh` script as defined in the main [README](README.md).


# Opening a PR

- Commit messages should describe the changes, not the filenames. Win our admiration by following
  the [excellent advice from Chris Beams](https://chris.beams.io/posts/git-commit/) when composing
  commit messages.
- Choose a meaningful title for your pull request.
- The pull request description should focus on what changed and why.
- Check that the tests pass (and add test coverage for your changes if appropriate).
