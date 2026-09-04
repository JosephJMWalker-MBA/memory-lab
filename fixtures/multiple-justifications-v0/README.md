# Multiple-justification fixture

This fictional fixture tests alternative support paths for the same semantic
derived record.

At `SYN-DM-0300`, Project Aurora can be derived as blocked through either:

    J1 = Aurora depends_on Sigma AND Sigma status = blocked

or:

    J2 = Aurora depends_on Tau AND Tau status = blocked

The support semantics are therefore:

    J1 OR J2

At `SYN-DM-0301`, Sigma becomes clear. J1 fails, but J2 remains valid, so the
same Aurora-blocked record must remain active.

At `SYN-DM-0302`, Tau also becomes clear. Now both J1 and J2 fail, so the
historical Aurora-blocked record leaves the current view.

Neither transition justifies inventing `Aurora status = clear`.

This fixture follows the truth-maintenance distinction between conjunctive
antecedents inside one justification and alternative environments/support paths
across justifications.
