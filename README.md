Hadrian's Brick
===============

A place where we collect public build logs of [Hadrian](https://github.com/snowleopard/hadrian),
and supply them to [Hadrian's Wall](https://github.com/izgzhen/hadrians-wall).

Get started
===========

To start contributing to this data repo, launch the GHC build with our provided script `main.py`:

1. (Recommanded) Use `virtualenv`
2. Add `export GITHUB_USERNAME=<your-username>` to your shell's rc file (and restart the shell or `source` it);
   another option is to use `GITHUB_USERNAME=<your-username> python main.py ...` each time
3. `python main.py --ghc_path=<ghc-source-path>`. Make sure you have `hadrian` inside `<ghc-source-path>`
4. After build ends, a `SUMMMARY` will be printed, and this summary will be appended to `logs/<your-username>.log`.
5. Create a commmit and push your change as a pull request to this repo.

NOTE: your build summary will be *public* to everyone
