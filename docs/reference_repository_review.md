# Reference research software

The methodological reference for this project is
[Post-adsorption phage resistance in Escherichia](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance),
at [source revision a63bde3](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/tree/a63bde39b748b4fcc65b22a9e285ed0219676039).
It addresses a separate phage–host question. Its code, data and results are
not inputs to the present analysis.

The relevant software examples are its
[checksum-verified acquisition](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/scripts/01_fetch_and_validate_data.py),
[independent statistical checks](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/tests/test_statistics.py)
and [documented model limitations](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/docs/limitations.md).
They illustrate source verification, comparison with separate estimator
implementations and the importance of matching resampling assumptions to
biological dependence.

For this study, the corresponding definitions and evidence are in
[data provenance](data_provenance.md), [methods](methods.md),
[statistical validation](statistical_validation.md) and [limitations](limitations.md).
The source measurements come from Ritz and colleagues' experiment, and the
present comparisons use its own observational units, linkage criteria and
estimators. This software reference does not establish an independent
reproduction of either project's biological conclusions.
