MFrameTest Meta Testing Framework
=================================

MFrameTest is a tool for executing tests, storing results in a common form and
exporting the results to a third party source.

It is designed to be used either as part of day-to-day software creation, to
store the results of the latest build of a project or as part of an automated
build process where the output is stored in a common place separate from a CI
server.

MFrameTest is build in a modular fashion, with the testing infrastructure being
separated from the result storing infrastructure where possible. New testers
and printers can be added by adding classes to the `printers` and `testers`
directories where appropriate. All run-time configuration is loaded from a
single file (.ini format), `test.ini.sample` shows an example of this
configuration.

The latest development version of this software can be found at
`https://github.com/simonpcook/mframetest` along with the documentation for how
to extend the platform for new testing and output targets.
